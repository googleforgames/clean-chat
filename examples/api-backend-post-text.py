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

'''
Example call to API Backend - /text
'''

import os
import sys
import subprocess
import json
import urllib3
urllib3.disable_warnings()

import google.auth.transport.requests
import google.oauth2.id_token
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

project_id      = os.environ.get('TF_VAR_GCP_PROJECT_ID', '')
cloud_run_name  = os.environ.get('TF_VAR_APP_CLOUD_RUN_NAME', '')
subscription_id = f'''{os.environ.get('TF_VAR_PUBSUB_TOPIC_TEXT_SCORED', '')}-sub-pull'''
timeout         = 30.0

def get_cloud_run_url(cloud_run_name):
    try:
        p = subprocess.Popen(["gcloud", "run", "services", "describe", cloud_run_name, "--platform", "managed", "--region", "us-central1", "--format", "value(status.url)"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        
        if stdout != b'':
            return stdout.decode('utf-8').replace('\n','')
        else:
            msg = f'Cloud Run URL not found. {stderr}'
            print(msg)
            return ''
    except Exception as e:
        print(f'Exception: {e}')
        sys.exit()

def get_active_authenticated_member_email():
    try:
        p = subprocess.Popen(["gcloud", "config", "list", "account", "--format", "value(core.account)"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout != b'':
            return stdout.decode('utf-8').replace('\n','')
        else:
            msg = f'Active authenticated member email not found. {stderr}'
            print(msg)
            return ''
    except Exception as e:
        print(f'Exception: {e}')
        return ''

def set_iam_policy_binding(member_email, cloud_run_name, gcp_region='us-central1'):
    try:
        member = f"user:{member_email}"
        p = subprocess.Popen(["gcloud", "run", "services", "add-iam-policy-binding", cloud_run_name, "--member", member, "--role", "roles/run.invoker", "--region", gcp_region], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout != b'':
            print('IAM policy binding updated')
            return stdout.decode('utf-8').replace('\n','')
        else:
            msg = f'{stderr}'
            print(msg)
            return ''
    except Exception as e:
        print(f'Exception: {e}')
        return ''

def make_authorized_request(service_url, post_json):
    try:
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, service_url)
        
        http = urllib3.PoolManager()
        
        r = http.request('POST',
            service_url,
            body=json.dumps(post_json),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {id_token}"}
        )
        
        return r
    except Exception as e:
        print(f'Exception: {e}')
        sys.exit()

def pubsub_subscriber(project_id, subscription_id):
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    
    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Scored Message: {message.data}")
        message.ack()
    
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"\nListening for messages on {subscription_path}..\n")
    
    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
            #pass

def main():
    
    # Demo/Example JSON Payload for Text Chat
    if len(sys.argv) >= 2:
        payload ={
            'text':     f'{sys.argv[1]}',
            'userid':   'user123'
        }
    else:
        payload ={
            'text':     'Test text message',
            'userid':   'user123'
        }
    
    # Set IAM Policy Binding
    # This grants the email/member to invoke the Cloud Run service
    member_email = get_active_authenticated_member_email()
    set_iam_policy_binding(member_email, cloud_run_name)
    
    # Get Cloud Run URL
    cloud_run_url = get_cloud_run_url(cloud_run_name)
    
    # Test the API Call to the deployed Backend service running on Cloud Run
    if cloud_run_url != '':
        
        service_url = f'{cloud_run_url}/text'
        
        print(f'Executing POST request for {service_url}')
        print(f'POST Payload:\n{json.dumps(payload,indent=4)}\n')
        response = make_authorized_request(service_url, payload)
        
        print(f'{response.status}, {response.read()}')
        
        # Start PubSub Subscriber to listen for scored message response.
        pubsub_subscriber(project_id, subscription_id)


if __name__ == "__main__":
    main()
