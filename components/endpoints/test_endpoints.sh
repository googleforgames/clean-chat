# Load Configs
#. ../../../config.default"

# Get Cloud Run URL and Hostname
CLOUD_RUN_URL=$(gcloud run services list --format "value(status.url)" --filter "metadata.name=$TF_VAR_ENDPOINTS_CLOUD_RUN_NAME")
echo ""
echo "[ INFO ] Testing against base URL: $CLOUD_RUN_URL"
echo ""

# CURL to Cloud Run Endpoint (GET)
echo "Testing /test"
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" $CLOUD_RUN_URL/test
echo ""

# CURL to Cloud Run Endpoint (POST)
echo "Testing /chat"
curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    -H "Content-Type: application/json" \
    -d '{"text":"This is a test chat message.", "username": "testuser123", "var1":12345}' \
    $CLOUD_RUN_URL/chat 
echo ""

# CURL to Cloud Run Endpoint (POST)
echo "Testing /audio"
curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    -H "Content-Type: application/json" \
    -d '{"audio_uri":"https://github.com/zaratsian/Datasets/raw/master/test_audio.wav", "username": "testuser123", "var1":12345}' \
    $CLOUD_RUN_URL/audio 
echo ""

