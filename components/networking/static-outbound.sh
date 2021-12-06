####################################################################
#
#   Set static outbound IP address for Callback URL
#   https://cloud.google.com/run/docs/configuring/static-outbound-ip
#   
####################################################################

gcloud compute networks list

gcloud compute networks subnets create antidote-subnet \
--range=10.124.0.0/20 --network=default --region=$TF_VAR_GCP_REGION

gcloud compute networks vpc-access connectors create antidote-vpc-connector \
  --region=$TF_VAR_GCP_REGION \
  --subnet-project=$TF_VAR_GCP_PROJECT_ID \
  --subnet=antidote-subnet

gcloud compute routers create antidote-router \
  --network=default \
  --region=$TF_VAR_GCP_REGION

gcloud compute addresses create antidote-static-ip --region=$TF_VAR_GCP_REGION

gcloud compute routers nats create antidote-nat-gateway \
  --router=antidote-router \
  --region=$TF_VAR_GCP_REGION \
  --nat-custom-subnet-ip-ranges=antidote-subnet \
  --nat-external-ip-pool=antidote-static-ip

# Then deploy cloud run (gcloud run deploy) with the following two parameters: 
#    --vpc-connector=antidote-vpc-connector \
#    --vpc-egress=all-traffic
