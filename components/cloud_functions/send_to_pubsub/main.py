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
import json
import time
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
        def pubsub_callback( message_future ):
            # When timeout is unspecified, the exception method waits indefinitely.
            if message_future.exception(timeout=30):
                print('[ ERROR ] Publishing message on {} threw an Exception {}.'.format(topic_name, message_future.exception()))
            else:
                print('[ INFO ] Result: {}'.format(message_future.result()))
        
        # Initialize PubSub Path
        pubsub_topic_path = pubsub_publisher.topic_path( project_id, pubsub_topic )
        
        # If message is JSON, then dump to json string
        if type( message ) is dict:
            message = json.dumps( message )
        
        if type(message) is not bytes:
            message = message.encode('utf-8')
        
        # When you publish a message, the client returns a Future.
        message_future = pubsub_publisher.publish(pubsub_topic_path, data=message )
        message_future.add_done_callback( pubsub_callback )
    except Exception as e:
        print('[ EXCEPTION ] {}'.format(e))


def parse_sentence_lightweight(text):
    import re
    sentences = re.split('\. |\? |\! ', text)
    sentences = [sent for sent in sentences if sent!=None and len(sent)>=3]
    return sentences


def parse_sentence_nltk(text):
    import nltk
    nltk.download('punkt')
    sentences = nltk.tokenize.sent_tokenize(text)
    sentences = [sent for sent in sentences if sent!=None and len(sent)>=3]
    return sentences


def main(event,context):
    
    # Parse input event parameters
    filename = event['name']
    
    # Initialize PubSub Object
    pubsub_publisher = pubsub_v1.PublisherClient()
    
    # Generate Google Cloud Storage uri
    gcs_uri = 'gs://{}/{}'.format(event['bucket'], event['name'])
    
    print('[ INFO ] Processing {}'.format(gcs_uri))
    gcs_payload = gcp_storage_download_as_string(event['bucket'], event['name'])
    
    # Get and enrich payload to send to PubSub
    payload = json.loads(gcs_payload)
    '''
    payload = {
        "userid":    "myusername",
        "timestamp": int(time.time()), # unix timestamp
        "text":      "my text message"
    }
    '''
    if 'timestamp' not in payload:
        payload['timestamp'] = int(time.time())
    
    # Split text into sentences prior to sending to scoring engine
    original_text = payload['text']
    sentences     = parse_sentence_lightweight(original_text)
    
    for sentence in sentences:
        sentence_payload = payload
        sentence_payload['text'] = sentence
        
        # Write message payload to PubSub
        pubsub_publish( pubsub_publisher, project_id=gcp_project_id, pubsub_topic=pubsub_topic, message=sentence_payload )
