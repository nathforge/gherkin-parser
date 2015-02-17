#!/usr/bin/env python

import collections
import json
import os
import os.path
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from gherkin_parser import ParseError, parse_from_filename

ROOT = os.path.join(os.path.dirname(__file__), '..')
FEATURE_ROOT = os.path.join(ROOT, 'features')
PARSED_FEATURE_ROOT = os.path.join(ROOT, 'parsed_features')

def main():
    try:
        shutil.rmtree(PARSED_FEATURE_ROOT)
    except OSError:
        if os.path.isdir(PARSED_FEATURE_ROOT):
            raise

    has_errors = False
    for path, _, basenames in os.walk(FEATURE_ROOT):
        for basename in basenames:
            if basename.endswith('.feature'):
                feature_filename = os.path.join(path, basename)

                parsed_feature_filename = re.sub(r'\.feature$', '.json',
                    os.path.join(PARSED_FEATURE_ROOT, os.path.relpath(feature_filename, FEATURE_ROOT))
                )

                try:
                    os.makedirs(os.path.dirname(parsed_feature_filename))
                except OSError:
                    if not os.path.isdir(os.path.dirname(parsed_feature_filename)):
                        raise

                try:
                    parsed = parse_from_filename(feature_filename, dict_cls=collections.OrderedDict)
                except ParseError as exc:
                    print >>sys.stderr, '{} of {}'.format(exc, feature_filename)
                    has_errors = True
                else:
                    open(parsed_feature_filename, 'w').write(json.dumps(parsed, indent=4))

    if has_errors:
        exit(1)

if __name__ == '__main__':
    main()
