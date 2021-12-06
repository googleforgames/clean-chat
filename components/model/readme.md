## Overview 

This module presents a packaged TFX pipeline for training and deploying your own custom toxicity model. Antidote currently utilizes the [TF Hub BERT Model](https://tfhub.dev/) as it's base language model. 

The architecture consists of: 
- The model pipeline (tfx_pipeline.py). A TFX/Kubeflow pipeline to transform the training data, train the model, and push the resulting model artifact 
  - transform.py (TFX transform file)
  - trainer.py (TFX training file)


Set your project
```
gcloud config set project antidote-playground
```


For running the pipeline in Google Cloud, find your Google Cloud project ID and set it as an enviroment variable

```
gcloud config list --format 'value(core.project)' 2>/dev/null
env GOOGLE_CLOUD_PROJECT={PROJECT ID HERE}
```

### Setting up your Kubernetes Cluster 

To deploy your pipeline to the cloud, we need to create a kubernetes cluster to host the kubeflow deployment. 

To create the cluster, run the following command. Make sure that the enviroment variables SERVICE_ACCOUNT and PROJECT_ID are defined beforehand. 

```
make create-cluster
```

This will create a new Kubernetes cluster named ANTIDOTE_CLUSTER running on a preemptible VM.  You'll need am ENDPOINT enviroment variable with the address of the new cluster. 

### Build Your Pipeline

When creating a pipeline for Kubeflow Pipelines, we need a container image which will be used to run our pipeline. You may either use base image, or a custom image. 

If selecting a base image, run the following command for Skaffold to pull the image from Docker Hub. It will take 5~10 minutes when we build the image for the first time, but it will take much less time from the second build.

```
make install-skaffold
```
Define the name of your pipeline image: 

```
TFX_IMAGE=gcr.io/${=PROJECT_ID}/antidote_pipeline
```

You can then run an initial execution of the pipeline with:

```
make tfx-create-pipeline
```
A Dockerfile will be generated. Don't forget to add it to the source control system (for example, git) along with other source files.

### 


### Scheduling Retrains


