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
# Copyright 2021 Google LLC
"""Perform BERT text pre-processing"""

import tensorflow as tf


def preprocessing_fn(inputs) -> dict:
    """default preprocessing function

    Args:
        inputs (dict): explanatory variables and objective variable

    Returns:
        dict: variables changed the key for BERT
    """

    inputs['comment_text'] = tf.strings.lower(inputs['comment_text'])

    return {'text': inputs['comment_text'], 'label': inputs['target']}
