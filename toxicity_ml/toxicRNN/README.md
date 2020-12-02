# **RNN for text-based Toxicity Modeling**

---
The notebook within this directory predicts toxic comments, where 0 is non-toxic and 1 is toxic. It was trained against the data within this directory, which is a sample dataset from Jigsaw containing 10000 records. 

Our end-goal is to implement a BERT, however a RNN was used in this case to prototype the end-to-end flow, specifically focusing on getting the Tensorflow model serving process correct. This repo achieves our model serving goals (at least at this point), by deploying the RNN model which accepts a raw text string and outputs a JSON payload with the toxicity score on a scale of 0-1.

## RNN Model Training
The model training code was developed within [Google Colab Notebooks](https://colab.sandbox.google.com/) and was saved as an .ipynb file (which can be loaded into a [Colab](https://colab.sandbox.google.com/), [AI Platform Notebooks](https://cloud.google.com/ai-platform-notebooks), open-source [Jupyter](https://jupyter.org/), etc). When this notebook is execute in [Colab](https://colab.sandbox.google.com/), it'll save a .tar.gz file (called toxicity_model_z1.tar.gz by default). This file can then be placed in a Google Cloud Storage directory that you specify (we are currently working from the gs://model_artificats/ GCS location). 

## Tensorflow Model Serving 
*Reference: https://www.tensorflow.org/tfx/serving/docker*
To serve this model, execute the following code:
```
# Variables
gcs_path_to_model="gs://model_artificats/toxicity_model_z1.tar.gz"
gcs_model_filename=${gcs_path_to_model##*/}
model_path="$(pwd)/saved_models/"
model_name=bert_model

# Install Docker (if not already installed)
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install -y wget apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
# Add docker to sudo users
sudo groupadd docker
sudo usermod -aG docker $USER
# Test Install
#sudo docker run hello-world

# Pull Docker dependencies and run container for model serving
sudo docker pull tensorflow/serving
gsutil cp "$gcs_path_to_model" .
tar -zxvf $gcs_model_filename
sudo docker run -t --rm -p 8501:8501 -v "$model_path:/models/$model_name" -e MODEL_NAME=$model_name tensorflow/serving &
```

## Client-side Prediction
```
curl -d '{"inputs":{"review": ["you suck at this game, i hate you. this is terrible."]}}' -X POST http://localhost:8501/v1/models/$model_name:predict
```

