GCP_PROJECT_ID='gaming-demos'


# Create GCP PubSub Topics
gcloud pubsub topics create antidote-toxicity
gcloud pubsub topics create antidote-griefing
gcloud pubsub topics create antidote-cheat
gcloud pubsub topics create antidote-score

# Create GCP PubSub Subscriptions
gcloud pubsub subscriptions create antidote-toxicity-sub --topic antidote-toxicity
gcloud pubsub subscriptions create antidote-griefing-sub --topic antidote-griefing
gcloud pubsub subscriptions create antidote-cheat-sub --topic antidote-cheat
gcloud pubsub subscriptions create antidote-score-sub --topic antidote-score

# Dataflow Setup
gsutil mkdir gs://$GCP_PROJECT_ID-antidote-dataflow
