# Load Configs
#. ../../config

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Get Cloud Run URL and Hostname
CLOUD_RUN_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_ENDPOINTS_CLOUD_RUN_NAME")
CLOUD_RUN_HOSTNAME="${CLOUD_RUN_URL//https:\/\//}"
ENDPOINTS_CONFIG_ID=$(gcloud endpoints services list --format "value(serviceConfig.id)" --filter "serviceName=$CLOUD_RUN_HOSTNAME")

echo "[ INFO ] PROJECT_ID:          $TF_VAR_GCP_PROJECT_ID"
echo "[ INFO ] CLOUD_RUN_HOSTNAME:  $CLOUD_RUN_HOSTNAME"
echo "[ INFO ] ENDPOINTS_CONFIG_ID: $ENDPOINTS_CONFIG_ID"

# Download Build Script
# https://cloud.google.com/endpoints/docs/openapi/get-started-cloud-run#configure_esp
wget https://raw.githubusercontent.com/GoogleCloudPlatform/esp-v2/master/docker/serverless/gcloud_build_image -O "${SCRIPT_DIR}/gcloud_build_image"
chmod +x "${SCRIPT_DIR}/gcloud_build_image"

# Build ESPv2 Container Image
"${SCRIPT_DIR}/gcloud_build_image" -s $CLOUD_RUN_HOSTNAME -c $ENDPOINTS_CONFIG_ID -p $TF_VAR_GCP_PROJECT_ID
