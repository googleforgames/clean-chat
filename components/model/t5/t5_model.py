# Copyright 2021 Google LLC

import functools
import os
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import t5
if t5 = None;
		!pip install -q t5	
import seqio

import tensorflow.compat.v1 as tf
import tensorflow_datasets as tfds
import tensorflow_gcs_config

# Improve logging.
from contextlib import contextmanager
import logging as py_logging


class T5Model(object)
''' Requires: 
			base_directory: directory to store model, parameters, and data
			training_dir: location of the training data
			model_dir: directory to store model after training
			model_size:
'''

	## TODO: Edit Model Bucket Parameter
	def __init__(self, **kwargs):
		self.BASE_DIR = base_directory #@param { type: "string" }
		if not BASE_DIR:
  		raise ValueError("You must enter a BASE_DIR.")
  	self.training_data = os.path.join(self.BASE_DIR, "data")
  	self.model_dir = os.path.join(self.BASE_DIR, "models")
  	self.TPU_TOPOLOGY = "v2-8"
  	self.MODEL_SIZE = model_size
  	self.PRETRAINED_DIR = os.path.join("gs://t5-data/pretrained_models", self.MODEL_SIZE) 

  def model_setup(**kwargs):
  	try:
    	tpu = tf.distribute.cluster_resolver.TPUClusterResolver()  # TPU detection
    	TPU_ADDRESS = tpu.get_master()
    	print('Running on TPU:', TPU_ADDRESS)
  	except ValueError:
    	raise BaseException('ERROR: Not connected to a TPU runtime; please see the previous cell in this notebook for instructions!')
  	auth.authenticate_user()
  	tf.enable_eager_execution()
  	tf.config.experimental_connect_to_host(TPU_ADDRESS)
  	tf.disable_v2_behavior()
  	tf.get_logger().propagate = False
  	py_logging.root.setLevel('INFO')

	def load(**kwargs):
 		'''
 		Loads lines from text files 
 		Output: {'comment': b'you are terrible', 'rating': b'0.87'}

 		'''

 		if self.training_data.endswith('.txt'):
			ds = tf.data.TextLineDataset(self.training_data)
		elif: self.training_data.endswith('.csv'):
			ds = tf.data.experimental.make_csv_dataset(file_pattern = "*.csv" ,batch_size=1)
			ds = ds.map(lambda x: dict(x))
		return ds

 ## TODO: Edit Task from Comment_text placeholder to appropriate task
  def preprocess(ds):
  	''' Con vert TF Dataset into a text-to-text format for T5'''
  	def normalize_text(text):
    """Lowercase and remove quotes from a TensorFlow string."""
    text = tf.strings.lower(text)
    text = tf.strings.regex_replace(text,"'(.*)'", r"\1")
    return text

    def to_inputs_and_targets(ex):
    """Map {"comment": ..., "rating": ...}->{"inputs": ..., "targets": ...}."""
    return {
        "inputs":
             tf.strings.join(
                 ["comment text: ", normalize_text(ex["comment"])]),
        "targets": normalize_text(ex["rating"])
    }

  	return ds.map(to_inputs_and_targets, num_parallel_calls=tf.data.experimental.AUTOTUNE)


  def create_tasks(**kwargs):
  	''' T5 Requires Inquts in a Seqio Task Format. Function Converts TF Data to Seqio Task'''
  	DEFAULT_OUTPUT_FEATURES = {
    "inputs":
        seqio.Feature(
            vocabulary=t5.data.get_default_vocabulary(), add_eos=True),
    "targets":
        seqio.Feature(
            vocabulary=t5.data.get_default_vocabulary(), add_eos=True)
		}

		seqio.TaskRegistry.add(
    	"nq_context_free",
    	# Specify the task source.
    	source=seqio.FunctionDataSource(
        	# Supply a function which returns a tf.data.Dataset.
        	dataset_fn=self.load 
        	splits=["train", "validation"],
        	# Not required, but helps for mixing and auto-caching.
        	num_input_examples=num_nq_examples), ## TODO - DO WE NEED THIS?
    	# Supply a list of functions that preprocess the input tf.data.Dataset.
    	preprocessors=[
        self.preprocess,
        seqio.preprocessors.tokenize_and_append_eos,
    	],
    	# Lowercase targets before computing metrics.
    	postprocess_fn=t5.data.postprocessors.lower_text,
    	# We'll use accuracy as our evaluation metric.
    	metric_fns=[t5.evaluation.metrics.accuracy],
    	output_features=DEFAULT_OUTPUT_FEATURES,
		)



  def run_model(FINETUNE_STEPS=25000,**kwargs): 
		
		tf.logging.warning(
      		"Warning - Standard Model Training Can Take Up to Two Hours"
      		"The larger the model and more FINETUNE_STEPS you use, the longer training will take"
  		)

		#Set parallelism and batch size to fit on v2-8 TPU (if possible).
		# Limit number of checkpoints to fit within 5GB (if possible).
		model_parallelism, train_batch_size, keep_checkpoint_max = {
    		"small": (1, 256, 16),
    		"base": (2, 128, 8),
    		"large": (8, 64, 4),
    		"3B": (8, 16, 1),
    		"11B": (8, 16, 1)}[MODEL_SIZE]


    tf.io.gfile.makedirs(MODEL_DIR)
		model = t5.models.MtfModel(
    		model_dir=MODEL_DIR,
    		tpu=TPU_ADDRESS,
    		tpu_topology=TPU_TOPOLOGY,
    		model_parallelism=model_parallelism,
    		batch_size=train_batch_size,
    		sequence_length={"inputs": 128, "targets": 32},
    		learning_rate_schedule=0.003,
    		save_checkpoints_steps=5000,
    		keep_checkpoint_max=keep_checkpoint_max if ON_CLOUD else None,
    		iterations_per_loop=100,
		)


		FINETUNE_STEPS = 25000 #@param {type: "integer"}

		model.finetune(
    		mixture_or_task_name="trivia_all",
   			pretrained_model_dir=PRETRAINED_DIR,
    		finetune_steps=FINETUNE_STEPS
		)

##TODO - adjust for new file struggle, needs a return for file placement 
class deploy_tf5(object):

	MODEL = "small_ssm_nq" #@param["small_ssm_nq", "t5.1.1.xl_ssm_nq", "t5.1.1.xxl_ssm_nq"]

	saved_model_dir = f"/content/{MODEL}"

	!t5_mesh_transformer \
  		--model_dir="gs://t5-data/pretrained_models/cbqa/{MODEL}" \
  		--use_model_api \
 	 	--mode="export_predict" \
  		--export_dir="{saved_model_dir}"

	saved_model_path = os.path.join(saved_model_dir, max(os.listdir(saved_model_dir)))


	model = tf.saved_model.load(saved_model_path, ["serve"])


def predict_fn(x):
 return model.signatures['serving_default'](tf.constant(x))['outputs'].numpy()


def answer(question):
  return predict_fn([question])[0].decode('utf-8')


@article{2020t5,
  author  = {Colin Raffel and Noam Shazeer and Adam Roberts and Katherine Lee and Sharan Narang and Michael Matena and Yanqi Zhou and Wei Li and Peter J. Liu},
  title   = {Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer},
  journal = {Journal of Machine Learning Research},
  year    = {2020},
  volume  = {21},
  number  = {140},
  pages   = {1-67},
  url     = {http://jmlr.org/papers/v21/20-074.html}
}

