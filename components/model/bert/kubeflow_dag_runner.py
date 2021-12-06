import os
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.proto import trainer_pb2
import pipeline 
import config

def create_pipline():
  metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
  tfx_image = os.environ.get('config.TFX_IMAGE', None)
  runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
    kubeflow_metadata_config=metadata_config,
    tfx_image=tfx_image
  )

  kubeflow_dag_runner.KubeflowDagRunner(config=runner_config).run(
    pipeline.create_train_pipeline(
      pipeline_name=config.PIPELINE_NAME,
      pipeline_root=config.PIPELINE_ROOT,
      data_path=config.DATA_PATH,
      transform_path=config.TRANSFORM_PATH,
      train_path=config.TRAIN_PATH,
      train_steps=trainer_pb2.TrainArgs(num_steps=config.TRAINING_STEPS),
      eval_steps=trainer_pb2.EvalArgs(num_steps=config.EVALUATION_STEPS),
      serving_model_dir=config.SERVING_MODEL_DIR,
      )
  )

