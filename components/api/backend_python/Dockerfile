# Copyright 2022 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.9-slim

ARG TF_VAR_GCP_PROJECT_ID
ARG TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT
ARG TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG
ARG TF_VAR_GCS_BUCKET_TEXT_DROPZONE
ARG TF_VAR_PUBSUB_TOPIC_TEXT_INPUT

ENV TF_VAR_GCP_PROJECT_ID=${TF_VAR_GCP_PROJECT_ID}
ENV TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT}
ENV TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG=${TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG}
ENV TF_VAR_GCS_BUCKET_TEXT_DROPZONE=${TF_VAR_GCS_BUCKET_TEXT_DROPZONE}
ENV TF_VAR_PUBSUB_TOPIC_TEXT_INPUT=${TF_VAR_PUBSUB_TOPIC_TEXT_INPUT}

RUN echo "TF_VAR_GCP_PROJECT_ID: $TF_VAR_GCP_PROJECT_ID"
RUN echo "TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT: $TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_SHORT"
RUN echo "TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG: $TF_VAR_GCS_BUCKET_AUDIO_DROPZONE_LONG"
RUN echo "TF_VAR_GCS_BUCKET_TEXT_DROPZONE: $TF_VAR_GCS_BUCKET_TEXT_DROPZONE"
RUN echo "TF_VAR_PUBSUB_TOPIC_TEXT_INPUT: $TF_VAR_PUBSUB_TOPIC_TEXT_INPUT"

ENV PYTHONUNBUFFERED True

WORKDIR /app

RUN apt-get update && apt-get -y install ffmpeg 

COPY ./main.py .
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app