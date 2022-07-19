##########################################################################
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
##########################################################################
"""Train the Full BERT Model with Keras"""

from typing import Any, Callable

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_transform as tft
from keras.models import Model
from official.nlp import optimization
from tfx import v1 as tfx

LABEL = 'label'


# https://github.com/tensorflow/tfx/blob/master/tfx/examples/chicago_taxi_pipeline/taxi_utils_native_keras.py
# Apache License, Version 2.0. | Copyright 2019 Google LLC.
def _get_tf_examples_serving_signature(
        model: Model, tf_transform_output: tft.TFTransformOutput) -> Callable:
    """Returns a serving signature that accepts `tensorflow.Example`."""

    # We need to track the layers in the model in order to save it.
    # TODO(b/162357359): Revise once the bug is resolved.
    model.tft_layer_inference = tf_transform_output.transform_features_layer()

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None], dtype=tf.string, name='examples')
    ])
    def serve_tf_examples_fn(serialized_tf_example):
        """Returns the output to be used in the serving signature."""
        raw_feature_spec = tf_transform_output.raw_feature_spec()
        # Remove label feature since these will not be present at serving time.
        raw_feature_spec.pop('target')
        raw_features = tf.io.parse_example(serialized_tf_example,
                                           raw_feature_spec)
        transformed_features = model.tft_layer_inference(raw_features)

        outputs = model(transformed_features)
        # TODO(b/154085620): Convert the predicted labels from the model using a
        # reverse-lookup (opposite of transform.py).
        return {'outputs': outputs}

    return serve_tf_examples_fn


# https://github.com/tensorflow/tfx/blob/master/tfx/examples/chicago_taxi_pipeline/taxi_utils_native_keras.py
# Apache License, Version 2.0. | Copyright 2019 Google LLC.
def _get_transform_features_signature(
        model: Model, tf_transform_output: tft.TFTransformOutput) -> Callable:
    """Returns a serving signature that applies tf.Transform to features."""

    # We need to track the layers in the model in order to save it.
    # TODO(b/162357359): Revise once the bug is resolved.
    model.tft_layer_eval = tf_transform_output.transform_features_layer()

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[None], dtype=tf.string, name='examples')
    ])
    def transform_features_fn(serialized_tf_example):
        """Returns the transformed_features to be fed as input to evaluator."""
        raw_feature_spec = tf_transform_output.raw_feature_spec()
        raw_features = tf.io.parse_example(serialized_tf_example,
                                           raw_feature_spec)
        transformed_features = model.tft_layer_eval(raw_features)
        return transformed_features

    return transform_features_fn


# https://github.com/kubeflow/pipelines/blob/master/samples/core/tfx-oss/utils/taxi_utils.py
# Apache License, Version 2.0. | Copyright 2019 The Kubeflow Authors.
def _gzip_reader_fn(filenames: tf.string) -> tf.data.TFRecordDataset:
    """Small utility returning a record reader that can read gzip'ed files."""
    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')


def _input_fn(
    file_pattern: Any,
    tf_transform_output: tft.TFTransformOutput,
    batch_size: int = 32,
) -> tf.data.Dataset:
    """Generates features and label for tuning/training.

    Args:
        file_pattern (Any): file patterns for training/evalluating fn_args
        tf_transform_output (tft.TFTransformOutput): the output of the tf.Transform
        batch_size (int, optional): Batch size for train/eval. Defaults to 32.

    Returns:
        tf.data.Dataset: Represents data.
    """

    transformed_feature_spec = (
        tf_transform_output.transformed_feature_spec().copy())

    dataset = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transformed_feature_spec,
        reader=_gzip_reader_fn,
        label_key=LABEL)

    return dataset


def toxicity_model() -> Model:
    """Toxicity BERT Model

    Returns:
        keras.models.Model: BERT Model
    """
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

    model = tf.keras.Model(text_input, net)

    optimizer = optimization.create_optimizer(init_lr=3e-5,
                                              num_train_steps=5,
                                              num_warmup_steps=int(0.1 * 5),
                                              optimizer_type='adamw')

    # add optimizer, loss, etc in appropriate place
    model.compile(optimizer=optimizer,
                  loss=tf.keras.losses.MeanAbsoluteError(),
                  metrics=tf.metrics.MeanSquaredError())

    return model


def run_fn(fn_args: tfx.components.FnArgs) -> None:
    """Train the model based on given args.
    Args:
      fn_args: Holds args used to train the model as name/value pairs.
    """
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)

    train_dataset = _input_fn(file_pattern=fn_args.train_files,
                              tf_transform_output=tf_transform_output,
                              batch_size=32)

    eval_dataset = _input_fn(file_pattern=fn_args.eval_files,
                             tf_transform_output=tf_transform_output,
                             batch_size=32)

    model = toxicity_model()

    # Write logs to path
    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=fn_args.model_run_dir, update_freq='batch')

    model.fit(train_dataset,
              steps_per_epoch=fn_args.train_steps,
              validation_data=eval_dataset,
              validation_steps=fn_args.eval_steps,
              callbacks=[tensorboard_callback])

    signatures = {
        'serving_default':
            _get_tf_examples_serving_signature(model, tf_transform_output),
        'transform_features':
            _get_transform_features_signature(model, tf_transform_output),
    }

    model.save(fn_args.serving_model_dir,
               save_format='tf',
               signatures=signatures)
