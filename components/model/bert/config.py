################################################################################################################
#
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################################################

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
