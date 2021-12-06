# Configs
import os 

PIPELINE_NAME="antidote-pipeline"

## Get Current GCP Project Name
try:
  import google.auth  
  try:
    _, GCP_PROJECT_ID = google.auth.default()
  except google.auth.exceptions.DefaultCredentialsError:
    GCP_PROJECT_ID = ''
except ImportError:
  GCP_PROJECT_ID = ''

## GCS Directories
MODEL_GCS = GCP_PROJECT_ID + '-kubeflowpipelines-default'
OUTPUT_DIR = os.path.join('gs://', MODEL_GCS)
PIPELINE_ROOT = os.path.join(OUTPUT_DIR, 'tfx_pipeline_output',PIPELINE_NAME)
SERVING_MODEL_DIR = os.path.join(PIPELINE_ROOT, 'serving_model')

DATA_PATH = 'gs://{}/antidote/data/'.format(MODEL_GCS)

TFX_IMAGE = f'gcr.io/{GCP_PROJECT_ID}/{PIPELINE_NAME}'

TRAINING_STEPS = 10000
EVALUATION_STEPS = 100

## local Directory Management
TRANSFORM_PATH = os.path.join(os.getcwd(), 'pipeline', 'transform.py')
TRAIN_PATH = os.path.join(os.getcwd(), 'pipeline', 'trainer.py')
