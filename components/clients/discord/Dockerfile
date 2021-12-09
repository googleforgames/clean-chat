FROM python:3.10-slim

ENV GCP_PROJECT_ID ""
ENV PUBSUB_TOPIC_ID ""
ENV DISCORD_TOKEN ""

WORKDIR /app
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

CMD python3 discord_client.py --gcp_project_id $GCP_PROJECT_ID --pubsub_topic_id $PUBSUB_TOPIC_ID --discord_token $DISCORD_TOKEN

