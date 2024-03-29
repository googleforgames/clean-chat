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

'''
NOTE: The code contained within this script is intended
for demo/example purposes, and uses the Perspective API.
https://www.perspectiveapi.com/

If you choose to use the Perspective API, follow these steps:
https://developers.perspectiveapi.com/s/docs-get-started

For best results, this script should be updated with your
own machine learning model and/or business logic. The 
model may leverage a Google Partner, such as Cohere, or 
a custom trained model in scikit-learn, tensorflow/keras, 
pytorch, rule-based logic, or a hybrid of those.

IMPORTANT: In order for the model to be deployed as part of 
the framework, this script must have the following input and output:

Input:
    name: text
    type: string
    desc: text string representing a chat message
Output:
    name: score_payload
    type: dict (json object)
    desc: Must contain a key called "score", which contains the toxicity score, ranging from -1 (toxic) to 1 (positive)
          Any additional json key-value pairs are acceptable as well, but it is required to have at least one key called "score".
'''

import unittest
import json
import os
import requests
from six import binary_type
from functools import reduce

class Perspective_Handler(object):
    '''Analyse the Toxicity of a Comment'''
    # __init__ function
    def __init__(self, key):
        self.key = key
        self.url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze'
        self.tests = {'IDENTITY_ATTACK': {}, 'INSULT': {}, 'SEXUALLY_EXPLICIT': {}}
        self.testUsed = ['IDENTITY_ATTACK', 'INSULT', 'SEXUALLY_EXPLICIT']
    
    def analyze_comment(self, commentIn):
        ''' Function to Analyze Comment via the Perspective API'''
        if self.key is None:
            raise ValueError("Perspective API Key Missing")
        else:
            apiKey = {"key": self.key}
        
        # Construct dictionary from coment to send to API
        comment_dict = {"comment": {"text": commentIn}, "requestedAttributes": {}}
        for test in self.tests.keys():
            comment_dict["requestedAttributes"][test] = self.tests[test]
        
        # Send dictionary encoded JSON
        commentRequest = json.dumps(comment_dict)
        headers = {'content-type': "application/json"}
        keyDict = {"key": self.key}
        response = requests.post(self.url, data=commentRequest, headers=headers,params=keyDict)
        commentJson = response.json()
        return commentJson
    
    # Parse through returned Json dictionary
    def deep_get(self, dictionary, keys, default=None):
        return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)
    
    # Parse Returned Json
    def parse_json(self, commentJson):
        if 'attributeScores' in commentJson:
            baseDict = commentJson["attributeScores"]
            probDict = [self.deep_get(baseDict, x) for x in self.testUsed]
            probs = [probDict[i]['summaryScore']['value'] for i in range(len(self.testUsed))] 
            return probs
        else:
            print('[ WARNING ] commentJson does not contain attributeScores')
            return [0.0 for item in self.testUsed]

# Combine Probailies of Multiple Comments
class monitor_toxicity:
    '''Combine Probailies of Multiple Comments'''
    def __init__(self):
        self.transition_probs = [.90,.93,.95,.97,.99]
        self.testUsed = ['IDENTITY_ATTACK', 'INSULT', 'SEXUALLY_EXPLICIT']
    
    # Calculate the total probability score 
    def calculate_tScore(self, probs):
        '''Conflation of the Individual Probability Scores '''
        AllP = {self.testUsed[i]:probs[i] for i in range(len(self.testUsed))}
        pIdentity, pInsult, pSexual = [probs[i] for i in range(len(self.testUsed))]
        CombinedP = (pIdentity * pInsult * pSexual) / ((pIdentity * pInsult * pSexual) + ((1-pIdentity)*(1-pInsult)*(1-pSexual)))
        return CombinedP, AllP
    
    # Calculate Current Score
    def calculate_score(self, cNum, iProb, nProb):
        'Calculate Probility of Sequential Comments Being Toxic'
        p = (iProb + nProb) - self.transition_probs[(cNum-1)]
        return p

def model(text, key):
    '''Run Toxicity Scoring'''
    
    toxicP = Perspective_Handler(key)
    monitorT = monitor_toxicity()
    
    # Returns the analyzed comment from the Perspective API
    comment = toxicP.analyze_comment(text)
    # Parse through the Json Dictionaries 
    probs = toxicP.parse_json(comment)
    
    # Calculate Total Probability from Perspective Scores
    # This score (p) is weighted between three categories   
    # Conflated probability from an individual comment
    p, pdetail = monitorT.calculate_tScore(probs)
    
    if isinstance(p, float):                                                       
        score_payload = {
            'score':  p,
            'detail': pdetail
        }
    
    return score_payload
