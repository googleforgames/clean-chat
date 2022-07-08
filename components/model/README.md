# Overview 

Clean Chat comes pre-packaged with a framework to train, test, and deploy toxicity detection models. Currently, the framework supports models that detect toxicity in voice and text chat. Clean Chat provides two model training interfaces; one basic training interface that only utilizes the training features of Keras, and one that supports an ML Ops framework. 

## Model Choices

### Cohere.AI 
Cohere.ai is a Google Cloud Partner who provides a developer API to create high-quality word embeddings. Users may “fine tune” a base cohere embedding model to receive embeddings that are specific to a Game’s dataset. We then provide a base Keras feed-forward neural network model, similar to those provided in Google tutorials, for a user to adjust. The Cohere Embeddings are fed into the Keras model, and the model is trained. 

To learn more about Cohere, see their [documentation](https://docs.cohere.ai/).

To utilize the Cohere model, run: 

```
python ./cohere/main.py 'API KEY HERE' 'DATA PATH HERE' 'COHERE MODEL TYPE HERE'
```

### BERT

BERT is a transformer language model developed by Google in 2018. BERT is available via Tensorflow Hub, and users can fine-tune the model to their Game’s dataset. 

#### Model Training with TFX (ML Ops)

This module presents a packaged TFX pipeline for training and deploying your own custom toxicity model. Clean Chat currently supports the [TF Hub BERT Model](https://tfhub.dev/) as it's base language model in a TFX framework. 

The architecture consists of: 
- The model pipeline (tfx_pipeline.py). A TFX/Kubeflow pipeline to transform the training data, train the model, and push the resulting model artifact 
  - transform.py (TFX transform file)
  - trainer.py (TFX training file)
- The pipeline runner (kubeflow_dag_runner.py)

You will need to setup a kubernetes cluster with kubeflow deployed on it. This is where your built pipeline will reside. You can set up your cluster with:

```
make create-pipeline-cluster
```
Your pipeline endpoint (the address of your pipeline is now contained in the enviroment variable KUBEFLOW_ENDPOINT

Before you build your pipeline, set the enviroment variables for the number of training steps, evaluation steps, adn the path to the model's training data. 

```
export TRAINING_DATA_PATH='training data dir path here'
export TRAINING_STEPS='the number of training steps'
export EVAL_STEPS='the number of eval steps'
```

To build your TFX pipeline on the Kubeflow cluster that you just created, run: 

```
make tfx-create-pipeline
```

Additional runs of the pipeline can be conducted with: 

``` 
make tfx-run
```

### Model Deployment

To deploy your pipeline to the cloud, we need both a serving container and a serving cluster. You can create the serving container with: 

``` 
make build-model-serving
```

Next, create a Kubernetes cluster to deploy your model on: 

``` 
make create-serving-cluster
```
Finally, to create a deployment of the model, run: 

```
make deploy-image
```
If you need to update the model that is currently being served, you may do so with: 

```
make serve-latest-model
```

### Vertex AI Pipelines

[tfx](https://www.tensorflow.org/tfx/guide/cli#create) supports [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs) option (`tfx pipeline create --engine=vertex`).   
This section helps you to deploy your BERT pipeline to Vertex AI. 

Before you start, you need to set up local Python environment. For Vertex AI compatibility, we use Python `3.7.12` or `3.7.13`. 

In addition, these commands build the image with [Docker](https://www.docker.com/). Install Docker if needed. 

After you set up the Python environment, install modules.

```sh
pip install -r ./components/model/bert/vertex_pipeline/requirements.txt
```

You have to enable Vertex AI service, Container Registry and Cloud Storage. Make sure you have the **OWNER** permission of your GCP Project to avoid IAM problems. 

```sh
gcloud services enable \
  aiplatform.googleapis.com \
  containerregistry.googleapis.com \
  storage.googleapis.com
```

After enabling the service, you need to set up values Vertex AI Pipelines.

```sh
cd ~/clean-chat # or appropriate root path you cloned this repository.
source config
source ./components/model/bert/vertex_pipeline/env.sh
make vertex-upload-data
make vertex-create-pipeline
```

[`vertex-upload-data`](../../Makefile) uploads sample data to Google Cloud Storage. If you changed it, you need to upload again.

[`vertex-create-pipeline`](../../Makefile) creates pipeline in Vertex AI and build a docker image with [Dockerfile](../../Dockerfile).

This image is used as the default image in the pipeline. 

Then you can run the pipeline. [`vertex-run-pipeline`](../../Makefile) run the pipeline.

```sh
make vertex-run-pipeline
```

The command shows the URL for Vertex AI pipelines to monitor the run.

If you modify files, you need to update the pipeline before your new run. 

```sh
make vertex-update-pipeline
```

Then run your pipeline again.

```sh
make vertex-run-pipeline
```