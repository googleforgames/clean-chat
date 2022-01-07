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

## TODO: Clean Up Imports
import cohere as co

import pandas as pd

from keras.engine import Layer, InputSpec
from keras.layers import Flatten 
import tensorflow as tf


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Input, GRU, Dense, Embedding, Dropout, Bidirectional, TimeDistributed, Flatten, Dot
from keras.models import Model
from keras_trainer import base_model
from keras_trainer.custom_metrics import auc_roc

from google.cloud import bigquery
try:
	 __import__(google.cloud)
except ImportError:
	pip.main(['install', google.cloud]) 



class CohereEmbed(object):
	''' Handles Embedding with Cohere AI. Supports Retrieval from GCS or Bigquery'''
	def init(self, **kwargs):
		self.key  = cohere.Client("IstgY4Kq8v9r0nb74tjVsR5FPoqEoZYBu71IM5SD") # ADD YOUR API KEY HERE

	def preprocess(self, data_path, model_size):
		if 'gs' in data_path: 
					data = pd.read_csv(data_path)
		else: 
			google.cloud.bigquery.Client()
			table = bigquery.TableReference.from_string(
    		"bigquery-public-data.utility_us.country_code_iso"
			)
			rows = bqclient.list_rows(
    			table,
    			selected_fields=[
        			bigquery.SchemaField("country_name", "STRING"),/
        			bigquery.SchemaField("fips_code", "STRING"),
    			],
			)
			data = rows.to_dataframe()

		# Split for Training and Testing
		msk = np.random.rand(len(data)) < 0.8
		train = data[msk]
		test = data[~msk]

		# Prepare for Cohere
		sentences_train = list(train.iloc[:,0].values)
		sentences_test = list(test.iloc[:,0].values)
		labels_train  = list(train.iloc[:,1].values)
		labels_test  = list(test.iloc[:,1].values)

		# embed sentences from both train and test set 
		embeddings_train = co.embed(model=model_size, texts=sentences_train).embeddings
		embeddings_test = co.embed(model=model_size, texts=sentences_test).embeddings

	def train(self):
		## Setup appropriate training pipeline / model selection. Currently setup for transformer model 
		model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
		history = model.fit(x_train, y_train, batch_size=32, epochs=2, validation_data=(x_val, y_val))


class RNNModel(object): 
'''RNN Model to use with Cohere embeddings'''
	def __init__(self, embeddings_matrix, hparams, labels):
    	self.embeddings_matrix = embeddings_matrix
    	self.hparams = hparams
    	self.labels = labels
    	self.num_labels = len(labels)

	def rnn_layer(self):
		sequence_length = self.hparams.sequence_length

    	I = Input(shape=(sequence_length,), dtype='float32')
    	E = Embedding(
        	self.hparams.vocab_size,
        	self.hparams.embedding_dim,
        	weights=[self.embeddings_matrix],
        	input_length=sequence_length,
        	trainable=self.hparams.train_embedding)(
            	I)
    	H = Bidirectional(GRU(128, return_sequences=True))(E)
    	A = TimeDistributed(
        	Dense(128, activation='relu'), input_shape=(sequence_length, 256))(
            	H)
    	A = TimeDistributed(Dense(1, activation='softmax'))(H)
    	X = Dot((1, 1))([H, A])
   		X = Flatten()(X)
    	X = Dense(128, activation='relu')(X)
    	X = Dropout(self.hparams.dropout_rate)(X)
    	Output = Dense(self.num_labels, activation='sigmoid')(X)

    	model = Model(inputs=I, outputs=Output)
    	model.compile(
        	optimizer='rmsprop',
        	loss='binary_crossentropy',
        	metrics=['accuracy', auc_roc])

    	print(model.summary())
    	return model


class CNNModel(object):
'''Text CNN Model to Use with Cohere Embeddings'''
	def init(self, **kwargs):
		self.key 


	## TODO - Data shapes need adjusting
	def cnn_layer(self):


		## Convolutional Layers
    	conv_0 = Conv1D(filter_nums, 1, kernel_initializer="normal", padding="valid", activation="relu")(drop)
    	conv_1 = Conv1D(filter_nums, 2, kernel_initializer="normal", padding="valid", activation="relu")(drop)
    	conv_2 = Conv1D(filter_nums, 3, kernel_initializer="normal", padding="valid", activation="relu")(drop)
    	conv_3 = Conv1D(filter_nums, 4, kernel_initializer="normal", padding="valid", activation="relu")(drop)

    	## Kmax pooling layers
    	maxpool_0 = KMaxPooling(k=3)(conv_0)
    	maxpool_1 = KMaxPooling(k=3)(conv_1)
    	maxpool_2 = KMaxPooling(k=3)(conv_2)
    	maxpool_3 = KMaxPooling(k=3)(conv_3)

    	## Merge and Dense Layers
    	merged_tensor = tf.keras.layers.concatenate([maxpool_0, maxpool_1, maxpool_2, maxpool_3], axis=1)
    	print(merged_tensor)
    	#output = Dropout(drop)(merged_tensor)
    	output = Dense(units=144, activation='relu')(merged_tensor)
    	output = Dense(units=1, activation='sigmoid')(output)
    	#dense = tf.keras.layers.Dense(256, activation='relu')(bert_output)
    	#pred = tf.keras.layers.Dense(1, activation='sigmoid')(dense)
    
    	model = tf.keras.models.Model(inputs=bert_inputs, outputs=output)
    	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    	model.summary()
    
    	return model

## TODO: Clean up - from text classification with keras transformers tutorial
class Transformer(object): 
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"), layers.Dense(embed_dim),]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


    def model(self):
    	inputs = layers.Input(shape=(maxlen,))
		embedding_layer = TokenAndPositionEmbedding(maxlen, vocab_size, embed_dim)
		x = embedding_layer(inputs)
		transformer_block = TransformerBlock(embed_dim, num_heads, ff_dim)
		x = transformer_block(x)
		x = layers.GlobalAveragePooling1D()(x)
		x = layers.Dropout(0.1)(x)
		x = layers.Dense(20, activation="relu")(x)
		x = layers.Dropout(0.1)(x)
		outputs = layers.Dense(2, activation="softmax")(x)

		model = keras.Model(inputs=inputs, outputs=outputs)

