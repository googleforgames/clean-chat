# Load Config
include ./config.default

.PHONY: help gcloud deploy-all terraform-init terraform-apply

help:
	@echo ""
	@echo "Initialize Terraform"
	@echo "    make terraform-init"
	@echo ""
	@echo "Terraform Apply"
	@echo "    make terraform-deploy"
	@echo ""
	@echo "Deploy realtime Scoring Engine"
	@echo "    make deploy-scoring-engine"
	@echo ""
	@echo "Deploy API Endpoints"
	@echo "    make deploy-endpoints"
	@echo ""

deploy-all: terraform-init terraform-apply deploy-scoring-engine deploy-endpoints

terraform-init:
	$(info GCP_PROJECT_ID is [${TF_VAR_GCP_PROJECT_ID}])
	terraform init

terraform-apply:
	$(info GCP_PROJECT_ID is [${TF_VAR_GCP_PROJECT_ID}])
	terraform apply

initialize-artifactregistry:
	-gcloud artifacts repositories create ${TF_VAR_GCP_ARTIFACT_REGISTRY_NAME} \
	--repository-format=docker \
	--location=${TF_VAR_GCP_ARTIFACT_REGISTRY_REGION} \
	--description="Antidote Repo"

deploy-scoring-engine:
	@echo "Building Python dependencies for Scoring Logic/ML model"
	@cd ./components/scoring_engine && python3 setup.py sdist && cd ../..
	@echo "Deploy Antidote Scoring Engine"
	@nohup python3 ./components/scoring_engine/main.py \
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
		--runner ${TF_VAR_DATAFLOW_RUNNER} \
		--no_use_public_ips \
		--subnetwork "regions/${TF_VAR_DATAFLOW_REGION}/subnetworks/dataflow-subnet" \
		--extra_package ./components/scoring_engine/dist/scoring_logic-0.1.tar.gz \
		--toxic_user_threshold ${TF_VAR_TOXIC_USER_THRESHOLD} \
		--perspective_apikey ${TF_VAR_PERSPECTIVE_API_KEY} \
		&

deploy-endpoints:
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

create-pipeline-cluster:
	gcloud auth configure-docker
	gcloud container clusters create "$ML_CLUSTER" --zone "$ML_ZONE" --machine-type "$ML_MACHINE_TYPE" --scopes $ML_SCOPES
	gcloud container clusters get-credentials "$ML_CLUSTER" --zone "$ML_ZONE"
	kubectl apply -f "https://raw.githubusercontent.com/GoogleCloudPlatform/marketplace-k8s-app-tools/master/crd/app-crd.yaml"
	kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user $(gcloud config get-value account)
	kubectl create namespace $ML_NAMESPACE
	docker pull gcr.io/cloud-marketplace-tools/k8s/dev
	BIN_FILE="/tmp/mpdev"
	docker run gcr.io/cloud-marketplace-staging/marketplace-k8s-app-tools/k8s/dev:remove-ui-ownerrefs cat /scripts/dev > "$BIN_FILE"
	chmod +x "$BIN_FILE"
	$BIN_FILE scripts/install --deployer=gcr.io/ml-pipeline/google/pipelines/deployer:0.1 --parameters='{"name": "'$ML_APP_INSTANCE_NAME'", "namespace": "'$ML_NAMESPACE'"}'
	kubectl get pods -n $ML_NAMESPACE --watch
	kubectl describe configmap inverse-proxy-config -n $ML_NAMESPACE | grep googleusercontent.com

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

build-model-serving:
	docker pull tensorflow/serving
	docker run -d --name serving_base tensorflow/serving
	docker cp ../components/model_pipeline/antidote_bert serving_base:/models/antidote_bert
	docker commit --change "ENV MODEL_NAME antidote_bert" serving_base $USER/antidote_serving
	docker kill serving_base
	docker rm serving_base

create-serving-cluster: 
	gcloud container clusters create ANTIDOTE_SERVING_CLUSTER \
	  --machine-type n1-standard-2 \
		--num-nodes 5 \
		--service-account ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
		--preemptible
	gcloud config set container/cluster ANTIDOTE_SERVING_CLUSTER
	gcloud container clusters get-credentials ANTIDOTE_SERVING_CLUSTER

deploy-serving: 
	docker tag $USER/antidote_serving gcr.io/tensorflow-serving/antidote_bert
	gcloud auth configure-docker
	docker push gcr.io/tensorflow-serving/antidote_bert
	kubectl create -f tensorflow_serving/example/antidote_k8s.yaml
