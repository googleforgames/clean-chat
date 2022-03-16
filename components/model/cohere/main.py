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

import logging
import sys

import cohere as co
import pandas as pd

from toxicity_model import Model

from google.cloud import bigquery
try:
	 __import__(google.cloud)
except ImportError:
	pip.main(['install', google.cloud]) 

class Cohere(object, key):
	''' Handles Embedding with Cohere AI. '''
	def init(self, **kwargs):
		self.client  = cohere.Client(key) # ADD YOUR API KEY HERE

	def batch_embed(self, examples, batch_size, model_id):
        embeddings = []
        for i in range(0,len(examples),self.batch_size):
            batch = examples[i:i+self.batch_size]
            emb = self.client.embed(texts=batch,model=self.model).embeddings
            embeddings += emb
        return embeddings

    def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

	def retry(fun, max_tries=5):
  		backoff = 1
  		i = 0
  		while True:
    		try:
      			return fun()
      			break
    		except Exception as e:
      			if i == max_tries:
        			raise e
      			time.sleep(backoff)
      			backoff**2
      			i+=1
      			continue

	def read_data(self, data_path):
		data = pd.read_csv(data_path)
		training_data = data.sample(frac=0.8, random_state=25)
		testing_data = data.drop(training_data.index)

		return training_data, testing_data

	def preprocess(self, model_id, data):		

		training_data = data.sample(frac=0.8, random_state=25)
		testing_data = data.drop(training_data.index)

		# Truncate Long Sentences. Cohere Only Supports 512 characters
		data['comment_text'] = data['comment_text'].str.slice(stop=511)

		comment_lists = chunks(list(data['comment_text']), 100)
		result = []
		for batch in comment_lists:
  			result += (retry(lambda: self.client.embed(model_id, batch)).embeddings)
  			time.sleep(5)
  		data.loc[:,'embedded_text'] = result

		return data

if __name__ == '__main__':

	logging.warning('Creating Embeddings')
	cohere = Cohere(sys.argv[1])
	training_data, testing_data = Cohere.read_data(sys.argv[2])
	train_data = Cohere.preprocess(sys.argv[3], training_data)
	test_data = Cohere.preprocess(sys.argv[3], testing_data)
	logging.warning('Embeddings Successfully Retrieved')
	sys.stdout.write('Proceed with Training?')
	choice = raw_input().lower()
	if choice in yes:
   		# Basic Model. Replace with your own model by editing toxicity_model.py 
		embed_length = len(embeddings[1])
		model = Model().model(embed_length)
		## Fit and save to GCS bucket
		model.fit(train_data['embedded_text'], train_data['target'], test_data['embedded_text'], test_data['target'], gcs_location) 
	elif choice in no:
   		return train_embeddings, train_labels, test_embeddings, test_labels
	else:
   		sys.stdout.write("Please respond with 'yes' or 'no'")
    

