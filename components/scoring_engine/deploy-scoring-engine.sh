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

##########################################################################
#
# The script will build and deploy a docker container that runs
# a Dataflow (Apache Beam) job on Google Dataflow using the DataflowRunner.
#
##########################################################################

# Remove/clean any existing container
docker rmi -f scoring_engine
docker rm -f $(docker ps -a -f name=scoring_engine -q)

# Load Config
. ./config || . ../../config

echo "GCP_PROJECT_ID: $TF_VAR_GCP_PROJECT_ID"

# Build scoring engine container
docker build --tag scoring_engine . 

# Deploy (interactive mode with DirectRunner)
docker run -it --name scoring_engine \
--env TF_VAR_GCP_PROJECT_ID=$TF_VAR_GCP_PROJECT_ID \
--env TF_VAR_DATAFLOW_REGION=$TF_VAR_DATAFLOW_REGION \
--env TF_VAR_GCS_BUCKET_DATAFLOW=$TF_VAR_GCS_BUCKET_DATAFLOW \
--env TF_VAR_PUBSUB_TOPIC_TEXT_INPUT=$TF_VAR_PUBSUB_TOPIC_TEXT_INPUT \
--env TF_VAR_PUBSUB_TOPIC_TEXT_SCORED=$TF_VAR_PUBSUB_TOPIC_TEXT_SCORED \
--env TF_VAR_PUBSUB_TOPIC_TOXIC=$TF_VAR_PUBSUB_TOPIC_TOXIC \
--env TF_VAR_BIGQUERY_DATASET=$TF_VAR_BIGQUERY_DATASET \
--env TF_VAR_BIGQUERY_TABLE=$TF_VAR_BIGQUERY_TABLE \
--env TF_VAR_WINDOW_DURATION_SECONDS=$TF_VAR_WINDOW_DURATION_SECONDS \
--env TF_VAR_WINDOW_SLIDING_SECONDS=$TF_VAR_WINDOW_SLIDING_SECONDS \
--env TF_VAR_DATAFLOW_RUNNER=$TF_VAR_DATAFLOW_RUNNER \
--env TF_VAR_TOXIC_USER_THRESHOLD=$TF_VAR_TOXIC_USER_THRESHOLD \
--env TF_VAR_PERSPECTIVE_API_KEY=$TF_VAR_PERSPECTIVE_API_KEY \
scoring_engine
