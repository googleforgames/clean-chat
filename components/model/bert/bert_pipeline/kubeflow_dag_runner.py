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

import os
from absl import logging

from tfx.orchestration.experimental import KubeflowDagRunner
from tfx import v1 as tfx
import pipeline 

def run_pipline():
  ''' Creates a Kubeflow Pipeline '''

  metadata_config = tfx.orchestration.experimental.get_default_kubeflow_metadata_config()
  tfx_image = 'gcr.io/' + s.getenv('TF_VAR_GCP_PROJECT_ID') + '/tfx-pipeline'
  runner_config = tfx.orchestration.experimental.KubeflowDagRunnerConfig(
    kubeflow_metadata_config=metadata_config,
    tfx_image=tfx_image
  )

  KubeflowDagRunner(config=runner_config).run_pipeline(
    pipeline.create_pipeline(
      pipeline_name=os.getenv('TF_VAR_ML_PIPELINE_NAME'),
      pipeline_root=os.getenv('TF_VAR_ML_PIPELINE_ROOT'),
      data_path=os.getenv('TRAINING_DATA_PATH'),
      preprocessing_fn=os.path.join(os.getcwd(), 'preprocessing.py'),
      run_fn='model.run_fn',
      train_steps=tfx.proto.TrainArgs(num_steps=os.getenv('TRAINING_STEPS')),
      eval_steps=tfx.proto.EvalArgs(num_steps=os.getenv('EVAL_STEPS')),
      serving_model_dir=os.path.join(os.getenv('TF_VAR_ML_PIPELINE_ROOT'), 'serving_model')
      )
  )

if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    run_pipline()
