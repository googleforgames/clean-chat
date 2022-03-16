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
from google.cloud import speech_v1p1beta1 as speech

gcs_results_stt = os.environ['gcs_results_stt']

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


def gcp_speech_to_text_long(gcs_uri, gcs_object_name):
    print(f'[ INFO ] Starting gcp_speech_to_text_long against {gcs_uri}')
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
    
    output_transcription_name = re.sub('.flac$','.json', gcs_object_name)
    
    output_config = speech.TranscriptOutputConfig(gcs_uri=f"gs://{gcs_results_stt}/{output_transcription_name}")
    request       = speech.LongRunningRecognizeRequest(config=config, audio=audio, output_config=output_config)
    operation     = speech_client.long_running_recognize(request=request)
    print(f'[ INFO ] Operation: {operation.metadata}')
    print(f'[ INFO ] Operation: {operation.result}')
    
    return True


def main(event,context):
    
    # Only process .flac files
    if re.search('\.flac$', event['name'].lower().strip()):
        gcs_uri = 'gs://{}/{}'.format(event['bucket'], event['name'])
        
        print('[ INFO ] Processing {}'.format(gcs_uri))
        text_blob = gcp_speech_to_text_long(gcs_uri, gcs_object_name=event['name'])
        
        return '200'
