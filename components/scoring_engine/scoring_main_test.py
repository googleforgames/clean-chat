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

## TODO: Continually adding unit tests
## adding pubsub input test

import logging
import unittest
from hamcrest.core.core.allof import all_of

from apache_beam.testing.pipeline_verifiers import PipelineStateMatcher
from apache_beam.testing.test_pipeline import TestPipeline

import scoring_main

def dependencies():
  try:
      import apache_beam as beam
  except ImportError:
      beam = None
               return unittest.skip("Not online")

  @unittest.skipIf(beam is None, 'Beam is not installed')


class ScoringTest(unittest.TestCase):
  ''' Tests that scoring from Perspective is approximately as expected'''
  @unittest.dependencies()

  input_coll =   {
            'userid':    'theUser',
            'timestamp': '20210804 11:22:46.222708',
            'text':      'this is a test chat'
            }
  
  EXPECTED_OUPUT = ["score: 0.000161490573803"]

  def test_scoring(self):
    with TestPipeline() as p:

      input = p | beam.Create(input_coll)

      # Run Pipeline Scoring Element
      output = input | score_event()

      self.assertAlmostEqual(output['score'], EXPECTED_OUPUT, 7, 'Not Returning Correct Perspective Scores')


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  unittest.main()
