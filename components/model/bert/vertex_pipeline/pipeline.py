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
"""Create Pipeline for Vertex AI Pipelines"""

from typing import Optional, Text

import tensorflow_model_analysis as tfma
from tfx import v1 as tfx

import configs


# pylint: disable=too-many-locals,too-many-arguments
def create_pipeline(
        pipeline_name: Text,
        pipeline_root: Text,
        data_path: Text,
        preprocessing_fn: Text,
        train_module: Text,
        train_steps: tfx.proto.TrainArgs = 10,
        eval_steps: tfx.proto.EvalArgs = 10,
        serving_model_dir: Optional[Text] = None,
        schema_path: Optional[Text] = None,
        ai_platform_training_args: Optional[dict] = None,
        ai_platform_serving_args: Optional[dict] = None) -> tfx.dsl.Pipeline:
    """Create TFX pipeline for Vertex AI.

    Args:
        pipeline_name (Text): pipeline name
        pipeline_root (Text): pipeline root (GCS Bucket)
        data_path (Text): data dir for training (GCS Bucket)
        preprocessing_fn (Text): preprocessing function name
        train_module (Text): training module path
        train_steps (tfx.proto.TrainArgs, optional): The number of training steps. Defaults to 10.
        eval_steps (tfx.proto.EvalArgs, optional): The number of evaluation steps. Defaults to 10.
        serving_model_dir (Optional[str], optional): Serving Directory . Defaults to None.
        schema_path (Optional[str], optional): Schema Path for repeated run. Defaults to None.
        ai_platform_training_args (Optional[dict], optional): Train args. Defaults to None.
        ai_platform_serving_args (Optional[dict], optional): Serving args. Defaults to None.

    Returns:
        tfx.dsl.Pipeline: Pipeline Object for TFX.
    """

    components = []

    # Brings data into the pipeline or otherwise joins/converts training data.
    example_gen = tfx.components.CsvExampleGen(input_base=data_path)
    components.append(example_gen)

    # Computes Statistics for Validation
    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs['examples'])
    components.append(statistics_gen)

    # Performs anomaly detection based on statistics and data schema.
    if schema_path is None:
        schema_gen = tfx.components.SchemaGen(
            statistics=statistics_gen.outputs['statistics'])
        components.append(schema_gen)
    else:
        schema_gen = tfx.components.ImportSchemaGen(schema_file=schema_path)
        components.append(schema_gen)

    # Performs anomaly detection based on statistics and data schema.
    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema'])
    components.append(example_validator)

    # Performs Transforms
    transform = tfx.components.Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        preprocessing_fn=preprocessing_fn,
    )
    components.append(transform)

    # Trainer Component
    trainer_args = {
        'examples': transform.outputs['transformed_examples'],
        'schema': schema_gen.outputs['schema'],
        'transform_graph': transform.outputs['transform_graph'],
        'train_args': train_steps,
        'eval_args': eval_steps,
        'module_file': train_module
    }

    if ai_platform_training_args is not None:
        trainer_args['custom_config'] = {
            tfx.extensions.google_cloud_ai_platform.ENABLE_VERTEX_KEY:
                True,
            tfx.extensions.google_cloud_ai_platform.VERTEX_REGION_KEY:
                configs.VERTEX_AI_REGION,
            tfx.extensions.google_cloud_ai_platform.TRAINING_ARGS_KEY:
                ai_platform_training_args,
        }
        trainer = tfx.extensions.google_cloud_ai_platform.Trainer(
            **trainer_args)
    else:
        trainer = tfx.components.Trainer(**trainer_args)

    components.append(trainer)

    # Resolver Component
    model_resolver = tfx.dsl.Resolver(
        strategy_class=tfx.dsl.experimental.LatestBlessedModelStrategy,
        model=tfx.dsl.Channel(type=tfx.types.standard_artifacts.Model),
        model_blessing=tfx.dsl.Channel(
            type=tfx.types.standard_artifacts.ModelBlessing)).with_id(
                'latest_blessed_model_resolver')
    components.append(model_resolver)

    # Evaluator Config
    eval_config = tfma.EvalConfig(
        model_specs=[
            tfma.ModelSpec(label_key='label',
                           signature_name='serving_default',
                           preprocessing_function_names=['transform_features'])
        ],
        metrics_specs=[
            tfma.MetricsSpec(
                metrics=[tfma.MetricConfig(class_name='ExampleCount')],
                thresholds={
                    'accuracy':
                        tfma.MetricThreshold(
                            value_threshold=tfma.GenericValueThreshold(
                                lower_bound={'value': 0.5}),
                            change_threshold=tfma.GenericChangeThreshold(
                                direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                                absolute={'value': -1e-10}))
                })
        ],
        slicing_specs=[
            tfma.SlicingSpec(),
        ])

    # Evaluator Component
    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs['examples'],
        model=trainer.outputs['model'],
        baseline_model=model_resolver.outputs['model'],
        eval_config=eval_config)
    components.append(evaluator)

    pusher_args = {
        'model': trainer.outputs['model'],
        'model_blessing': evaluator.outputs['blessing'],
    }
    if ai_platform_serving_args is not None:
        pusher_args['custom_config'] = {
            tfx.extensions.google_cloud_ai_platform.ENABLE_VERTEX_KEY:
                True,
            tfx.extensions.google_cloud_ai_platform.VERTEX_REGION_KEY:
                configs.VERTEX_AI_REGION,
            tfx.extensions.google_cloud_ai_platform.experimental.PUSHER_SERVING_ARGS_KEY:
                ai_platform_serving_args
        }
        pusher = tfx.extensions.google_cloud_ai_platform.Pusher(**pusher_args)
    else:
        pusher_args['push_destination'] = tfx.proto.PushDestination(
            filesystem=tfx.proto.PushDestination.Filesystem(
                base_directory=serving_model_dir))
        pusher = tfx.components.Pusher(**pusher_args)

    components.append(pusher)

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,
    )
