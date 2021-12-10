# Deploy placeholder/temporary app for Cloud Run Endpoints container
gcloud run deploy $TF_VAR_ENDPOINTS_CLOUD_RUN_NAME \
    --image="gcr.io/cloudrun/hello" \
    --project=$TF_VAR_GCP_PROJECT_ID \
    --region $TF_VAR_ENDPOINTS_CLOUD_RUN_REGION \
    --allow-unauthenticated \
    --concurrency 80 \
    --cpu 1 \
    --memory 256M \
    --max-instances 3 \
    --min-instances 0 \
    --platform managed \
    --timeout 30