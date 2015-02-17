import json
import os
import os.path
import sys
import unittest

import jsonschema

from gherkin_parser import ParseError, parse_from_filename

ROOT = os.path.join(os.path.dirname(__file__))
FEATURE_ROOT = os.path.join(ROOT, 'features')

SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    '$ref': '#/definitions/feature',
    'definitions': {
        'feature': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'language',
                'tags',
                'title',
                'description',
                'background',
                'scenarios'
            ],
            'properties': {
                'language': {
                    '$ref': '#/definitions/language'
                },
                'tags': {
                    '$ref': '#/definitions/tags'
                },
                'title': {
                    '$ref': '#/definitions/title'
                },
                'description': {
                    '$ref': '#/definitions/description'
                },
                'background': {
                    '$ref': '#/definitions/background'
                },
                'scenarios': {
                    '$ref': '#/definitions/scenarios'
                }
            }
        },
        'language': {
            'anyOf': [
                {
                    'type': 'null'
                },
                {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'index',
                        'content'
                    ],
                    'properties': {
                        'index': {
                            '$ref': '#/definitions/index'
                        },
                        'content': {
                            'type': 'string'
                        }
                    }
                }
            ]
        },
        'tags': {
            'anyOf': [
                {
                    'type': 'null'
                },
                {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'index',
                        'content'
                    ],
                    'properties': {
                        'index': {
                            '$ref': '#/definitions/index'
                        },
                        'content': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        }
                    }
                }
            ]
        },
        'title': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'index',
                'content'
            ],
            'properties': {
                'index': {
                    '$ref': '#/definitions/index'
                },
                'content': {
                    'type': 'string'
                }
            }
        },
        'description': {
            'anyOf': [
                {
                    'type': 'null'
                },
                {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'index',
                        'content'
                    ],
                    'properties': {
                        'index': {
                            '$ref': '#/definitions/index'
                        },
                        'content': {
                            'type': 'string'
                        }
                    }
                }
            ]
        },
        'background': {
            'anyOf': [
                {
                    'type': 'null'
                },
                {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'title',
                        'description',
                        'steps'
                    ],
                    'properties': {
                        'title': {
                            '$ref': '#/definitions/title'
                        },
                        'description': {
                            '$ref': '#/definitions/description'
                        },
                        'steps': {
                            '$ref': '#/definitions/steps'
                        }
                    }
                }
            ]
        },
        'steps': {
            'type': 'array',
            'items': {
                '$ref': '#/definitions/step'
            }
        },
        'step': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'title',
                'table',
                'text'
            ],
            'properties': {
                'title': {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'index',
                        'clause',
                        'content'
                    ],
                    'properties': {
                        'index': {
                            '$ref': '#/definitions/index'
                        },
                        'clause': {
                            'enum': [
                                'given',
                                'when',
                                'then'
                            ]
                        },
                        'content': {
                            'type': 'string'
                        }
                    }
                },
                'table': {
                    'oneOf': [
                        {
                            'type': 'null'
                        },
                        {
                            '$ref': '#/definitions/table'
                        }
                    ]
                },
                'text': {
                    'anyOf': [
                        {
                            'type': 'null'
                        },
                        {
                            'type': 'object',
                            'additionalProperties': False,
                            'required': [
                                'index',
                                'content'
                            ],
                            'properties': {
                                'index': {
                                    '$ref': '#/definitions/index'
                                },
                                'content': {
                                    'type': 'string'
                                }
                            }
                        }
                    ]
                }
            }
        },
        'table': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': [
                    'index',
                    'columns'
                ],
                'properties': {
                    'index': {
                        '$ref': '#/definitions/index'
                    },
                    'columns': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    }
                }
            }
        },
        'scenarios': {
            'type': 'array',
            'items': {
                '$ref': '#/definitions/scenario'
            }
        },
        'scenario': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'tags',
                'title',
                'description',
                'steps'
            ],
            'properties': {
                'tags': {
                    '$ref': '#/definitions/tags'
                },
                'title': {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [
                        'index',
                        'content'
                    ],
                    'properties': {
                        'index': {
                            '$ref': '#/definitions/index'
                        },
                        'is_outline': {
                            'type': 'boolean'
                        },
                        'content': {
                            'type': 'string'
                        }
                    }
                },
                'description': {
                    '$ref': '#/definitions/description'
                },
                'examples': {
                    'oneOf': [
                        {
                            'type': 'null'
                        },
                        {
                            '$ref': '#/definitions/examples'
                        }
                    ]
                },
                'steps': {
                    '$ref': '#/definitions/steps'
                }
            }
        },
        'examples': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'title',
                'table'
            ],
            'properties': {
                'title': {
                    '$ref': '#/definitions/title'
                },
                'table': {
                    '$ref': '#/definitions/table'
                }
            }
        },
        'index': {
            'type': 'integer',
            'minimum': 0
        }
    }
}

class ParserFormatTestCase(unittest.TestCase):
    maxDiff = None

    def test_features_against_schema(self):
        for path, _, basenames in os.walk(FEATURE_ROOT):
            for basename in basenames:
                if not basename.endswith('.feature'):
                    continue

                feature_filename = os.path.join(path, basename)
                parsed = parse_from_filename(feature_filename)

                try:
                    jsonschema.validate(parsed, SCHEMA)
                except jsonschema.ValidationError:
                    sys.stderr.write('{}\n'.format(feature_filename))
                    raise
