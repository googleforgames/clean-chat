###############################################################################
#
#   NOTE: This works when the TFX model is served from Docker, where 
#   the model name is "bert_model" or whatever is specified in the model_server_url
#   https://www.tensorflow.org/tfx/serving/docker
#
###############################################################################

import requests
import tensorflow as tf
import json

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def toxicity_prediction(model_server_url, text):
    
    if isinstance(text, (bytes, bytearray)):
        byte_str = text
    else:
        byte_str = text.encode('utf-8')
    
    example = tf.train.Example(features=tf.train.Features(feature={
        'comment_text': _bytes_feature(byte_str)
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


# Example: Call the function to get the prediction.
toxicity_prediction(model_server_url='http://localhost:8501/v1/models/bert_model:predict', text='I hate you, you suck at this game')
