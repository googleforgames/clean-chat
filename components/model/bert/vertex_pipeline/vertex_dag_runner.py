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
"""DAG Runner for Vertex AI Pipeline."""

import os
import datetime

from absl import logging
from tfx import v1 as tfx

import pipeline
import configs


def run_pipline() -> None:
    """Creates Vertex AI Pipeline"""

    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9)))

    tfx_image = os.path.join(
        'gcr.io', configs.GOOGLE_CLOUD_PROJECT,
        'tfx-pipeline') + ':' + dt_now.strftime("%Y%m%d%H%M%s")
    runner_config = tfx.orchestration.experimental.KubeflowV2DagRunnerConfig(
        display_name=configs.PIPELINE_NAME, default_image=tfx_image)

    vertex_training_job_spec = {
        'project':
            configs.GOOGLE_CLOUD_PROJECT,
        'worker_pool_specs': [{
            'machine_spec': {
                'machine_type': 'n1-standard-4',
            },
            # This replica count should be 1.
            'replica_count': 1,
            'container_spec': {
                'image_uri': tfx_image,
            },
        }],
    }

    vertex_serving_job_spec = {
        'project_id': configs.GOOGLE_CLOUD_PROJECT,
        'endpoint_name': configs.PIPELINE_NAME,
        'machine_type': 'n1-standard-4',
    }

    tfx.orchestration.experimental.KubeflowV2DagRunner(
        config=runner_config).run(
            pipeline.create_pipeline(
                pipeline_name=configs.PIPELINE_NAME,
                pipeline_root=configs.PIPELINE_ROOT,
                data_path=configs.TRAINING_DATA_DIR,
                preprocessing_fn=configs.PREPROCESSING_FN,
                train_module=configs.TRAIN_MODULE,
                train_steps=tfx.proto.TrainArgs(
                    num_steps=configs.TRAINING_STEPS),
                eval_steps=tfx.proto.EvalArgs(num_steps=configs.EVAL_STEPS),
                serving_model_dir=os.path.join(configs.PIPELINE_ROOT,
                                               'serving_model'),
                ai_platform_training_args=vertex_training_job_spec,
                ai_platform_serving_args=vertex_serving_job_spec))


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    run_pipline()
