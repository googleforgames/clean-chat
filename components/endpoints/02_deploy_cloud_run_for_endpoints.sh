# Load Configs
#. ../../../config.default

# Deploy placeholder/temporary app for Cloud Run Endpoints container
gcloud run deploy $TF_VAR_ENDPOINTS_CLOUD_RUN_NAME \
    --image="gcr.io/cloudrun/hello" \
    --region $TF_VAR_ENDPOINTS_CLOUD_RUN_REGION \
    --allow-unauthenticated \
    --platform managed \
    --project=$TF_VAR_GCP_PROJECT_ID