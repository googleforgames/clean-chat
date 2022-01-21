
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





