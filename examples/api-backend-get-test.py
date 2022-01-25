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
Example call to API Backend - /test
'''

import os
import sys
import subprocess
import urllib

import google.auth.transport.requests
import google.oauth2.id_token

try:
    cloud_run_name = os.environ['TF_VAR_APP_CLOUD_RUN_NAME']
except:
    print('Could not find TF_VAR_APP_CLOUD_RUN_NAME environment variable.')
    sys.exit()

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

def make_authorized_request(service_url):
    try:
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, service_url)
        
        req = urllib.request.Request(service_url)
        req.add_header("Authorization", f"Bearer {id_token}")
        response = urllib.request.urlopen(req)
        
        return response
    except Exception as e:
        print(f'Exception: {e}')
        sys.exit()

def main():
    
    # Set IAM Policy Binding
    # This grants the email/member to invoke the Cloud Run service
    member_email = get_active_authenticated_member_email()
    set_iam_policy_binding(member_email, cloud_run_name)
    
    # Get Cloud Run URL
    cloud_run_url = get_cloud_run_url(cloud_run_name)
    
    if cloud_run_url != '':
        
        service_url = f'{cloud_run_url}/test'
        
        print(f'Executing GET request for {service_url}')
        response = make_authorized_request(service_url)
        
        print(f'{response.status}, {response.read()}')


if __name__ == "__main__":
    main()
