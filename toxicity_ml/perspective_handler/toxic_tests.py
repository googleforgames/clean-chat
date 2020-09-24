from six import binary_type
from functools import reduce
import json
import requests

# Analyze the Toxicity of a Comment
class Perspective_Handler(object):
    ''' Takes a comment, queries the API, parses the JSON, returns a probability list'''

    # __init__ function
    def __init__(self, key):
      self.key = key
      self.url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze'
      self.tests = {'IDENTITY_ATTACK': {}, 'INSULT': {}, 'SEXUALLY_EXPLICIT': {}, 'TOXICITY': {}}
      self.testUsed = ['IDENTITY_ATTACK', 'INSULT', 'SEXUALLY_EXPLICIT', 'TOXICITY']

    # Analyze Comment via the Perspective API
    def analyze_comment(self, commentIn):
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
      baseDict = commentJson["attributeScores"]
      testsUsed = ['IDENTITY_ATTACK', 'INSULT', 'SEXUALLY_EXPLICIT', 'TOXICITY']
      probDict = [self.deep_get(baseDict, x) for x in testsUsed]
      probs = [probDict[i]['summaryScore']['value'] for i in range(4)] 
      return probs


# Combine Probailies of Multiple Comments
class monitor_toxicity:
    '''Combine Probailies of Multiple Comments'''
    def __init__(self):
        self.transition_probs = [.40,.30,.20,.10]

    # Calculate the total probability score 
    def calculate_tScore(self, probs):
      '''Conflation of the Individual Probability Scores '''
      pIdentity, pInsult, pSexual, pToxic = [probs[i] for i in range(4)]
      CombinedP = (pToxic * pIdentity * pInsult * pSexual) / ((pToxic * pIdentity * pInsult * pSexual) + ((1-pToxic)*(1-pIdentity)*(1-pInsult)*(1-pSexual)))
      return CombinedP

    # Calculate Current Score
    def calculate_score(self, cNum, iProb, nProb):
        'Calculate Probility of Sequential Comments Being Toxic'
        p = (iProb + nProb) - self.transition_probs[(cNum-1)]
        return p
