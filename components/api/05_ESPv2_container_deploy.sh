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

# Set Container Repo Tag (based on previous ESPv2_container_build step)
CONTAINER_REPO_TAG=$(gcloud container images list-tags gcr.io/$TF_VAR_GCP_PROJECT_ID/endpoints-runtime-serverless --format "value(tags)" | grep $TF_VAR_ENDPOINTS_CLOUD_RUN_NAME | head -1)

echo "[ INFO ] CONTAINER_REPO_TAG:       $CONTAINER_REPO_TAG"
echo "[ INFO ] Using this Docker Image:  gcr.io/$TF_VAR_GCP_PROJECT_ID/endpoints-runtime-serverless:$CONTAINER_REPO_TAG"

gcloud run deploy $TF_VAR_ENDPOINTS_CLOUD_RUN_NAME \
    --image="gcr.io/$TF_VAR_GCP_PROJECT_ID/endpoints-runtime-serverless:$CONTAINER_REPO_TAG" \
    --region $TF_VAR_ENDPOINTS_CLOUD_RUN_REGION \
    --allow-unauthenticated \
    --concurrency 80 \
    --cpu 1 \
    --memory 256M \
    --max-instances 3 \
    --min-instances 0 \
    --platform managed \
    --project=$TF_VAR_GCP_PROJECT_ID
