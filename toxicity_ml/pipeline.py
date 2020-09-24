# coding=utf-8
# Copyright 2020 Google LLC

import tensorflow_model_analysis as tfma
from tfx.components import (Evaluator, ExampleValidator, ImportExampleGen,
                            ModelValidator, Pusher, ResolverNode, SchemaGen,
                            StatisticsGen, Trainer, Transform)
from tfx.proto import example_gen_pb2
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.orchestration.kubeflow import kubeflow_dag_runner


def create_train_pipeline(pipeline_name: Text, pipeline_root: Text):
'''
Args:
    pipeline_name: name of the TFX pipeline being created.
    pipeline_root: root directory of the pipeline. Should be a valid GCS path

Returns:
    A TFX pipeline object.
''' 
	
	## Parameters
	TRAINING_STEPS = 10000
	EVALUATION_STEPS = 1000

	## GCS Location
	serving_model_dir = "/directory"


	## Bring Data Into Pipeline
	example_gen = example_gen_pb2.Output(
             	split_config=example_gen_pb2.SplitConfig(splits=[
                 	example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=45),
                 	example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=5)
             	]))

	## Computes Statistics for Validation
	statistics_gen = StatisticsGen(
    	examples=example_gen.outputs['examples']
    	)

	## Performs Transforms
	transform = Transform(
    	examples=example_gen.outputs['examples'],
    	schema=schema_gen.outputs['schema'],
    	module_file=os.path.abspath("toxicBERT/transform.py")
    	)

	## Trainer Component
	trainer = Trainer(
    	module_file=os.path.abspath("toxicBERT/trainer.py"),
    	custom_executor_spec=executor_spec.ExecutorClassSpec(GenericExecutor),
    	examples=transform.outputs['transformed_examples'],
    	transform_graph=transform.outputs['transform_graph'],
    	schema=schema_gen.outputs['schema'],
    	train_args=trainer_pb2.TrainArgs(num_steps=TRAINING_STEPS),
    	eval_args=trainer_pb2.EvalArgs(num_steps=EVALUATION_STEPS)
    	)

	## Resolver Component
	model_resolver = ResolverNode(
    	instance_name='latest_blessed_model_resolver',
    	resolver_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
    	model=Channel(type=Model),
    	model_blessing=Channel(type=ModelBlessing)
    	)

	## Evaluator 
	eval_config = tfma.EvalConfig(
    	model_specs=[
        	tfma.ModelSpec(label_key='label')
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

    ## Pusher - Export for Model Serving
	pusher = Pusher(
    	model=trainer.outputs['model'],
    	model_blessing=evaluator.outputs['blessing'],
    	push_destination=pusher_pb2.PushDestination(
        	filesystem=pusher_pb2.PushDestination.Filesystem(
            	base_directory=serving_model_dir)))

	return pipeline.Pipeline(
		pipeline_name=pipeline_name,
      	pipeline_root=pipeline_root,
      	components=[
          example_gen, statistics_gen, schema_gen, example_validator, transform,
          trainer, model_resolver, evaluator
      	],
  	)	

def main(unused_argv):
	metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()

  	tfx_image = os.environ.get('KUBEFLOW_TFX_IMAGE', None)

  	runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
     	kubeflow_metadata_config=metadata_config,
      	# Specify custom docker image to use.
      	tfx_image=tfx_image)

  	kubeflow_dag_runner.KubeflowDagRunner(config=runner_config).run(
     	create_pipeline(
         	pipeline_name=_pipeline_name,
         	pipeline_root=_pipeline_root,
      	))


if __name__ == '__main__':
  app.run(main)