import json
import os
import os.path
import re
import unittest

from gherkin_parser import ParseError, parse_from_filename

ROOT = os.path.join(os.path.dirname(__file__))
FEATURE_ROOT = os.path.join(ROOT, 'features')
PARSED_FEATURE_ROOT = os.path.join(ROOT, 'parsed_features')

class ParserRegressionTestCase(unittest.TestCase):
    maxDiff = None

    def test_previously_parsed_features(self):
        for path, _, basenames in os.walk(FEATURE_ROOT):
            for basename in basenames:
                if not basename.endswith('.feature'):
                    continue

                feature_filename = os.path.join(path, basename)
                parsed = parse_from_filename(feature_filename)

                parsed_feature_filename = re.sub(r'\.feature$', '.json',
                    os.path.join(PARSED_FEATURE_ROOT, os.path.relpath(feature_filename, FEATURE_ROOT))
                )
                with open(parsed_feature_filename) as fp:
                    pre_parsed = json.load(fp)

                try:
                    self.assertEqual(
                        json.loads(json.dumps(parsed)),
                        pre_parsed
                    )
                except AssertionError as exc:
                    raise AssertionError('{}:\n\n{}'.format(feature_filename, exc))
