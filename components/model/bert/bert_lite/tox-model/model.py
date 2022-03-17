import os 

import numpy as np
import pandas as pd

import tensorflow as tf 
import tensorflow_hub as hub



class toxicity model():
  def init(self): 
    self.data_location = os.environ['GCS_PATH']

  def read_data(self):

    data = pd.read_csv(self.data_location)
    training_data = data.sample(frac=0.8, random_state=25)
    testing_data = data.drop(training_data.index)

    x_train = np.array(training_data['comment_text'])
    y_train = np.array(training_data['target'])

    x_test = np.array(testing_data['comment_text'])
    y_test = np.array(testing_data['target'])

    return x_train, y_train, x_test, y_test


  def create_model(self):

    bert_path = "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4"
    preprocess_path = 'https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3'

    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
    preprocessing_layer = hub.KerasLayer(preprocess_path, name='preprocessing')
    encoder_inputs = preprocessing_layer(text_input)
    encoder = hub.KerasLayer(bert_path, trainable=True, name='BERT_encoder')
    outputs = encoder(encoder_inputs)
    net = outputs['pooled_output']
    net = tf.keras.layers.Dropout(0.1)(net)
    net = tf.keras.layers.Dense(1, activation=None, name='classifier')(net)

    model =tf.keras.Model(text_input, net)

    optimizer = optimization.create_optimizer(init_lr=3e-5,
                                          num_train_steps=5,
                                          num_warmup_steps=int(0.1*5),
                                          optimizer_type='adamw')

    ## add optimizer, loss, etc in appropriate place
    model.compile(optimizer=optimizer,
                         loss=tf.keras.losses.MeanAbsoluteError(),
                         metrics=tf.metrics.MeanSquaredError())

    return model


if __name__ == "__main__": 


  model = toxicity_model()

  x_train, y_train, x_test, y_test = model.read_data()

  tox_model =  model.create_model()

  tox_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

  tf.keras.callbacks.EarlyStopping(monitor='loss', patience=2)

  history = model.fit(x=x_train, y=y_train, validation_split=0.2, epochs=epochs, callbacks=[early_stopping])

  model.save(os.environ['GCS_PATH'] + '/model')






