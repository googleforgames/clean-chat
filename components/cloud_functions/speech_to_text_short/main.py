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

# ffmpeg -ss 56 -i toxic_behavior.mp3 -t 11 -ac 1 toxic_behavior1.flac

import os
import datetime,time
import re,json
from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud import speech


gcs_results_bucket = os.environ['gcs_results_bucket']


def gcp_storage_upload_string(source_string, bucket_name, blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(source_string)
    except Exception as e:
        print('[ ERROR ] Failed to upload to GCS. {}'.format(e))


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


def gcp_speech_to_text_short(gcs_uri):
    print(f'[ INFO ] Starting gcp_speech_to_text_short against {gcs_uri}')
    start_time = datetime.datetime.now()
    
    speech_client = speech.SpeechClient()
    
    audio  = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        #encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        #sample_rate_hertz=16000,
        #audio_channel_count=2,
        #enable_separate_recognition_per_channel=True,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )
    
    response = speech_client.recognize(config=config, audio=audio)
    
    text_blob_list = []
    for result in response.results:
        if result.alternatives[0].transcript not in text_blob_list:
            text_blob_list.append(result.alternatives[0].transcript)
        
        print("Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))
    
    text_blob = ' '.join(text_blob_list)
    runtime = (datetime.datetime.now() - start_time).seconds
    print('[ INFO ] Speech-to-Text Runtime: {} seconds'.format(runtime))
    print('[ INFO ] Text Blob: {}'.format(text_blob))
    
    return text_blob


def main(event,context):
    
    # Only process .flac files
    if re.search('\.flac$', event['name'].lower().strip()):
        
        gcs_uri = 'gs://{}/{}'.format(event['bucket'], event['name'])
        
        print('[ INFO ] Processing {}'.format(gcs_uri))
        text_blob = gcp_speech_to_text_short(gcs_uri)
        
        # Get audio file metadata (if it exists)
        metadata = gcp_storage_download_as_string(bucket_name=event['bucket'], blob_name=event['name'].lower().replace('.flac','.json'))
        
        # Construct Payload
        payload = json.loads(metadata)
        payload['text'] = text_blob
        payload['timestamp'] = payload['timestamp'] if 'timestamp' in payload else int(time.time())
        
        blob_name = f"{event['name'].replace('.flac','')}_{int(time.time())}.json"
        print(f'[ INFO ] Writing text blob {blob_name} to gs://{gcs_results_bucket}')
        gcp_storage_upload_string(source_string=json.dumps(payload), bucket_name=gcs_results_bucket, blob_name=blob_name)
