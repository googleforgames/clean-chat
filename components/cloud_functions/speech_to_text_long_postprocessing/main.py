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

import os
import datetime,time
import re,json
from google.cloud import storage
from google.cloud.storage.blob import Blob


gcs_audio_long_bucket = os.environ['gcs_audio_long_bucket']
gcs_results_bucket    = os.environ['gcs_results_bucket']


def gcp_storage_upload_string(source_string, bucket_name, blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(source_string)
    except Exception as e:
        print(f'[ ERROR ] Failed to upload to GCS. {e}')


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


def main(event,context):
    print(f'[ INFO ] Event: {event}')
    
    try:    
        # Get Results from GCS
        blob = gcp_storage_download_as_string(event['bucket'], event['name'])
        blob = json.loads(blob)
        
        # Iterate over text payload and regroup the text blob.
        text_blob_list = []
        start_time = '0s'
        for result in blob['results']:
            if result['alternatives'][0]['transcript'] not in text_blob_list:
                text_blob_list.append({'text': result['alternatives'][0]['transcript'], 'start_time': start_time, 'end_time': result['resultEndTime'] })
                # Update start_time for next iteration
                start_time = result['resultEndTime']
        
        print(f'[ INFO ] Text Results: {text_blob_list}')
        
        # Get request metdata
        metadata = gcp_storage_download_as_string(gcs_audio_long_bucket, event['name'])
        metadata = json.loads(metadata)
        # Update metdata to include the text results.
        metadata['text'] = text_blob_list
        
        print(f'[ INFO ] Saving text results to GCS bucket {gcs_results_bucket}')
        gcp_storage_upload_string(json.dumps(metadata), gcs_results_bucket, event['name'])
        
        return '200'
    except Exception as e:
        print(f"[ EXCEPTION ] At main, gs://{event['bucket']}/{event['name']}. {e}")
        return '400'
