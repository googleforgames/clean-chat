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

# Set Script Directory
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Get Cloud Run URL and Hostname
ENDPOINTS_CLOUD_RUN_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_ENDPOINTS_CLOUD_RUN_NAME")
ENDPOINTS_CLOUD_RUN_HOSTNAME="${ENDPOINTS_CLOUD_RUN_URL//https:\/\//}"
BACKEND_APP_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_APP_CLOUD_RUN_NAME")
echo "ENDPOINTS_CLOUD_RUN_URL:       $ENDPOINTS_CLOUD_RUN_URL"
echo "ENDPOINTS_CLOUD_RUN_HOSTNAME:  $ENDPOINTS_CLOUD_RUN_HOSTNAME"
echo "BACKEND_APP_URL:               $BACKEND_APP_URL"

# Dynamically update openapi-run.yaml with the Cloud Run Hostname and URL
cp "$SCRIPT_DIR/openapi-run.yaml.example" "$SCRIPT_DIR/openapi-run.yaml"
sed -i "s@BACKEND_APP_URL@$BACKEND_APP_URL@" "$SCRIPT_DIR/openapi-run.yaml"
sed -i "s@ENDPOINTS_CLOUD_RUN_HOSTNAME@$ENDPOINTS_CLOUD_RUN_HOSTNAME@" "$SCRIPT_DIR/openapi-run.yaml"

# Deploy Google Endpoints Service
gcloud endpoints services deploy "$SCRIPT_DIR/openapi-run.yaml" \
    --project $TF_VAR_GCP_PROJECT_ID

# Cleanup file - remove openapi-run.yaml
rm openapi-run.yaml
