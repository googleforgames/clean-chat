# Copyright 2021 Google LLC

import os 
import logging
import argparse

from bert import kubeflow_dag_runner
from model_serving import server
from t5_model import T5Model
from cohere_model import CohereModel

class ModelSelector(object):
	'''Choose Which Anti-Toxicity Model to Train / Use'''

	logger = logging.getLogger('toxicity_model')
	logger.setLevel('INFO')
	logger.info('Creating Model Instance')

	## TODO: Auto-deploys for kubeflow cluster, checks to see if piepline already exists
	def bert(self, **kwargs):
		logger.info('Instantiating BERT Model')
		logger.info('Creating Kubeflow Pipeline for BERT')
		kubeflow_dag_runner.create_pipline()

	def t5_model(self, use_tpu='FALSE',  **kwargs):
		logger.info('Instantiating T5 Model')
		T5Model = T5Model(base_directory, model_size='3B')

		if use_tpu =='TRUE': 
			T5Model.model_setup()
		else: 
			logger.info('No TPU Instance Selected. Proceeding with Standard Instance Type')
		T5Model.create_tasks()

		logging.warning('Beginning T5 Model Tuning. May Take Several Hours.')
		T5Model.run_model(FINETUNE_STEPS)

	def cohere(self, **kwargs):
		logging.warning('Cohere Embedding Model Currently Not Available. Coming Soon')

if __name__ == '__main__':
    
	model_selector = ModelSelector()

	parser = argparse.ArgumentParser()
	parser.add_argument('--gcp_project', required=True, default='gaming-demos', help='GCP Project ID')
	parser.add_argument('--gcs_location', required=True, default='gs://', help='Location of Model GCS Bucket')
	parser.add_argument('--model_type', required=True, default='BERT', help='Model to be trained')
 
	known_args, = parser.parse_known_args()

	# Set GOOGLE_CLOUD_PROJECT environ variable
	if known_args.gcp_project is None:
		print("Variable 'gcp_project' not set")
		sys.exit()
	else:
		os.environ['GOOGLE_CLOUD_PROJECT']=known_args.gcp_project

	if known_args.model_type == 'BERT':
		model_selector.bert()

	if known_args.model_type == 't5':
		model_selector.t5_model()

	if known_args.model_type == 'cohere':
		model_selector.cohere()


