export PIPELINE_CLUSTER_NAME=${TF_VAR_ML_CLUSTER}
export PIPELINE_VERSION=1.7.1
export ZONE=${TF_VAR_GCP_REGION}
export MACHINE_TYPE=${TF_VAR_ML_MACHINE_TYPE}
export SCOPES=${TF_VAR_ML_SCOPES}

gcloud container clusters create $PIPELINE_CLUSTER_NAME \
    --zone ${ZONE} \
    --machine-type ${MACHINE_TYPE} \
    --scopes ${SCOPES}

# Deploy Kubeflow on Cluster 

export PIPELINE_VERSION=1.7.1
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=${PIPELINE_VERSION}"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=${PIPELINE_VERSION}"

# Get Pipeline Endpoint
gcloud container clusters get-credentials $PIPELINE_CLUSTER_NAME --zone ${ZONE} --project ${TF_VAR_GCP_PROJECT_ID}
export KUBEFLOW_ENDPOINT=$(kubectl describe configmap inverse-proxy-config -n kubeflow | grep googleusercontent.com)