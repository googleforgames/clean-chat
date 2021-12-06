FROM apache/beam_python3.7_sdk:2.25.0

WORKDIR /app

COPY main.py requirements.txt dist/scoring_logic-0.1.tar.gz ./

RUN pip3 install -r requirements.txt 
RUN pip3 install scoring_logic-0.1.tar.gz

ENTRYPOINT python3 ./main.py \
	--gcp_project ${GCP_PROJECT_ID} \
	--region ${DATAFLOW_REGION} \
	--job_name 'antidote-scoring-engine' \
	--gcp_staging_location "gs://${DATAFLOW_GCS_BUCKET}/staging" \
	--gcp_tmp_location "gs://${DATAFLOW_GCS_BUCKET}/tmp" \
	--batch_size 10 \
	--pubsub_topic_text_input projects/${GCP_PROJECT_ID}/topics/${PUBSUB_TOPIC_TEXT_INPUT} \
	--pubsub_topic_text_scored projects/${GCP_PROJECT_ID}/topics/${PUBSUB_TOPIC_TEXT_SCORED} \
    --pubsub_topic_toxic projects/${GCP_PROJECT_ID}/topics/${PUBSUB_TOPIC_TOXIC} \
	--bq_dataset_name ${BIGQUERY_DATASET} \
	--bq_table_name ${BIGQUERY_TABLE} \
	--window_duration_seconds ${WINDOW_DURATION_SECONDS} \
	--window_sliding_seconds ${WINDOW_SLIDING_SECONDS} \
	--runner ${DATAFLOW_RUNNER} \
    --extra_package scoring_logic-0.1.tar.gz \
    --toxic_user_threshold ${TF_VAR_TOXIC_USER_THRESHOLD} \
    --perspective_apikey ${TF_VAR_PERSPECTIVE_API_KEY}