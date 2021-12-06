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
            'username':  'theUser',
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
