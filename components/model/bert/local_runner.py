# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Define LocalDagRunner to run the pipeline locally."""

import os
from absl import logging

from tfx import v1 as tfx
import pipeline

OUTPUT_DIR = '.'
PIPELINE_ROOT = os.path.join(OUTPUT_DIR, 'tfx_pipeline_output',
                             configs.PIPELINE_NAME)
METADATA_PATH = os.path.join(OUTPUT_DIR, 'tfx_metadata', configs.PIPELINE_NAME,
                             'metadata.db')

SERVING_MODEL_DIR = os.path.join(PIPELINE_ROOT, 'serving_model')

## TODO: Change to Enviroment Variable
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def run():
  """Define a local pipeline."""

  ## Change anything withj config
  tfx.orchestration.LocalDagRunner().run(
      pipeline.create_pipeline(
          pipeline_name=configs.PIPELINE_NAME,
          pipeline_root=PIPELINE_ROOT,
          data_path=DATA_PATH,
          preprocessing_fn=configs.PREPROCESSING_FN,
          run_fn=configs.RUN_FN,
          train_steps=tfx.proto.TrainArgs(num_steps=os.getenv('TRAINING_STEPS')),
          eval_steps=tfx.proto.EvalArgs(num_steps=os.getenv('EVAL_STEPS')),
          serving_model_dir=SERVING_MODEL_DIR,
          metadata_connection_config=tfx.orchestration.metadata
          .sqlite_metadata_connection_config(METADATA_PATH)))


if __name__ == '__main__':
  logging.set_verbosity(logging.INFO)
  run()