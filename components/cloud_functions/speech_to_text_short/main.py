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
from google.cloud import speech
from google.cloud import translate

gcp_project_id               = os.environ['gcp_project_id']
gcs_results_bucket           = os.environ['gcs_results_bucket']
enable_alternative_languages = os.environ['enable_alternative_languages'] # "true" or "false"

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



def translate_detect_language(text):
    """Detects the text's language."""
    translate_client = translate.Client()
    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)
    return result["language"]


def translate_text(gcp_project_id, text, source_language_code='es-ES', target_language_code='en-US'):
    translate_client = translate.TranslationServiceClient()
    
    location = "global"
    
    parent = f"projects/{gcp_project_id}/locations/{location}"
    
    # Translate text from English to French
    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = translate_client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": source_language_code,
            "target_language_code": target_language_code,
        }
    )
    
    # Display the translation for each input text provided
    translated_text_str = ''
    for translation in response.translations:
        translated_text_str = translated_text_str + ' ' + translation.translated_text
    
    return translated_text_str.strip()


def gcp_speech_to_text_short(gcs_uri, enable_alternative_languages='false'):
    print(f'[ INFO ] Starting gcp_speech_to_text_short against {gcs_uri}')
    start_time = datetime.datetime.now()
    
    speech_client = speech.SpeechClient()
    
    audio  = speech.RecognitionAudio(uri=gcs_uri)
    
    if enable_alternative_languages.lower() == 'true':
        print(f'[ INFO ] Detecting non-english language')
        config = speech.RecognitionConfig(
            #encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            #sample_rate_hertz=16000,
            #audio_channel_count=2,
            #enable_separate_recognition_per_channel=True,
            language_code="en-US",
            alternative_language_codes=["es-ES","pt-BR","zh-TW"],
            enable_automatic_punctuation=True,
        )
    else:
        print(f'[ INFO ] Not running language detection. Assuming source language is en-US')
        config = speech.RecognitionConfig(
            #encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            #sample_rate_hertz=16000,
            #audio_channel_count=2,
            #enable_separate_recognition_per_channel=True,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
    
    response = speech_client.recognize(config=config, audio=audio)
    
    text_blob = []
    for result in response.results:
        if result.alternatives[0].transcript not in text_blob:
            text_blob.append(result.alternatives[0].transcript)
    
    runtime = (datetime.datetime.now() - start_time).seconds
    print('[ INFO ] Speech-to-Text Runtime: {} seconds'.format(runtime))
    
    text_blob = ' '.join(text_blob)
    print(f'[ INFO ] Original Text: {text_blob}')
    
    # Detect language
    try:
        detected_language = response.results[0].language_code
    except:
        detected_language = 'en-us'
    
    print(f'[ INFO ] Detected language: {detected_language}')
    
    # Translate text if in non-english language, and flag is set, enable_alternative_languages == 'true'
    if enable_alternative_languages.lower() == 'true' and detected_language.lower() != 'en-us':
        print(f'[ INFO ] Translating non-english language')
        text_blob_translated = translate_text(gcp_project_id, text_blob, source_language_code=detected_language, target_language_code='en-US')
    else:
        text_blob_translated = text_blob
    
    print(f'[ INFO ] Translated Text: {text_blob_translated}')
    
    # Generate payload
    text_blob_list = [{'text': text_blob_translated, 'start_time': '0s', 'end_time': '59s'}]
    return text_blob_list, detected_language


def main(event,context):
    
    # Only process .flac files
    if re.search('\.flac$', event['name'].lower().strip()):
        
        gcs_uri = f"gs://{event['bucket']}/{event['name']}"
        
        print(f'[ INFO ] Processing {gcs_uri}')
        text_blob_list, detected_language = gcp_speech_to_text_short(gcs_uri, enable_alternative_languages)
        
        # Get audio file metadata (if it exists)
        metadata = gcp_storage_download_as_string(bucket_name=event['bucket'], blob_name=event['name'].lower().replace('.flac','.json'))
        
        # Construct Payload
        payload = json.loads(metadata)
        payload['text']      = text_blob_list
        payload['timestamp'] = payload['timestamp'] if 'timestamp' in payload else int(time.time())
        
        blob_name = f"{event['name'].replace('.flac','')}_{int(time.time())}.json"
        print(f'[ INFO ] Writing text blob {blob_name} to gs://{gcs_results_bucket}')
        gcp_storage_upload_string(source_string=json.dumps(payload), bucket_name=gcs_results_bucket, blob_name=blob_name)
