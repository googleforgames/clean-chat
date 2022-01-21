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
CLOUD_RUN_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_ENDPOINTS_CLOUD_RUN_NAME")
CLOUD_RUN_HOSTNAME="${CLOUD_RUN_URL//https:\/\//}"
ENDPOINTS_CONFIG_ID=$(gcloud endpoints services list --format "value(serviceConfig.id)" --filter "serviceName=$CLOUD_RUN_HOSTNAME")

echo "[ INFO ] PROJECT_ID:          $TF_VAR_GCP_PROJECT_ID"
echo "[ INFO ] CLOUD_RUN_HOSTNAME:  $CLOUD_RUN_HOSTNAME"
echo "[ INFO ] ENDPOINTS_CONFIG_ID: $ENDPOINTS_CONFIG_ID"

# Download Build Script
# https://cloud.google.com/endpoints/docs/openapi/get-started-cloud-run#configure_esp
wget https://raw.githubusercontent.com/GoogleCloudPlatform/esp-v2/master/docker/serverless/gcloud_build_image -O "${SCRIPT_DIR}/gcloud_build_image"
chmod +x "${SCRIPT_DIR}/gcloud_build_image"

# Build ESPv2 Container Image
"${SCRIPT_DIR}/gcloud_build_image" -s $CLOUD_RUN_HOSTNAME -c $ENDPOINTS_CONFIG_ID -p $TF_VAR_GCP_PROJECT_ID

# Cleanup / Remove gcloud_build_image file
rm "${SCRIPT_DIR}/gcloud_build_image"
