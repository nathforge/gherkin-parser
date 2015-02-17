#!/usr/bin/env python

import os.path
import sys

from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

setup(
    version='0.1',
    url='https://github.com/nathforge/gherkin-parser',
    name='gherkin_parser',
    description='Gherkin BDD feature file parser. Compatible with Cucumber.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    packages=['gherkin_parser'],
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=['six'],
    tests_require=['jsonschema==2.4.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ]
)
