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
echo "Testing /audio"
curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    -H "Content-Type: application/json" \
    -d '{"audio_uri":"https://storage.googleapis.com/lofty-proton-329718-tmp/%28ok%29%20this%20is%20why%20I%20dont%20use%20my%20mic%20cause%20there%20are%20sexist%20pigs%20like%20you.mp3?x-goog-signature=33f3abf72853df4821082c54e445535b129e56894bb6a6befb1c246cf4b68ddf85e225194da85bfb7ea3686cd8e6b56103cfe6a0e4c5167477c7bc94c1d67771dd352f83499840b1f0ba0b46f7ff35796de6591118f645a14997b7112cafb683aa94c3e77191f84a063a6bf2f678dc87e2dde8d1c9e520de5c3d2a6aef275030e231aa661ece7f06238ee1dd8451c6846c68eb5f83afbfaec4d0ac61650cc999762df9715fd7fa88139ee7a12ecaf53ab23906e628f069ad1cf086fe9a86f7ba4696d703754362b11729e76059fe50a5c5591b47e0d2b54f21ae2640652dccde55f125e1cb76cdd28ef3695a69f98baee81b18e676f08880bad90065e2a515b9&x-goog-algorithm=GOOG4-RSA-SHA256&x-goog-credential=sa-signedurl%40lofty-proton-329718.iam.gserviceaccount.com%2F20211104%2Fus%2Fstorage%2Fgoog4_request&x-goog-date=20211104T161257Z&x-goog-expires=600&x-goog-signedheaders=host", "username": "danz", "label":"test batch 1"}' \
    $CLOUD_RUN_URL/audio 
echo ""

