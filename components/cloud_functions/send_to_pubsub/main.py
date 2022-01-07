################################################################################################################
#
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################################################

import os
import json
import datetime,time
from google.cloud import storage
from google.cloud import pubsub_v1


gcp_project_id = os.environ['gcp_project_id']
pubsub_topic   = os.environ['pubsub_topic']


def gcp_storage_download_as_string(bucket_name, blob_name):
    '''
        Downloads a blob from the bucket, and outputs as a string.
    '''
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob_content = blob.download_as_string()
        
        return blob_content
    
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))


def pubsub_publish( pubsub_publisher, project_id, pubsub_topic, message ):
    '''
        Pub/Sub Publish Message
        Notes:
          - When using JSON over REST, message data must be base64-encoded
          - Messages must be smaller than 10MB (after decoding)
          - The message payload must not be empty
          - Attributes can also be added to the publisher payload
        
        pubsub_publisher  = pubsub_v1.PublisherClient()
    '''
    try:
        # Initialize PubSub Path
        pubsub_topic_path = pubsub_publisher.topic_path( project_id, pubsub_topic )
        
        # If message is JSON, then dump to json string
        if type( message ) is dict:
            message = json.dumps( message )
        
        # When you publish a message, the client returns a Future.
        #message_future = pubsub_publisher.publish(pubsub_topic_path, data=message.encode('utf-8'), attribute1='myattr1', anotherattr='myattr2')
        message_future = pubsub_publisher.publish(pubsub_topic_path, data=message.encode('utf-8') )
        message_future.add_done_callback( pubsub_callback )
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))


def main(event,context):
    
    filename = event['name']
    #username = filename.replace('.txt','')
    
    gcs_uri = 'gs://{}/{}'.format(event['bucket'], event['name'])
    
    print('[ INFO ] Processing {}'.format(gcs_uri))
    gcs_payload = gcp_storage_download_as_string(event['bucket'], event['name'])
    
    # Get and enrich payload to send to PubSub
    payload = json.loads(gcs_payload)
    if 'timestamp' not in payload:
        payload['timestamp'] = int(time.time())
    
    '''
    payload = {
        "username": username,
        "timestamp": int(time.time()), # unix timestamp
        "text": f'{text_blob}'
     }
    '''
    
    # Initialize PubSub Object
    pubsub_publisher  = pubsub_v1.PublisherClient()
    
    # Write message payload to PubSub
    pubsub_publish( pubsub_publisher, project_id=gcp_project_id, pubsub_topic=pubsub_topic, message=payload )

