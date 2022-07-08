##########################################################################
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
##########################################################################
"""Constants for Vertex DAG Runner"""

import os

try:
    import google.auth
    try:
        _, GOOGLE_CLOUD_PROJECT = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        GOOGLE_CLOUD_PROJECT = ''
except ImportError:
    GOOGLE_CLOUD_PROJECT = ''

# Environment Variables
PIPELINE_NAME = os.getenv('TF_VAR_ML_PIPELINE_NAME')
TRAINING_STEPS = int(os.getenv('TRAINING_STEPS'))
EVAL_STEPS = int(os.getenv('EVAL_STEPS'))
GCS_BUCKET_NAME = os.environ.get('ML_GCS_BUCKET')
VERTEX_AI_REGION = os.environ.get("TF_VAR_GCP_REGION")

# Google Cloud Storage Paths
PIPELINE_ROOT = os.path.join(GCS_BUCKET_NAME, 'tfx_pipeline_output',
                             PIPELINE_NAME)
TRAIN_MODULE = os.path.join(PIPELINE_ROOT, 'module-file', 'model.py')
TRAINING_DATA_DIR = os.path.join(PIPELINE_ROOT, 'training-data')

# preprocessing function
PREPROCESSING_FN = "preprocessing.preprocessing_fn"
