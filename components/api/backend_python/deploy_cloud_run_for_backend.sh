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

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Deploy to Cloud Run
gcloud run deploy $TF_VAR_APP_CLOUD_RUN_NAME \
    --project=$TF_VAR_GCP_PROJECT_ID \
    --source "$SCRIPT_DIR" \
    --region $TF_VAR_APP_CLOUD_RUN_REGION \
    --cpu 1 \
    --memory 512M \
    --min-instances 0 \
    --max-instances 5 \
    --concurrency 80 \
    --platform managed \
    --set-env-vars TF_VAR_GCP_PROJECT_ID=${TF_VAR_GCP_PROJECT_ID} \
    --set-env-vars TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT} \
    --set-env-vars TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG} \
    --set-env-vars TF_VAR_GCS_BUCKET_TEXT_DROPZONE=${TF_VAR_GCS_BUCKET_TEXT_DROPZONE} \
    --set-env-vars TF_VAR_PUBSUB_TOPIC_TEXT_INPUT=${TF_VAR_PUBSUB_TOPIC_TEXT_INPUT} \
    --timeout 30 \
    --service-account "${TF_VAR_APP_CLOUD_RUN_NAME}-sa@${TF_VAR_GCP_PROJECT_ID}.iam.gserviceaccount.com" \
    --no-allow-unauthenticated
