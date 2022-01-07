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

import tensorflow_model_analysis as tfma
from typing import Text
from tfx.components import (Evaluator, ExampleValidator, ImportExampleGen,
                            ModelValidator, Pusher, SchemaGen,
                            StatisticsGen, Trainer, Transform)
from tfx.proto import example_gen_pb2, pusher_pb2, trainer_pb2
from tfx.dsl.components.common import resolver
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.orchestration import pipeline
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.components.example_gen.csv_example_gen.component import CsvExampleGen
from tfx.types import Channel
from tfx.types.standard_artifacts import Model, ModelBlessing


from pipeline import config

def create_train_pipeline(
	pipeline_name: Text,
    pipeline_root: Text,
    data_path: Text,
    transform_path: Text,
    train_path: Text,
	train_steps,
    eval_steps,
    serving_model_dir
	):

	'''
	Returns:
    	A TFX pipeline object.
	''' 

	## GCS Location
	serving_model_dir = "config.MODEL_GCS"


	## Bring Data Into Pipeline
	output = example_gen_pb2.Output(
             	split_config=example_gen_pb2.SplitConfig(splits=[
                 	example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=45),
                 	example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=5)
             	]))
	example_gen = CsvExampleGen(input_base=serving_model_dir, output_config=output)


	## Computes Statistics for Validation
	statistics_gen = StatisticsGen(
    	examples=example_gen.outputs['examples']
    	)

	## Creates Schema
	schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'], 
	 	infer_feature_shape=True)

	## Performs Transforms
	transform = Transform(
    	examples=example_gen.outputs['examples'],
    	schema=schema_gen.outputs['schema'],
    	module_file=os.path.abspath(transform_path)
    	)

	## Trainer Component
	trainer = Trainer(
    	module_file=os.path.abspath(train_path),
    	#custom_executor_spec=executor_spec.ExecutorClassSpec(GenericExecutor),
    	examples=transform.outputs['transformed_examples'],
    	transform_graph=transform.outputs['transform_graph'],
    	schema=schema_gen.outputs['schema'],
    	train_args=train_steps,
    	eval_args=eval_steps
    	)

	## Resolver Component
	model_resolver = resolver.Resolver(
    	strategy_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
    	model=Channel(type=Model),
    	model_blessing=Channel(type=ModelBlessing)).with_id('latest_blessed_model_resolver'
    	)

	## Evaluator 
	eval_config = tfma.EvalConfig(
    	model_specs=[
        	tfma.ModelSpec(label_key='target')
    	],
    	metrics_specs=[
        	tfma.MetricsSpec(
            	metrics=[
                	tfma.MetricConfig(class_name='ExampleCount')
            	],
            	thresholds = {
                	'binary_accuracy': tfma.MetricThreshold(
                    	value_threshold=tfma.GenericValueThreshold(
                        	lower_bound={'value': 0.5}),
                    	change_threshold=tfma.GenericChangeThreshold( direction=tfma.MetricDirection.HIGHER_IS_BETTER, absolute={'value': -1e-10}))
            	}
        	)
    	],
    	slicing_specs=[tfma.SlicingSpec(),]
    )

	## Evaluator Componant
	evaluator = Evaluator(
    	examples=example_gen.outputs['examples'],
    	model=trainer.outputs['model'],
    	baseline_model=model_resolver.outputs['model'],
    	eval_config=eval_config
	)

    ## TODO: Update Serving Model Directory 
    ## Pusher - Export for Model Serving
	pusher = Pusher(
    	model=trainer.outputs['model'],
    	model_blessing=evaluator.outputs['blessing'],
    	push_destination=pusher_pb2.PushDestination(
        	filesystem=pusher_pb2.PushDestination.Filesystem(
            	base_directory=serving_model_dir)))

	return pipeline.Pipeline(
		pipeline_name='antidote-pipeline',
      	pipeline_root='gs://antdote_ml_storage/tfx_pipeline_output/antidote-pipeline',
      	components=[
          example_gen, statistics_gen, schema_gen, transform,
          trainer, model_resolver, evaluator
      	],
  	)	
