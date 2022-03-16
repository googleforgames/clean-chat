
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

# A basic feedforward network designed to be a placeholder for more advanced toxicity models. 

from tf.keras.layers import Dense, Input, Dropout
from tf.keras.models import Model 
from tf.keras.optimizers import Adam
from tf.keras.losses import BinaryCrossentropy
from.keras.metrics import Accuracy
from tf.keras.callbacks import ModelCheckpoint

class Model(object):
	''' Basic Keras Model for Toxicity Classification. Used to demonstate appropriate use of classification layer. Not to be used in production''' 
	def init(self, **kwargs): 
		super(Model, self).__init__(*args, **kwargs)
        pass

	def model(embed_length): 
		embedded_input = tf.keras.Input(shape=(embed_length,), dtype="float32")
		net = tf.keras.layers.Dense(2000, activation=tf.keras.activations.relu)(embedded_input)
    	net = tf.keras.layers.Dropout(0.1)(net)
    	net = tf.keras.layers.Dense(500, activation=tf.keras.activations.relu)(embedded_input)
    	net = tf.keras.layers.Dropout(0.1)(net)
    	preds = tf.keras.layers.Dense(1, activation=tf.keras.activations.sigmoid, name='regression_layer')(net)
		model = Model(embedded_input, preds)
		model.compile(loss=tf.keras.losses.MeanAbsoluteError(),
                  optimizer=Adam(learning_rate=1e-3),
                  metrics=[tf.metrics.MeanSquaredError(), tf.keras.metrics.Accuracy()]
                  )
		return model 

	def fit(train_embeddings, labels_train, test_embeddings, labels_test, save_dir): 
		'''Fit Model, Save to GCS Bucket'''
		early_stop = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=2)
		checkpoint_filepath = '/tmp/checkpoint'
		model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
    		filepath=checkpoint_filepath,
    		save_weights_only=True,
    		monitor='val_accuracy',
    		mode='max',
    		save_best_only=True)

		self.model.fit(x=train_embeddings, y=labels_train, validation_split=0.2, epochs=200, callbacks=[early_stop, model_checkpoint])
		loss, accuracy = model.evaluate(test_embeddings, labels_test)
		print(f'Loss: {loss}')
		print(f'Accuracy: {accuracy}')
		self.model.save(save_dir)



