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

import os,sys
import json
import time
import argparse
import discord # discord.py==1.7.3
import random
from google.cloud import pubsub_v1 # google-cloud-pubsub==2.7.0

if len(sys.argv)<=1:
    print('\nUsage Example:\npython3 discord_client.py --gcp_project_id $GCP_PROJECT_ID --pubsub_topic_id $PUBSUB_TOPIC_ID --discord_token $DISCORD_TOKEN\n')

def write_to_pubsub(publisher_client, project_id, topic_id, json_payload):
    try:
        topic_path = publisher_client.topic_path(project_id, topic_id)
        
        data = json.dumps(json_payload).encode('utf-8')
        
        future = publisher_client.publish(topic_path, data)
        print(future.result())
        print(f'[ INFO ] Published message to {topic_path}.')
    except Exception as e:
        print(f'[ EXCEPTION ] {e}')

if __name__ == "__main__":
    
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument('--gcp_project_id',  type=str, help='Google Cloud Project ID',              required=True)
    parser.add_argument('--pubsub_topic_id', type=str, help='Google PubSub Topic ID for text input',required=True)
    parser.add_argument('--discord_token',   type=str, help='Discord Bot Token',                    required=True)
    args = parser.parse_args()
    
    # Initialize PubSub Client
    publisher_client = pubsub_v1.PublisherClient()
    
    # Initialize Discord
    discord_token  = args.discord_token
    discord_client = discord.Client()
    
    @discord_client.event
    async def on_ready():
        print(f'[ INFO ] Logged in as {discord_client.user}')
    
    @discord_client.event
    async def on_message(message):
        
        #Don't monitor or respond to ourselves
        #if message.author == discord_client.user:
        #    return None
        
        if message.content == 'hi all':
                payload = {
                    #'id': message.id,
                    'userid': message.author.name,
                    #'discriminator': message.author.discriminator,
                    'text': message.content,
                    'timestamp': time.mktime(message.created_at.timetuple()), # unix timestamp
                }
                
                write_to_pubsub(publisher_client, args.gcp_project_id, args.pubsub_topic_id, payload)                
                print(f'[ MESSAGE ] {json.dumps(payload,indent=4)}')
                
                responses = [
                    "I can't believe you took my weapon",
                    'i hate playing with you',
                    "you play like shit. What's your address, I'm going to come find you.",
                    "you are terrible!!"
                ]
                for i in range(len(responses)):
                    time.sleep(random.random()*8)
                    await message.channel.send(responses[i])
                    
                    payload = {
                        #'id': message.id,
                        'userid': discord_client.user.name,
                        #'discriminator': message.author.discriminator,
                        'text': responses[i],
                        'timestamp': time.mktime(message.created_at.timetuple()), # unix timestamp
                    }
                    
                    write_to_pubsub(publisher_client, args.gcp_project_id, args.pubsub_topic_id, payload)
                    print(f'[ MESSAGE ] {json.dumps(payload,indent=4)}')
        else:
            if message.author != discord_client.user:
                pass
    
    discord_client.run(discord_token)
