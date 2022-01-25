
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

class BasicModel(object):
	def init(self, **kwargs): 
		super(BasicModel, self).__init__(*args, **kwargs)
        pass

	def model(embed_length): 
		input = tf.keras.Input(shape=(embed_length,), dtype="float32")
		x = layers.Dropout(0.5)(x)
		x = layers.Dense(512, activation="relu")(x)
		x = layers.Dropout(0.5)(x)
		x = layers.Dense(256, activation="relu")(x)
		x = layers.Dropout(0.5)(x)
		predictions = layers.(Dense(120, activation='softmax')) 
		model = Model(input, predictions)
		model.compile(loss=BinaryCrossentropy(),
                  optimizer=Adam(learning_rate=1e-3),
                  metrics=Accuracy())
		return model 

	def fit(train_embeddings, labels_train): 
		## model + fit
		self.model.fit(train_embeddings, labels_train, batch_size=32, epochs=5, verbose=1, validation_split=0.1, shuffle=True)

		


