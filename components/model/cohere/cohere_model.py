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

import cohere as co
import pandas as pd

from toxicity_model import Model

from google.cloud import bigquery
try:
	 __import__(google.cloud)
except ImportError:
	pip.main(['install', google.cloud]) 

class Cohere(object, key):
	''' Handles Embedding with Cohere AI. Supports Retrieval from GCS or Bigquery'''
	def init(self, **kwargs):
		self.client  = cohere.Client("IstgY4Kq8v9r0nb74tjVsR5FPoqEoZYBu71IM5SD") # ADD YOUR API KEY HERE

	def batch_embed(self, examples, batch_size, model_id):
        embeddings = []
        for i in range(0,len(examples),self.batch_size):
            batch = examples[i:i+self.batch_size]
            emb = self.client.embed(texts=batch,model=self.model).embeddings
            embeddings += emb
        return embeddings

	def preprocess(self, data_path, model_id):
		if: 
			google.cloud.bigquery.Client()
			table = bigquery.TableReference.from_string(
    		"bigquery-public-data.utility_us.country_code_iso"
			)
			rows = bqclient.list_rows(
    			table,
    			selected_fields=[
        			bigquery.SchemaField("country_name", "STRING"), /
        			bigquery.SchemaField("fips_code", "STRING"),
    			],
			)
			data = rows.to_dataframe()
		else:
			data = pd.read_csv(data_path)

		# Truncate Long Sentences. Cohere Only Supports 512 characters
		data['comment_text'] = data['comment_text'].str.slice(stop=511)

		# Training Data
		sentences = list(data.iloc[:,1].values)
		labels  = list(data.iloc[:,0].values)

		# Embedding Data
		embeddings = self.batch_embed(examples=train_text, batch_size=5, model_id='small-20211115')

		return embeddings, labels
    

