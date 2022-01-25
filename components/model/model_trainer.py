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
# Note: T5 Model Still Under Work. Needs a Better Distributed Strategy (Heavily Resource Intesnive)

import os 
import logging
import argparse

from bert import kubeflow_dag_runner
from model_serving import server
from t5_model import T5Model
from cohere_model import Cohere

class ModelSelector(object):
	'''Choose Which Anti-Toxicity Model to Train / Use'''

	def __init__(self): 
		self.yes = {'yes','y'}
		self.no = {'no','n'}

	logger = logging.getLogger('toxicity_model')
	logger.setLevel('INFO')
	logger.info('Creating Model Instance')

	## TODO: Auto-deploys for kubeflow cluster, checks to see if piepline already exists
	def bert_select(self, **kwargs):
		logger.info('Instantiating BERT Model')
		logger.info('Creating Kubeflow Pipeline for BERT')
		kubeflow_dag_runner.create_pipline()
		sys.stdout.write('Proceed with Training?')
		choice = raw_input().lower()
		if choice in yes:
   			##TODO - Add Model Training Run
		elif choice in no:
   			return False ## TODO: Placeholder for doing nothing
		else:
   			sys.stdout.write("Please respond with 'yes' or 'no'")

	def cohere_select(self, data_location, gcs_location, model_type, cohere_key):
		''' Generates Embeddings from Cohere; Option to train classification model'''
		logging.warning('Creating Model')
		cohere = Cohere(cohere_key)
		embeddings, labels = cohere.preprocess(data_location, model_type)
		logging.warning('Embeddings Successfully Retrieved')
		sys.stdout.write('Proceed with Training?')
		choice = raw_input().lower()
		if choice in yes:
   			# Basic Model. Replace with your own model by editing toxicity_model.py 
			embed_length = len(embeddings[1])
			model = Model().model(embed_length)
			## Fit and save to GCS bucket
			model.fit(embeddings,labels, gcs_location) 
		elif choice in no:
   			return embeddings, labels
		else:
   			sys.stdout.write("Please respond with 'yes' or 'no'")

if __name__ == '__main__':
    
	model_selector = ModelSelector()

	parser = argparse.ArgumentParser()
	parser.add_argument('--gcp_project', required=True, default='gaming-demos', help='GCP Project ID')
	parser.add_argument('--data_location', required=True, default='', help='Location of Data')
	parser.add_argument('--gcs_location', required=True, default='gs://', help='Location of Model GCS Bucket')
	parser.add_argument('--model', required=True, default='BERT', help='Model to be trained')
	parser.add_argument('--model_type', required=False, default='small-20211115', help='Optional: Cohere Embedding Modeling')
	parser.add_argument('--cohere_key', required=False, default='', help='Cohere API Key')

	known_args, = parser.parse_known_args()

	# Set GOOGLE_CLOUD_PROJECT environ variable
	if known_args.gcp_project is None:
		print("Variable 'gcp_project' not set")
		sys.exit()
	else:
		os.environ['GOOGLE_CLOUD_PROJECT']=known_args.gcp_project

	if known_args.model_type == 'BERT':
		model_selector.bert_select()

	if known_args.model_type == 'cohere':
		model_selector.cohere_select(known_args.data_location, known_args.gcs_location, known.args.model_type, known_args.cohere_key)


