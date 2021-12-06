# Load Config
#. "${TF_VAR_CURRENT_DIR}/config.default"

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Enable necessary GCP services
#gcloud services enable run.googleapis.com

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
    --timeout 30 \
    --vpc-connector=antidote-vpc-connector \
    --vpc-egress=all-traffic

#Testing from Cloud Shell - load random audio file
#curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" "https://audio-input-cyj7y6zvsq-ue.a.run.app/audio" \
#   -H "Content-Type: application/json" \
#   -d '{"audio_uri":"https://github.com/zaratsian/speech-to-text-container/raw/main/samples/otherguys_clip1.mp3","key_value1":"my sample value"}'