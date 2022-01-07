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
import time
import requests
import re
import json
import io
import subprocess
import base64
import audioread
from flask import Flask, request
from google.cloud import storage
from google.cloud.storage.blob import Blob
from google.cloud import speech
from google.cloud import pubsub_v1

app = Flask(__name__)

project_id             = os.environ['TF_VAR_GCP_PROJECT_ID']
gcs_bucket_audio_short = os.environ['TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT']
gcs_bucket_audio_long  = os.environ['TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG']
gcs_bucket_text        = os.environ['TF_VAR_GCS_BUCKET_TEXT_DROPZONE']
pubsub_topic           = os.environ['TF_VAR_PUBSUB_TOPIC_TEXT_INPUT']

# Ensure that ENV variables do not have extra quotes
project_id             = project_id.replace('"','')
gcs_bucket_audio_short = gcs_bucket_audio_short.replace('"','')
gcs_bucket_audio_long  = gcs_bucket_audio_long.replace('"','')
gcs_bucket_text        = gcs_bucket_text.replace('"','')
pubsub_topic           = pubsub_topic.replace('"','')

# Initialize Clients
speech_client    = speech.SpeechClient()
pubsub_publisher = pubsub_v1.PublisherClient()

def gcp_storage_upload_string(source_string, bucket_name, blob_name):
    print(f'[ DEBUG ] gcp_storage_upload_string received {bucket_name} and {blob_name}')
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(source_string)
        print(f'[ INFO ] Uploaded {blob_name} as string to GCS bucket {bucket_name}')
    except Exception as e:
        print(f'[ ERROR ] gcp_storage_upload_string.Failed to upload to GCS. {e}')

def gcp_storage_upload_filename(filename, bucket_name, blob_name):
    print(f'[ DEBUG ] gcp_storage_upload_string received {bucket_name} and {blob_name}')
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(filename)
        print(f'[ INFO ] Uploaded file {blob_name} to GCS bucket {bucket_name}')
    except Exception as e:
        print(f'[ ERROR ] gcp_storage_upload_filename. Failed to upload to GCS. {e}')

def speech_to_text_short(gcs_uri):
    '''
    Google Cloud Speech-to-Text (short audio)
    '''
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        #encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        #sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )
    
    response = speech_client.recognize(config=config, audio=audio)
    
    sentences = []
    for result in response.results:
        sentences.append(result.alternatives[0].transcript)
    
    return sentences

def pubsub_callback( message_future ):
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print('[ ERROR ] Publishing message on {} threw an Exception {}.'.format(topic_name, message_future.exception()))
    else:
        print('[ INFO ] Result: {}'.format(message_future.result()))

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
        print(f'[ DEBUG ] Pubsub message_future.result(): {message_future.result()}')
    except Exception as e:
        print('[ ERROR ] {}'.format(e))

def download_online_file(response, saved_filename):
    '''
    "response" comes from requests.get or request.post response
    '''
    if response.status_code == 200:
        print(f'[ INFO ] Saving {response.url} as {saved_filename}')
        with open(saved_filename, 'wb') as f:
            #f.write(response.content)
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
    
    return None

def get_audio_duration(audio_file):
    try:
        with audioread.audio_open(audio_file) as f:
            audio_file_duration_in_secs = f.duration
            print(f'[ INFO ] Audio file duration: {audio_file_duration_in_secs} seconds')
            return audio_file_duration_in_secs
    except Exception as e:
        print(f'[ EXCEPTION ] At get_audio_duration. {e}')
        return None

def generate_filename(url):
    try:
        # Lowcase
        url = url.lower()
        # Extract filename from URL
        filename = re.search('[a-zA-Z0-9\-\_\ \(\)]+\.(wav|mp3|flac)', url).group()
        # Cleanup URL
        filename = re.sub('[^a-zA-Z0-9\.]','_',filename)
        # Remove leading character(s) if not a letter
        filename = re.sub('^[^a-zA-Z]+','', filename)
    except Exception as e:
        print(f'[ EXCEPTION ] At generate_filename. {e}')
        filename = f'noid_{int(time.time())}.mp3'
    
    print(f'[ DEBUG ] generate_filename = {filename}')
    return filename


