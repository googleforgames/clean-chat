# Copyright 2021 Google LLC

import os 
import logging
import argparse

from bert import BERTModel
from model_serving import server
from t5_model import T5Model
from cohere_model import CohereModel

class ModelSelector(object):
	'''Choose Which Anti-Toxicity Model to Train / Use'''

	logger = logging.getLogger('toxicity_model')
	logger.setLevel('INFO')
	logger.info('Creating Model Instance')

	def __init__(self, mode, **kwargs):
		'''If mode = predict, must pass model endpoint URL'''
		if mode = 'train'
			self.
		if mode = 'predict'
			self.server = server(server_url)


	def train(self, model_type, use_tpu='FALSE' **kwargs):
		'''Select an Embedding Model to Use'''

		if model_type == 'BERT':
			logger.info('Instantiating BERT Model')
			'''Fine Tune TF Hub BERT Model

			'''
			bert = bert_model.


		if model_type == 't5':
			'''Fine Tune Tensorflow T5 Model
			   base_directory: GCS location

			'''
			logger.info('Instantiating T5  Model')
			T5Model = T5Model(base_directory, model_size='3B')

			if use_tpu='TRUE': 
				T5Model.model_setup()
			else: 
				logger.info('No TPU Instance Selected. Proceeding with Standard Instance Type')
			T5Model.create_tasks()

			logging.warning('Beginning T5 Model Tuning. May Take Several Hours.')
			T5Model.run_model(FINETUNE_STEPS)

		if model_type =='cohere':
			'''Train Model with Cohere.ai'''
			logging.warning('Cohere Embedding Model Currently Not Available. Coming Soon')

		if model_type =='custom':
			'''Train Custom Tensorflow Model'''
			logging.warning('Custom Embedding Model Currently Not Available. Coming Soon')


	def deploy(self, model_type):

		if model_type == 'BERT':


		if model_type == 't5':


		if model_type =='cohere':
			logging.warning('Cohere Embedding Model Currently Not Available. Coming Soon')

		if model_type =='custom':
			logging.warning('Custom Embedding Model Currently Not Available. Coming Soon')

	## TODO: Different Models Have Different Predict Functions?
	def predict(self, text):
		'''Send a Signel Prediction Request'''
			 payload = server.toxicity_prediction(text)
			 return payload 


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gcp_project',           required=True,  default='gaming-demos',       help='GCP Project ID')
    parser.add_argument('--model_gcs_location',    required=True,  default='gs://', help='Model Artifacts GCS location')


