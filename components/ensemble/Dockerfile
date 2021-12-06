FROM apache/beam_python3.7_sdk:2.25.0

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "main.py", "--gcp_project", "gaming-demos", "--region", "us-central1", "--job_name", "antidote-ensemble", "--gcp_staging_location", "gs://gaming-demos-antidote-dataflow/staging", "--gcp_tmp_location", "gs://gaming-demos-antidote-dataflow/tmp", "--batch_size", "10", "--topic_antidote_toxicity", "projects/gaming-demos/topics/antidote-toxicity", "--topic_antidote_griefing", "projects/gaming-demos/topics/antidote-griefing", "--topic_antidote_cheat", "projects/gaming-demos/topics/antidote-cheat", "--runner", "DirectRunner" ]


