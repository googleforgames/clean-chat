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

# Load Config
include ./config

.PHONY: help gcloud deploy-all terraform-init terraform-apply

help:
	@echo ""
	@echo "Enable GCP APIs"
	@echo "    make enable-gcp-apis"
	@echo ""
	@echo "Initialize Terraform"
	@echo "    make terraform-init"
	@echo ""
	@echo "Terraform Apply"
	@echo "    make terraform-apply"
	@echo ""
	@echo "Deploy realtime Scoring Engine"
	@echo "    make deploy-scoring-engine"
	@echo ""
	@echo "Deploy API Endpoints"
	@echo "    make deploy-endpoints"
	@echo ""
	@echo "Delete Services - Terraform Destroy"
	@echo "    make terraform-destroy"
	@echo ""

deploy-all: terraform-init terraform-apply deploy-scoring-engine deploy-endpoints

# APIs should be enabled as part of the Terraform deployment. 
# This make target can be used to enable all required GCP APIs.
enable-gcp-apis:
	gcloud services enable \
	storage.googleapis.com \
	containerregistry.googleapis.com \
	artifactregistry.googleapis.com \
	cloudbuild.googleapis.com \
	cloudfunctions.googleapis.com \
	container.googleapis.com \
	run.googleapis.com \
	dataflow.googleapis.com \
	speech.googleapis.com

terraform-init:
	$(info GCP_PROJECT_ID is [${TF_VAR_GCP_PROJECT_ID}])
	terraform init

terraform-apply:
	$(info GCP_PROJECT_ID is [${TF_VAR_GCP_PROJECT_ID}])
	terraform apply

terraform-destroy:
	$(info GCP_PROJECT_ID is [${TF_VAR_GCP_PROJECT_ID}])
	terraform destroy

deploy-scoring-engine:
	@echo "Deploying Antidote Scoring Engine"
	@./components/scoring_engine/deploy-scoring-engine.sh

deploy-scoring-engine-interactive:
	@echo "Building Python dependencies for Scoring Logic/ML model"
	@cd ./components/scoring_engine && python3 setup.py sdist && cd ../..
	@echo "Deploying Antidote Scoring Engine"
	@python3 ./components/scoring_engine/main.py \
		--gcp_project ${TF_VAR_GCP_PROJECT_ID} \
		--region ${TF_VAR_DATAFLOW_REGION} \
		--job_name 'antidote-scoring-engine' \
		--gcp_staging_location "gs://${TF_VAR_GCS_BUCKET_DATAFLOW}/staging" \
		--gcp_tmp_location "gs://${TF_VAR_GCS_BUCKET_DATAFLOW}/tmp" \
		--batch_size 10 \
		--pubsub_topic_text_input projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TEXT_INPUT} \
		--pubsub_topic_text_scored projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TEXT_SCORED} \
		--pubsub_topic_toxic projects/${TF_VAR_GCP_PROJECT_ID}/topics/${TF_VAR_PUBSUB_TOPIC_TOXIC} \
		--bq_dataset_name ${TF_VAR_BIGQUERY_DATASET} \
		--bq_table_name ${TF_VAR_BIGQUERY_TABLE} \
		--window_duration_seconds ${TF_VAR_WINDOW_DURATION_SECONDS} \
		--window_sliding_seconds ${TF_VAR_WINDOW_SLIDING_SECONDS} \
		--runner DirectRunner \
		--no_use_public_ips \
		--subnetwork "regions/${TF_VAR_DATAFLOW_REGION}/subnetworks/dataflow-subnet" \
		--extra_package ./components/scoring_engine/dist/scoring_logic-0.1.tar.gz \
		--toxic_user_threshold ${TF_VAR_TOXIC_USER_THRESHOLD} \
		--perspective_apikey ${TF_VAR_PERSPECTIVE_API_KEY}

deploy-endpoints:
	#@echo "[ INFO ] Set static outbound IP address for Callback URL with VPC Access connector and NAT Gateway"
	#./components/networking/static-outbound.sh
	@echo "[ INFO ] Deploy endpoint backend app"
	./components/endpoints/backend_python/deploy_cloud_run_for_backend.sh
	@echo "[ INFO ] Deploy endpoint cloud run instance (temporary deployment to get URL)"
	./components/endpoints/02_deploy_cloud_run_for_endpoints.sh
	@echo "[ INFO ] Deploy endpoints config (openapi spec)"
	./components/endpoints/03_deploy_endpoint_config.sh
	@echo "[ INFO ] Build endpoint cloud run instance"
	./components/endpoints/04_ESPv2_container_build.sh
	@echo "[ INFO ] Deploy endpoint cloud run instance"
	./components/endpoints/05_ESPv2_container_deploy.sh

# Antidote Model Sidecar - Local Training

train-local: 
	@echo "Enterining Local Training"
	@echo "Select Model Type BERT or cohere: "; \
    read MODEL; \
	@python3 ./components/scoring_engine/main.py \
		--gcp_project {GCP_PROJECT_ID} \
		--gcs_location {GCP_BUCKET} \
		--model_type MODEL


# Antidote Model Sidecar - TFX Training in Cloud
# Requires Kubeflow Endpoint

install-skaffold:
	curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 \ 
	sudo install skaffold /usr/local/bin/

tfx-create-pipeline:
	tfx pipeline create \
		--pipeline-path=kubeflow_dag_runner.py \
		--endpoint={ENDPOINT} \
		--build-image

tfx-update-pipeline:
	tfx pipeline update \
		--pipeline-path=kubeflow_dag_runner.py \
		--endpoint=${ENDPOINT}

tfx-run:
	tfx run create \
		--pipeline-name=antidote_pipeline \
		--endpoint=${ENDPOINT}


# Antidote Model Sidecar - Model Deployment 

build-model-serving:
	@echo "Building Tensorflow Serving Container"
	docker pull tensorflow/serving
	docker run -d --name serving_base tensorflow/serving
	@echo "Attaching Model"
	docker cp ../components/model_pipeline/antidote_serving serving_base:/models/antidote_serving
	docker commit --change "ENV MODEL_NAME antidote_serving" serving_base $USER/antidote_serving
	docker tag antidote_serving gcr.io/tensorflow-serving-229609/antidote_serving:v0.1.0
	docker push gcr.io/tensorflow-serving-229609/antidote_serving:v0.1.0
	@echo "Model Container Pushed to Container Registry"

create-serving-cluster:
	@echo "Creating Serving Cluster for Toxicity Model"
	gcloud container clusters create ANTIDOTE_SERVING_CLUSTER \
		--num-nodes 5 \
		--service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
		--preemptible
		--enable-autoscaling \
  		--min-nodes=1 \
  		--max-nodes=3 \
  		--num-nodes=1 
	gcloud config set container/cluster ANTIDOTE_SERVING_CLUSTER
	gcloud container clusters get-credentials 
	@echo "Serving Cluster Created"

deploy-image:
	@echo "Deploying Image to K8s Cluster"
	kubectl set image deployment/antidote-model-deployment image=gcr.io/tensorflow-serving-229609/antidote_serving:v0.1.0
	kubectl create -f antidote_k8s.yaml

serve-latest-model: 
	@echo "Pushing Latest Model to Production"
	# TODO: Update Parameters, Port, model name
	docker run -p 8501:8501 -e MODEL_BASE_PATH=gs://$BUCKET_NAME -e MODEL_NAME=antidote_serving -t tensorflow/serving
