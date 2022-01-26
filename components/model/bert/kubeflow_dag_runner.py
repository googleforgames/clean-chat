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
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.proto import trainer_pb2
import pipeline 

def create_pipline():
  ''' Creates a TFX Pipeline '''
  metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
  tfx_image = 'gcr.io/' + s.getenv('TF_VAR_GCP_PROJECT_ID') + '/tfx-pipeline'
  runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
    kubeflow_metadata_config=metadata_config,
    tfx_image=tfx_image
  )

  kubeflow_dag_runner.KubeflowDagRunner(config=runner_config).run(
    pipeline.create_train_pipeline(
      pipeline_name=os.getenv('TF_VAR_ML_PIPELINE_NAME'),
      pipeline_root=os.getenv('TF_VAR_ML_PIPELINE_ROOT'),
      data_path=os.getenv('TRAINING_DATA_PATH'),
      transform_path=os.path.join(os.getcwd(), 'transform.py'),
      train_path=os.path.join(os.getcwd(), 'trainer.py'),
      train_steps=trainer_pb2.TrainArgs(num_steps=os.getenv('TRAINING_STEPS')),
      eval_steps=trainer_pb2.EvalArgs(num_steps=os.getenv('EVAL_STEPS')),
      serving_model_dir=os.path.join(os.getenv('TF_VAR_ML_PIPELINE_ROOT'), 'serving_model')
      )
  )

if __name__ == '__main__':
  create_pipline()
