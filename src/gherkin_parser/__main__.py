"""
Main command. Reads a feature file from stdin, outputs it as parsed JSON.
"""

import codecs
import json
import sys

from gherkin_parser import parse_file

with codecs.getreader('utf8')(sys.stdin) as fp:
    print json.dumps(parse_file(fp), indent=4)
