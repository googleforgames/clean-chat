# Copyright 2022 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Google Cloud Dataflow
# References:
# https://cloud.google.com/dataflow/docs/

import os
import logging
import time
import argparse
import json
import apache_beam as beam
from apache_beam import window
from apache_beam.transforms import trigger
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.options.pipeline_options import SetupOptions
from scoring_logic import scoring_logic

class ToxicityPipeline(object):
    '''Dataflow Pipeline and Supporting Methods for Aggregating Toxicity Scores'''
    def __init__(self, **kwargs):
        self.bq_schema = {'fields': [
            {'name': 'username',       'type': 'STRING',  'mode': 'NULLABLE'},
            {'name': 'timestamp',      'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'text',           'type': 'STRING',  'mode': 'NULLABLE'},
            {'name': 'score',          'type': 'FLOAT64', 'mode': 'NULLABLE'}
        ]}
    
    def parse_pubsub(self, event):
        json_payload = json.loads(event)
        
        # If payload does not contain timestamp, then generate unix timestamp.
        if 'timestamp' not in json_payload:
            json_payload['timestamp'] = int(time.time())
        
        return json_payload
    
    def preprocess_event(self, event):
        return ((event['username']), event)
    
    def bq_preprocessing(self, event):
        bq_payload = {
            'timestamp': event['timestamp'],
            'username':  event['username'],
            'text':      event['text'],
            'score':     event['score'],
        }
        return bq_payload
    
    def avg_by_group(self, tuple):
        print(f'[ DEBUG ] avg_by_group tuple = {tuple}')
        (k,v) = tuple
        return {"username":k, "score": sum([record['score'] for record in v])/len(v)} 
    
    def convert_to_bytestring(self, event):
        try:
            bytestr = json.dumps(event).encode('utf-8')
            return bytestr
        except Exception as e:
            print('[ EXCEPTION ] Could not convert to bytestring. {}'.format(e))
    
    def is_toxic(self, event, toxic_usernames):
        
        send_toxic_signal = False
        
        if event['username'] not in toxic_usernames:    
            if event['score'] >= float(toxic_user_threshold):
                send_toxic_signal = True
                toxic_usernames.add(event['username'])
        else:
            if event['score'] < float(toxic_user_threshold):
                toxic_usernames.remove(event['username'])
        
        return send_toxic_signal
    
    def score_event(self, event):
        '''
        event = {
            'username':  'user123',
            'timestamp': '20210804 11:22:46.222708',
            'text':      'my chat message'
        }
        '''
        score_payload = scoring_logic.model(event['text'], perspective_apikey)
        event['score']        = score_payload['score']
        event['score_detail'] = score_payload
        return event
    
    def run_pipeline(self, known_args, pipeline_args):
        
        pipeline_options = PipelineOptions(pipeline_args)
        pipeline_options.view_as(SetupOptions).save_main_session = True
        pipeline_options.view_as(StandardOptions).streaming = True
        
        ###################################################################
        #   DataFlow Pipeline
        ###################################################################
        
        with beam.Pipeline(options=pipeline_options) as p:
            
            toxic_usernames = set()
            
            # Text Ingest Topic
            pubsub_topic_ingest_stream = known_args.pubsub_topic_text_input
            logging.info(f'Ready to process events from PubSub topic: {pubsub_topic_ingest_stream}') 
            raw_events = ( 
                    p  | 'raw events' >> beam.io.ReadFromPubSub( pubsub_topic_ingest_stream )
            )
            
            # Parse events
            parsed_events = (
                raw_events  | 'parsed events' >> beam.Map(self.parse_pubsub)
                            | 'set_timestamp' >> beam.Map(lambda x: window.TimestampedValue(x, x['timestamp']))
            )
            
            # Print results to console (for testing/debugging)
            #parsed_events | 'print parsed_events' >> beam.Map(print)
            
            score_events = (
                parsed_events   | 'score events' >> beam.Map(self.score_event)
            )
            
            # Print results to console (for testing/debugging)
            score_events | 'print score_events' >> beam.Map(print)
            
            # Tranform events
            events_window = (
                parsed_events   | 'window_preprocessing' >> beam.Map(self.preprocess_event)
                                | 'windowing' >> beam.WindowInto(window.SlidingWindows(known_args.window_duration_seconds, known_args.window_sliding_seconds)) # Default window is 30 seconds in length, and a new window begins every 5 seconds
                                | 'window_grouping' >> beam.GroupByKey()
                                | 'window_aggregation' >> beam.Map(self.avg_by_group)
            )
            
            # Apply Game Studio Business Logic
            flag_user = (
                events_window   | 'flag user' >> beam.Filter(self.is_toxic, toxic_usernames=toxic_usernames)
            )
            
            # Print results to console (for testing/debugging)
            flag_user | 'print flag_user' >> beam.Map(print)
            
            # Write flagged/toxic users to PubSub Topic
            (
            flag_user   | 'convert toxic msg'    >> beam.Map(self.convert_to_bytestring)
                        | 'write to toxic topic' >> beam.io.WriteToPubSub(known_args.pubsub_topic_toxic)
            )
            
            # Write scored events to PubSub (where it can be pushed to a designed endpoint URL)
            (
            score_events | 'convert scored msg'    >> beam.Map(self.convert_to_bytestring)
                        | 'write to scored topic' >> beam.io.WriteToPubSub(known_args.pubsub_topic_text_scored)
            )
            
            # Write all events into BigQuery (for analysis and model retraining)
            (
            score_events |  beam.Map(self.bq_preprocessing)
                        |  'scored_events to bq' >> beam.io.gcp.bigquery.WriteToBigQuery(
                            table=known_args.bq_table_name,
                            dataset=known_args.bq_dataset_name,
                            project=known_args.gcp_project,
                            schema=self.bq_schema,
                            batch_size=int(known_args.batch_size)
                            )
            )


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gcp_project',             required=True,  default='gaming-demos',       help='GCP Project ID')
    parser.add_argument('--region',                  required=True,  default='us-central1',        help='GCP Region')
    parser.add_argument('--job_name',                required=True,  default='dataflow-job-z1',    help='Dataflow Job Name')
    parser.add_argument('--gcp_staging_location',    required=True,  default='gs://xxxxx/staging', help='Dataflow Staging GCS location')
    parser.add_argument('--gcp_tmp_location',        required=True,  default='gs://xxxxx/tmp',     help='Dataflow tmp GCS location')
    parser.add_argument('--batch_size',              required=True,  default=10, type=int,         help='Dataflow Batch Size')
    parser.add_argument('--pubsub_topic_text_input', required=True,  default='',                   help='Text Input PubSub Topic: projects/<project_id>/topics/<topic_name>')
    parser.add_argument('--pubsub_topic_text_scored',required=True,  default='',                   help='PubSub Topic containing scores for each individual text string passed through Dataflow. projects/<project_id>/topics/<topic_name>')
    parser.add_argument('--pubsub_topic_toxic',      required=True,  default='',                   help='Output PubSub Topic for flagged/toxic user: projects/<project_id>/topics/<topic_name>')
    parser.add_argument('--bq_dataset_name',         required=True,  default='',                   help='Output BigQuery Dataset')
    parser.add_argument('--bq_table_name',           required=True,  default='',                   help='Output BigQuery Table')
    parser.add_argument('--window_duration_seconds', required=True,  default=30, type=int,         help='Dataflow window duration (in seconds)')
    parser.add_argument('--window_sliding_seconds',  required=True,  default=5,  type=int,         help='Dataflow window sliding interval (in seconds)')
    parser.add_argument('--runner',                  required=True,  default='DirectRunner',       help='Dataflow Runner - DataflowRunner or DirectRunner (local)')
    parser.add_argument('--extra_package',           required=True,  default='scoring_logic-0.1.tar.gz', help='Local python dependency that contains the scoring logic and ML model')
    parser.add_argument('--toxic_user_threshold',    required=True,  default=0.60, type=float,     help='Toxic threshold on a scale of 0-1. Anything over this threshold will be flagged as toxic.')
    parser.add_argument('--perspective_apikey',      required=False, default='',                   help='Perspective API key. Generated via GCP Credentials')
    known_args, pipeline_args = parser.parse_known_args()
    
    # Set GOOGLE_CLOUD_PROJECT environ variable
    if known_args.gcp_project is None:
        print("Variable 'gcp_project' not set")
        sys.exit()
    else:
        os.environ['GOOGLE_CLOUD_PROJECT']=known_args.gcp_project
    
    # Set toxic user threshold value
    toxic_user_threshold = known_args.toxic_user_threshold
    perspective_apikey = known_args.perspective_apikey
    
    pipeline_args.extend([
        '--runner={}'.format(known_args.runner),                          # DataflowRunner or DirectRunner (local)
        '--project={}'.format(known_args.gcp_project),
        '--region={}'.format(known_args.region),
        '--staging_location={}'.format(known_args.gcp_staging_location),  # Google Cloud Storage gs:// path
        '--temp_location={}'.format(known_args.gcp_tmp_location),         # Google Cloud Storage gs:// path
        '--job_name=' + str(known_args.job_name),
        '--extra_package=' + str(known_args.extra_package),
    ])
    
    logging.basicConfig(level=logging.INFO)
    
    # Instantiate Beam Pipeline
    ToxPipeline = ToxicityPipeline()
    # Run Pipeline
    ToxPipeline.run_pipeline(known_args, pipeline_args)

