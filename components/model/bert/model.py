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
## Train the Full BERT  Keras 

from absl import logging
import tensorflow as tf
import tensorflow_transform as tft

from official.nlp import optimization

from tfx.experimental.templates.taxi.models import features
from tfx.experimental.templates.taxi.models.keras_model import constants
from tfx_bsl.public import tfxio


def _get_serve_tf_examples_fn(model, tf_transform_output):
    """Returns a function that parses a serialized tf.Example and applies TFT."""

    model.tft_layer = tf_transform_output.transform_features_layer()

    @tf.function
    def serve_tf_examples_fn(serialized_tf_examples):
        """Returns the output to be used in the serving signature."""
        feature_spec = tf_transform_output.raw_feature_spec()
        feature_spec.pop(_LABEL_KEY)
        parsed_features = tf.io.parse_example(serialized_tf_examples, feature_spec)

        transformed_features = model.tft_layer(parsed_features)

        outputs = model(transformed_features)
        return {'outputs': outputs}

    return serve_tf_examples_fn

def _input_fn(file_pattern: Text,
              tf_transform_output: tft.TFTransformOutput,
              batch_size: int = 32) -> tf.data.Dataset:
    """Generates features and label for tuning/training.
    Args:
      file_pattern: input tfrecord file pattern.
      tf_transform_output: A TFTransformOutput.
      batch_size: representing the number of consecutive elements of returned
        dataset to combine in a single batch
    Returns:
      A dataset that contains (features, indices) tuple where features is a
        dictionary of Tensors, and indices is a single Tensor of label indices.
    """
    transformed_feature_spec = (
        tf_transform_output.transformed_feature_spec().copy())

    dataset = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transformed_feature_spec,
        reader=_gzip_reader_fn,
        label_key=_LABEL_KEY)

    return dataset 

def toxicity_model():

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

# TFX Trainer will call this function.
def run_fn(fn_args):
    """Train the model based on given args.
    Args:
      fn_args: Holds args used to train the model as name/value pairs.
    """
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)

    train_dataset = _input_fn(fn_args.train_files, tf_transform_output, 32)
    eval_dataset = _input_fn(fn_args.eval_files, tf_transform_output, 32)

    mirrored_strategy = tf.distribute.MirroredStrategy()
    with mirrored_strategy.scope():
        model = toxicity_model()

    # Write logs to path
    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=fn_args.model_run_dir, update_freq='batch')

    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps, 
        callbacks=[tensorboard_callback])

    ## TODO: Update model serving signiture?
    signatures = {
        'antidote-serving':
            _get_serve_tf_examples_fn(model,
                                      tf_transform_output).get_concrete_function(
                                          tf.TensorSpec(
                                              shape=[None],
                                              dtype=tf.string,
                                              name='examples')),
    }
    model.save(fn_args.serving_model_dir, save_format='tf', signatures=signatures)
