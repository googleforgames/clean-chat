SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Deploy to Cloud Run
gcloud run deploy $TF_VAR_APP_CLOUD_RUN_NAME \
    --project=$TF_VAR_GCP_PROJECT_ID \
    --source "$SCRIPT_DIR" \
    --allow-unauthenticated \
    --region $TF_VAR_APP_CLOUD_RUN_REGION \
    --concurrency 80 \
    --cpu 1 \
    --memory 256M \
    --max-instances 3 \
    --min-instances 0 \
    --platform managed \
    --set-env-vars TF_VAR_GCP_PROJECT_ID=${TF_VAR_GCP_PROJECT_ID} \
    --set-env-vars TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT} \
    --set-env-vars TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG} \
    --set-env-vars TF_VAR_GCS_BUCKET_TEXT_DROPZONE=${TF_VAR_GCS_BUCKET_TEXT_DROPZONE} \
    --set-env-vars TF_VAR_PUBSUB_TOPIC_TEXT_INPUT=${TF_VAR_PUBSUB_TOPIC_TEXT_INPUT} \
    --timeout 30
