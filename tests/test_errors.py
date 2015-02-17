import json
import os
import os.path
import re
import unittest

import six

from gherkin_parser import ParseError, parse_lines

class ParserTestCaseMixin(object):
    def parse(self, feature_string):
        return parse_lines(feature_string.split('\n'))

    def assertErrorMessage(self, feature_string, message):
        with self.assertRaises(ParseError) as cm:
            self.parse(feature_string)
        self.assertEqual(str(cm.exception), message)

class FeatureTagsTestCase(ParserTestCaseMixin, unittest.TestCase):
    def test_broken_tags(self):
        self.assertErrorMessage(u"""
            @tag broken tags
        """, "Tags must start with a '@' character, and not contain spaces (line 2)")

class FeatureTitleTestCase(ParserTestCaseMixin, unittest.TestCase):
    def test_empty_title(self):
        parsed = self.parse(u"""
            Feature:
        """)
        self.assertEqual(parsed['title']['content'], '')

    def test_missing_feature_title(self):
        self.assertErrorMessage(u"""
            Not a feature
        """, 'Expected feature title (line 2)')

    def test_multiple_feature_titles(self):
        self.assertErrorMessage(u"""
            Feature: Feature 1
                Scenario:
                    Given a given

            Feature: Feature 2
        """, "Unexpected {!r}. File must not contain multiple features (line 6)".format(six.text_type('Feature: Feature 2')))

class FeatureBackgroundTestCase(ParserTestCaseMixin, unittest.TestCase):
    def test_background_after_scenario(self):
        self.assertErrorMessage(u"""
            Feature:
                Scenario:

                Background:
                    Description 1
        """, "Unexpected {!r}. Background must not occur after scenarios (line 5)".format(six.text_type('Background:')))

class ScenarioTestCase(ParserTestCaseMixin, unittest.TestCase):
    def test_with_examples(self):
        self.assertErrorMessage(u"""
            Feature: Title
                Scenario: Title
                    Given I have a given

                    Examples:
        """, "Scenario block has examples section - should be 'scenario outline' (line 3)")

class ScenarioOutlineTestCase(ParserTestCaseMixin, unittest.TestCase):
    def test_without_examples(self):
        self.assertErrorMessage(u"""
            Feature: Title
                Scenario Outline: Title
                    Given I have a given
        """, "Scenario Outline block is missing an examples section (line 3)")