@app.route("/audio", methods = ['POST'])
def audio():
    if request.method == 'POST':
        try:
            '''# Payload should look like this
            {
                'timestamp': 1639163163,
                'username':  'user123',
                'audio_uri': 'https://mypath/audio.wav',
            }
            '''
            payload   = request.get_json()
            audio_uri = payload['audio_uri']
            print(f'''[ INFO ] User-provided payload: {payload}''')
            
            print(f'[ INFO ] /audio requesting audio file from {audio_uri}')
            response = requests.get(audio_uri)
            print(f'[ INFO ] Requested audio file. Status code: {response.status_code}')
            
            if response.status_code == 200:
                
                audio_filename = generate_filename(audio_uri)
                
                # Write audio to GCS so that STT can be ran against this file.
                if True: # re.search('\.mp3$',audio_filename):
                    # Save audio file
                    download_online_file(response=response, saved_filename=audio_filename)
                    
                    # Get Audio file length
                    audio_file_duration_in_secs = get_audio_duration(audio_file=audio_filename)
                    
                    if audio_file_duration_in_secs < 60:
                        bucket_name = gcs_bucket_audio_short
                    else:
                        bucket_name = gcs_bucket_audio_long
                    
                    print(f"[ INFO ] bucket_name:  {bucket_name}")
                    
                    # Upload raw (initial) audio file
                    print(f'[ INFO ] Processing audio file called  {audio_filename}')
                    gcp_storage_upload_string(response.content, bucket_name=bucket_name, blob_name=audio_filename)
                    # Convert mp3 to flac
                    audio_filename_flac = re.sub('\.[a-z0-9]+$','.flac',audio_filename.lower())
                    print(f'[ INFO ] Running {audio_filename} through FFMPEG to generate {audio_filename_flac}')
                    subprocess.call(['ffmpeg', '-i', audio_filename, '-ac', '1', audio_filename_flac])
                    print(f'[ INFO ] Uploading processed audio file {audio_filename_flac} (as flac) to gs://{bucket_name}')
                    gcp_storage_upload_filename(filename=audio_filename_flac, bucket_name=bucket_name, blob_name=audio_filename_flac)
                    
                    # GCS Path
                    gcs_uri = f'gs://{bucket_name}/{audio_filename_flac}'
                    
                    # Write audio payload/metadata to GCS
                    audio_payload_filename = re.sub('\.[a-z0-9]+$', '.json', audio_filename)
                    print(f'[ INFO ] Writing {audio_payload_filename} to GCS')
                    gcp_storage_upload_string(json.dumps(payload), bucket_name=bucket_name, blob_name=audio_payload_filename)
                    
                    # Return Status
                    if audio_file_duration_in_secs < 60:
                        #sentences = speech_to_text_short(gcs_uri=gcs_uri)
                        #transcript = ' '.join(sentences)
                        msg = f'''{audio_uri} has been processed.'''                        
                        print(f'''[ INFO ] {msg}''')
                        return msg, 201
                    else:
                        #speech_to_text_long(gcs_uri=gcs_uri)
                        msg = f'''{audio_uri} is being process as a long audio file.'''
                        print(f'''[ INFO ] {msg}''')
                        return msg, 201
            else:
                msg = f'''Failed to get {audio_uri}. Status Code: {response.status_code}. {response.content}'''
                print(f'''[ ERROR ] {msg}''')
                return msg, response.status_code
        except Exception as e:
            print(f'[ EXCEPTION ] At /audio. {e}')
            return '', 401


@app.route("/chat", methods = ['POST'])
def chat():
    if request.method == 'POST':
        try:
            '''# Payload should look like this
            {
                'timestamp': 1639163163,
                'username':  'user123',
                'text':      'test text message',
            }
            '''
            payload = request.get_json()
            print(f'''[ INFO ] User-provided payload: {payload}''')
            
            # Write to the text dropzone in GCS
            bucket_name = gcs_bucket_text
            payload_filename = f"{payload['username'].lower()}_{int(time.time())}.json"
            gcp_storage_upload_string(json.dumps(payload), bucket_name=bucket_name, blob_name=payload_filename)
            
            # Publish to PubSub
            #print(f'''[ INFO ] Publishing payload to PubSub Topic: {pubsub_topic}''')
            #pubsub_publish( pubsub_publisher, project_id=project_id, pubsub_topic=pubsub_topic, message=payload )
            return 'Success', 201
        except Exception as e:
            print(f'[ EXCEPTION ] At /chat. {e}')
            return '', 401


@app.route("/test", methods = ['GET'])
def test():
    return f'Hello!', 200


@app.route("/antidote_callback", methods = ['POST'])
def antidote_callback():
    if request.method == 'POST':
        try:
            print('[ INFO ] Starting Antidote Callback')
            payload = request.get_json()
            print(f'[ INFO ] antidote_callback payload: {payload}')
            
            payload_decoded = json.loads(base64.b64decode(payload['message']['data']).decode('utf-8'))
            callback_url = payload_decoded['callback_url']
            r = requests.post(callback_url, json=payload_decoded)
            print(f'[ INFO ] Status code from callback_url: {r.status_code}')
            return 'Success', 201
        except Exception as e:
            print(f'[ EXCEPTION ] At /antidote_callback. {e}')
            return 'Bad Request', 401


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
