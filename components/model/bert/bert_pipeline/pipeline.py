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

from typing import Any, Dict, List, Optional

import tensorflow_model_analysis as tfma
from tfx import v1 as tfx

from ml_metadata.proto import metadata_store_pb2


def create_pipeline(
	pipeline_name: str,
    pipeline_root: str,
    data_path: str,
    preprocessing_fn: str,
    run_fn: str,
    train_steps: tfx.proto.TrainArgs,
    eval_steps: tfx.proto.EvalArgs,
	train_steps,
    eval_steps,
    serving_model_dir
	):

	'''
	Returns:
    	A TFX pipeline object.
	''' 


	components = []

  	## Brings data into the pipeline or otherwise joins/converts training data.
  	example_gen = tfx.components.CsvExampleGen(input_base=data_path)
  	components.append(example_gen)

	## Computes Statistics for Validation
	statistics_gen = tfx.components.StatisticsGen(
    	examples=example_gen.outputs['examples']
    	)

	## Performs anomaly detection based on statistics and data schema.
	if schema_path is None:
    	schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'])
    	components.append(schema_gen)
  	else:
    	schema_gen = tfx.components.ImportSchemaGen(schema_file=schema_path)
    	components.append(schema_gen)

    ## Performs anomaly detection based on statistics and data schema.
    example_validator = tfx.components.ExampleValidator(statistics=statistics_gen.outputs['statistics'],
    													schema=schema_gen.outputs['schema'])
	components.append(example_validator)


	## Performs Transforms
	transform = tfx.components.Transform(
      examples=example_gen.outputs['examples'],
      schema=schema_gen.outputs['schema'],
      preprocessing_fn=preprocessing_fn)
  	components.append(transform)

	## Trainer Component
	trainer = tfx.components.Trainer(
    	module_file=os.path.abspath(train_path),
    	#custom_executor_spec=executor_spec.ExecutorClassSpec(GenericExecutor),
    	examples=transform.outputs['transformed_examples'],
    	transform_graph=transform.outputs['transform_graph'],
    	schema=schema_gen.outputs['schema'],
    	train_steps=train_steps,
    	eval_steps=eval_steps
    	)

	# Uses user-provided Python function that implements a model.
  	trainer_args = {
    	'run_fn': run_fn,
    	'examples': transform.outputs['transformed_examples'],
    	'schema': schema_gen.outputs['schema'],
    	'transform_graph': transform.outputs['transform_graph'],
    	'train_args': train_args,
    	'eval_args': eval_args,
  		}

  	if ai_platform_training_args is not None:
    	trainer_args['custom_config'] = {
        	tfx.extensions.google_cloud_ai_platform.TRAINING_ARGS_KEY:
            	ai_platform_training_args,
    	}   	
    	trainer = tfx.extensions.google_cloud_ai_platform.Trainer(**trainer_args)
  	else:
    	trainer = tfx.components.Trainer(**trainer_args)
		components.append(trainer)

	## Resolver Component
	model_resolver = tfx.dsl.Resolver(
    	strategy_class=tfx.dsl.experimental.LatestBlessedModelStrategy,
    	model=tfx.dsl.Channel(type=tfx.types.standard_artifacts.Model),
    	model_blessing=tfx.dsl.Channel(
          type=tfx.types.standard_artifacts.ModelBlessing)).with_id(
              'latest_blessed_model_resolver')
  	components.append(model_resolver)

	## Evaluator 
	eval_config = tfma.EvalConfig(
    	model_specs=[
        	tfma.ModelSpec(label_key='target',
        	signature_name='serving_default',
        	preprocessing_function_names=['transform_features'])
    	],
    	metrics_specs=[
        	tfma.MetricsSpec(
            	metrics=[
                	tfma.MetricConfig(class_name='ExampleCount')
            	],
            	thresholds = {
                	'accuracy': tfma.MetricThreshold(
                    	value_threshold=tfma.GenericValueThreshold(
                        	lower_bound={'value': 0.5}),
                    	change_threshold=tfma.GenericChangeThreshold( direction=tfma.MetricDirection.HIGHER_IS_BETTER, absolute={'value': -1e-10}))
            	}
        	)
    	],
    	slicing_specs=[tfma.SlicingSpec(),]
    )

	## Evaluator Componant
	evaluator = tfx.components.Evaluator(
    	examples=example_gen.outputs['examples'],
    	model=trainer.outputs['model'],
    	baseline_model=model_resolver.outputs['model'],
    	eval_config=eval_config
	)
	components.append(evaluator)

	# Checks whether the model passed the validation steps and pushes the model
  	# to a file destination if check passed.
 	pusher_args = {
     	'model':
         	trainer.outputs['model'],
      	'model_blessing':
         	evaluator.outputs['blessing'],
 	}

  if ai_platform_serving_args is not None:
    pusher_args['custom_config'] = {
        tfx.extensions.google_cloud_ai_platform.experimental
        .PUSHER_SERVING_ARGS_KEY:
            ai_platform_serving_args
    }
    pusher = tfx.extensions.google_cloud_ai_platform.Pusher(**pusher_args)  # pylint: disable=unused-variable
  else:
    pusher_args['push_destination'] = tfx.proto.PushDestination(
        filesystem=tfx.proto.PushDestination.Filesystem(
            base_directory=serving_model_dir))
    pusher = tfx.components.Pusher(**pusher_args)  # pylint: disable=unused-variable
  # TODO(step 6): Uncomment here to add Pusher to the pipeline.
  # components.append(pusher)

    ## TODO: Update Serving Model Directory 
    ## Pusher - Export for Model Serving
	pusher = tfx.components.Pusher(
    	model=trainer.outputs['model'],
    	model_blessing=evaluator.outputs['blessing'],
    	push_destination=tfx.proto.PushDestination(
        	filesystem=tfx.proto.PushDestination.Filesystem(
            	base_directory=serving_model_dir)))
	## TODO: Change Pipeline Name / Root Enviroment Variables
	return pipeline.Pipeline(
		pipeline_name=pipeline_name,
      	pipeline_root=pipeline_root,
      	components=components
  	)	
