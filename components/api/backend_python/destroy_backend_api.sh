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

# Get Running Cloud Run Service
RUNNING_CLOUD_RUN_SERVICE=$(gcloud run services list --format='value(metadata.name)' --filter metadata.name="${TF_VAR_APP_CLOUD_RUN_NAME}")

if [[ $TF_VAR_APP_CLOUD_RUN_NAME ]] && [[ $RUNNING_CLOUD_RUN_SERVICE == ${TF_VAR_APP_CLOUD_RUN_NAME} ]]
then
    echo "Shutting down $TF_VAR_APP_CLOUD_RUN_NAME Cloud Run service in 3 seconds."
    sleep 3
    gcloud run services delete ${TF_VAR_APP_CLOUD_RUN_NAME} --region ${TF_VAR_APP_CLOUD_RUN_REGION} --no-async
else
    echo "[ WARNING ] TF_VAR_APP_CLOUD_RUN_NAME variable not set or serivice is not running."
fi
