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

FROM apache/beam_python3.7_sdk:2.25.0

ENV TF_VAR_GCP_PROJECT_ID ""
ENV TF_VAR_DATAFLOW_REGION ""
ENV TF_VAR_GCS_BUCKET_DATAFLOW ""
ENV TF_VAR_PUBSUB_TOPIC_TEXT_INPUT ""
ENV TF_VAR_PUBSUB_TOPIC_TEXT_SCORED ""
ENV TF_VAR_PUBSUB_TOPIC_TOXIC ""
ENV TF_VAR_BIGQUERY_DATASET ""
ENV TF_VAR_BIGQUERY_TABLE ""
ENV TF_VAR_WINDOW_DURATION_SECONDS ""
ENV TF_VAR_WINDOW_SLIDING_SECONDS ""
ENV TF_VAR_DATAFLOW_RUNNER ""
ENV TF_VAR_TOXIC_USER_THRESHOLD ""
ENV TF_VAR_MODEL_API_KEY ""

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt 
RUN python3 setup.py sdist
RUN pip3 install ./dist/scoring_logic-0.1.tar.gz

ENTRYPOINT python3 main.py \
		--gcp_project ${TF_VAR_GCP_PROJECT_ID} \
		--region ${TF_VAR_DATAFLOW_REGION} \
		--job_name 'scoring-engine' \
		--gcp_staging_location "gs://${TF_VAR_GCS_BUCKET_DATAFLOW}/staging" \
		--gcp_tmp_location "gs://${TF_VAR_GCS_BUCKET_DATAFLOW}/tmp" \
		--batch_size 10 \
		--pubsub_topic_text_input projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TEXT_INPUT} \
		--pubsub_topic_text_scored projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TEXT_SCORED} \
		--pubsub_topic_toxic projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TOXIC} \
		--bq_dataset_name ${TF_VAR_BIGQUERY_DATASET} \
		--bq_table_name ${TF_VAR_BIGQUERY_TABLE} \
		--window_duration_seconds ${TF_VAR_WINDOW_DURATION_SECONDS} \
		--window_sliding_seconds ${TF_VAR_WINDOW_SLIDING_SECONDS} \
		--runner ${TF_VAR_DATAFLOW_RUNNER} \
		#--no_use_public_ips \
		#--subnetwork "regions/${TF_VAR_DATAFLOW_REGION}/subnetworks/dataflow-subnet" \
		--extra_package ./dist/scoring_logic-0.1.tar.gz \
		--toxic_user_threshold ${TF_VAR_TOXIC_USER_THRESHOLD} \
		--model_api_key ${TF_VAR_MODEL_API_KEY}
