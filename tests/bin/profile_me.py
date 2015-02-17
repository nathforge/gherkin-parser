#!/usr/bin/env python

"""
Walks through the feature directory and parse all files.

This is intended to be a profileable script.
"""

import os
import os.path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from gherkin_parser import parse_from_filename

ROOT = os.path.join(os.path.dirname(__file__), '..')
FEATURE_ROOT = os.path.join(ROOT, 'features')

def main():
    feature_filenames = []
    for path, _, basenames in os.walk(FEATURE_ROOT):
        for basename in basenames:
            if basename.endswith('.feature'):
                feature_filename = os.path.join(path, basename)
                parse_from_filename(feature_filename)

if __name__ == '__main__':
    main()
