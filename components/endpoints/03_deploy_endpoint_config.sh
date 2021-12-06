# Load Configs
#. ../../../config.default

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Get Cloud Run URL and Hostname
ENDPOINTS_CLOUD_RUN_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_ENDPOINTS_CLOUD_RUN_NAME")
ENDPOINTS_CLOUD_RUN_HOSTNAME="${ENDPOINTS_CLOUD_RUN_URL//https:\/\//}"
BACKEND_APP_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_APP_CLOUD_RUN_NAME")
echo "ENDPOINTS_CLOUD_RUN_URL:       $ENDPOINTS_CLOUD_RUN_URL"
echo "ENDPOINTS_CLOUD_RUN_HOSTNAME:  $ENDPOINTS_CLOUD_RUN_HOSTNAME"
echo "BACKEND_APP_URL:               $BACKEND_APP_URL"

# Dynamically update openapi-run.yaml with the Cloud Run Hostname and URL
cp "$SCRIPT_DIR/openapi-run.yaml.example" "$SCRIPT_DIR/openapi-run.yaml"
sed -i "s@BACKEND_APP_URL@$BACKEND_APP_URL@" "$SCRIPT_DIR/openapi-run.yaml"
sed -i "s@ENDPOINTS_CLOUD_RUN_HOSTNAME@$ENDPOINTS_CLOUD_RUN_HOSTNAME@" "$SCRIPT_DIR/openapi-run.yaml"

# Deploy Google Endpoints Service
gcloud endpoints services deploy "$SCRIPT_DIR/openapi-run.yaml" \
    --project $TF_VAR_GCP_PROJECT_ID

# Cleanup file - remove openapi-run.yaml
#rm openapi-run.yaml
