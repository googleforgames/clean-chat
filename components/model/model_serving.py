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

import requests
import tensorflow as tf
import json


## TODO: Change from REST to gRPC 
class server(object): 
    '''Model Serving Class'''
    def __init__(self, server_url):
        self.server_url = server_url

    def _bytes_feature(value):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

    def toxicity_prediction(model_server_url, text):
    
        if isinstance(text, (bytes, bytearray)):
            byte_str = text
        else:
            byte_str = text.encode('utf-8')
    
        example = tf.train.Example(features=tf.train.Features(feature={
            'comment_text': self._bytes_feature(byte_str)
        }))
    
        serialized_example = example.SerializeToString()
    
        json_data = {
                "signature_name":"serving_default",
                "instances":[
                    {
                    "examples":serialized_example
                    }
                ]
            }
        
        r = requests.post(model_server_url, json=json_data)
    
        if r.status_code == 200:
            return json.loads(r.content)['predictions'][0][0]
        else:
            return '[ ERROR ] {}. {}'.format(r.status_code, r.content)

