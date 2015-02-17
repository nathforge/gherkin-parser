import abc
import codecs
import collections
import re
import textwrap

import six

from gherkin_parser.exceptions import ParseError, RecoverableParseError

Line = collections.namedtuple('Line', ('index', 'content'))

def parse_from_filename(filename, dict_cls=dict):
    """
    Parse a named file.
    """

    with codecs.open(filename, encoding='utf8') as fp:
        return parse_file(fp, dict_cls=dict_cls)

def parse_file(fp, dict_cls=dict):
    """
    Parse a file. File must return unicode data.
    """

    return parse_lines(fp, dict_cls=dict_cls)

def parse_lines(strings, dict_cls=dict):
    """
    Parse a list of lines.
    """

    def test_line_match(parser, line):
        try:
            parser(context, 0, [line])
        except ParseError:
            return False
        else:
            return True

    lines = lines_from_strings(strings)

    context = {
        'comment_cache': {},
        'dict_cls': dict_cls
    }

    # Parse the lines.
    line_index, result = feature_parser(context, 0, lines)

    # Do we have any unparsed lines?
    if line_index < len(lines) - 1:
        line = lines[line_index]

        if 'title' in result:
            if test_line_match(background_title_parser, line) and result['scenarios']:
                raise ParseError(
                    'Unexpected {!r}. Background must not occur after scenarios'.format(line.content.strip()),
                    line_index=line.index
                )

            if test_line_match(feature_title_parser, line):
                raise ParseError(
                    'Unexpected {!r}. File must not contain multiple features'.format(line.content.strip()),
                    line_index=line.index
                )

        raise ParseError(
            'Unexpected {!r}'.format(line.content.strip()),
            line_index=line.index
        )

    return result

def lines_from_strings(strings):
    lines = []
    for index, string in enumerate(strings):
        if not isinstance(string, six.text_type):
            raise ValueError('Line must be {}, not {}'.format(
                six.text_type.__name__, type(string).__name__
            ))
        lines.append(Line(index, string))

    return tuple(lines)

def indent(text, prefix):
    return '\n'.join(
        '{}{}'.format(prefix, line)
        for line in text.split('\n')
    )

class Parser(object):
    def __init__(self, title=None, consume_blank_lines_after=True, remove_comment=True):
        if title:
            self._title = title
        elif getattr(self, '_title', None) is None:
            self._title = self._get_default_title()

        self._consume_blank_lines_after = consume_blank_lines_after
        self._remove_comment = remove_comment

        self._post_parse_funcs = []

    def __str__(self):
        return self._title

    def __call__(self, context, line_index, lines):
        start_line_index = line_index

        try:
            line_index, result = self._parse(context, line_index, lines)

            for func in self._post_parse_funcs:
                result = func(context, result)

            if self._consume_blank_lines_after:
                line_index = self._consume_blank_lines(context, line_index, lines)
        except ParseError as exc:
            if exc.line_index is None:
                if start_line_index:
                    exc.line_index = start_line_index

            raise

        return (line_index, result)

    def post_parse(self, func):
        self._post_parse_funcs.append(func)

    def _parse(self, context, line_index, lines):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_default_title(self):
        raise NotImplementedError

    def _parse_error(self, title=None, recoverable=False):
        if title is None:
            title = self._title

        message = 'Expected {}'.format(title)

        if recoverable:
            return RecoverableParseError(message)
        else:
            return ParseError(message)

    def _next_line(self, context, line_index, lines, remove_comment=None):
        if line_index >= len(lines):
            raise self._parse_error(recoverable=True)

        if remove_comment is None:
            remove_comment = self._remove_comment

        line = lines[line_index]

        if remove_comment:
            if line_index not in context['comment_cache']:
                context['comment_cache'][line_index] = self._strip_comment(line)
            line = context['comment_cache'][line_index]

        line_index += 1

        return (line_index, line)

    def _consume_blank_lines(self, context, line_index, lines):
        while True:
            try:
                line_index, line = self._next_line(context, line_index, lines, remove_comment=True)
            except RecoverableParseError:
                break

            if line.content.strip() != '':
                line_index -= 1
                break

        return line_index

    def _strip_comment(self, line):
        """
        Strip out the comment from a line.

        Allows escaping of '#' characters.
        """

        if '#' not in line.content:
            return line
        else:
            chars = []
            escaped = False
            for char in line.content:
                if char == '\\' and not escaped:
                    escaped = True
                    continue

                if char == '#' and not escaped:
                    break

                if escaped:
                    chars.append('\\')

                chars.append(char)

                if escaped:
                    escaped = False

            content = ''.join(chars)

            return Line(line.index, content)

class AnyOf(Parser):
    def __init__(self, parser_list, *args, **kwargs):
        self._parser_list = parser_list
        super(AnyOf, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        for parser in self._parser_list:
            try:
                return parser(context, line_index, lines)
            except RecoverableParseError:
                pass

        raise self._parse_error(recoverable=True)

    def _get_default_title(self):
        return 'any of (\n{}\n)'.format(
            '\n'.join(
                indent('({})'.format(parser), '    ')
                for parser in self._parser_list
            )
        )

class Dict(Parser):
    def __init__(self, parser_dict, *args, **kwargs):
        self._parser_dict = parser_dict
        super(Dict, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        result_dict = context['dict_cls']()
        for key, parser in self._parser_dict:
            line_index, result = parser(context, line_index, lines)
            result_dict[key] = result
        return (line_index, result_dict)

    def _get_default_title(self):
        return 'dict (\n{}\n)'.format(
            '\n'.join(
                indent('{}=({})'.format(key, parser), '    ')
                for key, parser in self._parser_dict
            )
        )

class FlattenLists(Parser):
    def __init__(self, parser, key, *args, **kwargs):
        self._parser = parser
        self._key = key
        super(FlattenLists, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        line_tuples, result = self._parser(context, line_index, lines)
        if not result:
            return (line_tuples, None)

        flattened = []
        for sub_result in result:
            flattened.extend(sub_result[self._key])

        return (line_tuples, context['dict_cls']((
            ('index', result[0]['index']),
            (self._key, flattened),
        )))

    def _get_default_title(self):
        return 'flatten lists ({})'.format(self._parser)

class MultipleOf(Parser):
    def __init__(self, parser, min_count=0, max_count=None, *args, **kwargs):
        self._parser = parser
        self._min_count = min_count
        self._max_count = max_count
        super(MultipleOf, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        result_list = []
        while True:
            if self._max_count is not None and len(result_list) > self._max_count:
                raise self._parse_error(recoverable=True)

            try:
                line_index, result = self._parser(context, line_index, lines)
            except RecoverableParseError as exc:
                break

            result_list.append(result)

        if len(result_list) < self._min_count:
            raise self._parse_error(recoverable=True)

        return (line_index, result_list)

    def _get_default_title(self):
        if self._max_count is not None:
            return '{}-{} of ({})'.format(self._min_count, self._max_count, self._parser)
        elif self._min_count > 0:
            return '{} or more of ({})'.format(self._min_count, self._parser)
        else:
            return 'multiple of ({})'.format(self._parser)

class Optional(MultipleOf):

    def __init__(self, parser, *args, **kwargs):
        super(Optional, self).__init__(parser, min_count=1, max_count=1, *args, **kwargs)

    def _parse(self, context, line_index, lines):
        try:
            line_index, result = super(Optional, self)._parse(context, line_index, lines)
        except RecoverableParseError:
            return (line_index, None)
        else:
            return (line_index, result[0])

    def _get_default_title(self):
        return 'optional ({})'.format(self._parser)

class Regex(Parser):
    def __init__(self, pattern, *args, **kwargs):
        self._regex = re.compile(pattern)
        super(Regex, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        line_index, line = self._next_line(context, line_index, lines)

        match = self._regex.search(line.content)
        if not match:
            raise self._parse_error(recoverable=True)

        result = context['dict_cls'](match.groupdict())
        result['index'] = line.index

        return (line_index, result)

    def _get_default_title(self):
        return 'string matching regex {!r}'.format(self._regex.pattern)

class SingleLineIfNot(Parser):
    def __init__(self, parser, remove_comment=True):
        self._parser = parser
        super(SingleLineIfNot, self).__init__(consume_blank_lines_after=False, remove_comment=remove_comment)

    def _parse(self, context, line_index, lines):
        try:
            self._parser(context, line_index, lines)
        except RecoverableParseError:
            line_index, line = self._next_line(context, line_index, lines)
            return (line_index, {
                'index': line.index,
                'line': line.content
            })
        else:
            raise self._parse_error(recoverable=True)

    def _get_default_title(self):
        return 'single line if not ({})'.format(self._parser)

class BlockTitle(Parser):
    def __init__(self, block_title_parser, block_types, block_type_title, store_type=False, title=None):
        self._block_title_parser = block_title_parser
        self._block_types = block_types
        self._block_type_title = block_type_title
        self._store_type = store_type
        super(BlockTitle, self).__init__(title, consume_blank_lines_after=False)

    def _parse(self, context, line_index, lines):
        try:
            line_index, result = self._block_title_parser(context, line_index, lines)
        except ParseError:
            raise self._parse_error(recoverable=True)
        result['type'] = result['type'].lower()
        if result['type'] not in self._block_types:
            raise self._parse_error(recoverable=True)
        if not self._store_type:
            del result['type']
        return (line_index, result)

    def _get_default_title(self):
        return '{} title'.format(self._block_type_title)

class Description(Parser):
    def __init__(self, parser, *args, **kwargs):
        self._parser = parser
        super(Description, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        line_index, result = self._parser(context, line_index, lines)
        if not result:
            return (line_index, None)
        else:
            content = textwrap.dedent('\n'.join(
                sub_result['line'].rstrip()
                for sub_result in result
            )).rstrip()

            return (line_index, context['dict_cls']((
                ('index', result[0]['index']),
                ('content', content),
            )))

    def _get_default_title(self):
        return 'description from ({})'.format(self._parser)

class FirstStepTitle(Parser):
    def __init__(self, step_parser, title=None):
        self._step_parser = step_parser
        self._clauses = ['given', 'when', 'then']
        super(FirstStepTitle, self).__init__(title, consume_blank_lines_after=False, remove_comment=False)

    def _parse(self, context, line_index, lines):
        line_index, result = self._step_parser(context, line_index, lines)
        result['clause'] = result['clause'].lower()
        if result['clause'] not in self._clauses:
            raise self._parse_error(title='{}, not {!r}'.format(self._title, result['clause']), recoverable=True)
        return (line_index, result)

    def _get_default_title(self):
        return '{}'.format('/'.join(self._clauses))

class OptionalLanguage(Parser):
    def __init__(self):
        self._regex = re.compile(r'(?i)^\s*#\s*language\s*:\s*(?P<code>\S+)\s*$')
        super(OptionalLanguage, self).__init__(remove_comment=False)

    def _parse(self, context, line_index, lines):
        try:
            line_index, language, language_line = self._parse_language(context, line_index, lines)
        except RecoverableParseError:
            return (0, None)

        return (line_index, context['dict_cls']((
            ('index', language_line.index),
            ('content', language),
        )))

    def _parse_language(self, context, line_index, lines):
        while True:
            line_index, line = self._next_line(context, line_index, lines)
            if line.content.strip() == '':
                continue

            match = self._regex.search(line.content)
            if not match:
                raise self._parse_error(recoverable=True)

            language = match.group('code')
            language_line = line

            return (line_index, language, language_line)

    def _get_default_title(self):
        return 'optional language comment'

class TableRow(Parser):
    def __init__(self):
        super(TableRow, self).__init__(remove_comment=False)

    def _parse(self, context, line_index, lines):
        line_index, line = self._next_line(context, line_index, lines)

        content = line.content.strip()
        if not content.startswith('|') or not content.endswith('|'):
            raise self._parse_error(recoverable=True)

        columns = []
        column_chars = []
        escaped = False
        unescaped_backslash = False
        for char in content[1:]:
            unescaped_backslash = False

            if char == '\\' and not escaped:
                escaped = True
                continue

            if char == '|' and not escaped:
                columns.append(''.join(column_chars).strip())
                column_chars = []
            else:
                column_chars.append(char)

            if escaped:
                escaped = False
                unescaped_backslash = True

        if unescaped_backslash:
            raise ParseError('Unescaped backslash at end of table row')

        return (line_index, context['dict_cls']((
            ('index', line.index),
            ('columns', columns),
        )))

    def _get_default_title(self):
        return 'table row'

class Tags(Parser):
    def __init__(self, tag_prefix_parser, *args, **kwargs):
        self.tag_prefix_parser = tag_prefix_parser
        super(Tags, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        line_index, result = self.tag_prefix_parser(context, line_index, lines)

        tags = result['tags_str'].split()
        if not all(tag.startswith('@') for tag in tags):
            raise ParseError('Tags must start with a \'@\' character, and not contain spaces')
        tags = [tag[1:] for tag in tags]

        return (line_index, context['dict_cls']((
            ('index', result['index']),
            ('content', tags)
        )))

    def _get_default_title(self):
        return 'tags'

class TextBlock(Parser):
    def __init__(self, delimiter, *args, **kwargs):
        self._delimiter = delimiter
        kwargs['remove_comment'] = False
        super(TextBlock, self).__init__(*args, **kwargs)

    def _parse(self, context, line_index, lines):
        if len(lines) < 2:
            raise self._parse_error(recoverable=True)

        line_index, line = self._next_line(context, line_index, lines)

        if line.content.strip() != self._delimiter:
            raise self._parse_error(recoverable=True)

        first_line_index = line.index
        line_contents = []
        while True:
            line_index, line = self._next_line(context, line_index, lines)

            if line.content.strip() == self._delimiter:
                break
            else:
                line_contents.append(line.content)

        text = textwrap.dedent('\n'.join(
            line_content.rstrip()
            for line_content in line_contents
        ))

        return (line_index, context['dict_cls']((
            ('index', first_line_index),
            ('text', text),
        )))

    def _get_default_title(self):
        return 'text block delimited by {}'.format(self._delimiter)

block_title_parser = Regex(r'(?i)^\s*(?P<type>feature|background|scenario|scenario outline|examples)\s*:\s*(?P<content>.*?)\s*$', remove_comment=False)
tag_prefix_parser = Regex(r'^\s*(?P<tags_str>@.*?)\s*$')
tags_parser = Tags(tag_prefix_parser)
optional_multiline_tags_parser = FlattenLists(MultipleOf(tags_parser), 'content')

feature_title_parser = BlockTitle(block_title_parser, ['feature'], 'feature')
background_title_parser = BlockTitle(block_title_parser, ['background'], 'background')
scenario_title_parser = BlockTitle(block_title_parser, ['scenario', 'scenario outline'], 'scenario', store_type=True)
examples_title_parser = BlockTitle(block_title_parser, ['examples'], 'examples')

step_title_parser = Regex(r'(?i)^\s*(?P<clause>given|when|then|and|but)\s+(?P<content>.*?)\s*$')
first_step_title_parser = FirstStepTitle(step_title_parser)

feature_description_parser = Description(MultipleOf(SingleLineIfNot(AnyOf([
    tag_prefix_parser,
    background_title_parser,
    scenario_title_parser
]))))

background_description_parser = Description(MultipleOf(SingleLineIfNot(AnyOf([
    tag_prefix_parser,
    scenario_title_parser,
    first_step_title_parser
]))))

scenario_description_parser = Description(MultipleOf(SingleLineIfNot(AnyOf([
    tag_prefix_parser,
    background_title_parser,
    scenario_title_parser,
    examples_title_parser,
    first_step_title_parser
]))))

optional_language_parser = OptionalLanguage()

table_row_parser = TableRow()
table_rows_parser = MultipleOf(table_row_parser)
single_quote_text_block_parser = TextBlock("'''")
double_quote_text_block_parser = TextBlock('"""')

step_parser = Dict((
    ('title', step_title_parser),
    ('data', MultipleOf(AnyOf([
        table_row_parser,
        single_quote_text_block_parser,
        double_quote_text_block_parser
    ])))
))
steps_parser = MultipleOf(step_parser)

optional_examples_parser = Optional(Dict((
    ('title', examples_title_parser),
    ('table', table_rows_parser),
)))

scenario_parser = Dict((
    ('tags', optional_multiline_tags_parser),
    ('title', scenario_title_parser),
    ('description', scenario_description_parser),
    ('steps', steps_parser),
    ('examples', optional_examples_parser),
))
scenarios_parser = MultipleOf(scenario_parser)

optional_background_parser = Optional(Dict((
    ('title', background_title_parser),
    ('description', background_description_parser),
    ('steps', steps_parser),
)))

feature_parser = Dict((
    ('language', optional_language_parser),
    ('tags', optional_multiline_tags_parser),
    ('title', feature_title_parser),
    ('description', feature_description_parser),
    ('background', optional_background_parser),
    ('scenarios', scenarios_parser),
))

@steps_parser.post_parse
def post_steps(context, result):
    prev_clause = None
    for step in result:
        clause = step['title']['clause'].lower()
        if clause in ('and', 'but'):
            clause = prev_clause
        step['title']['clause'] = clause

        table = None
        text = None
        for data in step['data']:
            if 'columns' in data:
                if table is None:
                    table = []
                table.append(data)
            elif 'text' in data:
                text = context['dict_cls']((
                    ('index', data['index']),
                    ('content', data['text']),
                ))
            else:
                raise Exception('Unexpected data type {!r}'.format(data))

        del step['data']
        step['table'] = table
        step['text'] = text

        prev_clause = clause

    return result

@scenario_parser.post_parse
def post_scenario(context, result):
    scenario_type = result['title']['type'].lower()

    if scenario_type == 'scenario':
        is_outline = False
    elif scenario_type == 'scenario outline':
        is_outline = True
    else:
        raise Exception('Unexpected scenario title type {!r}'.format(scenario_type))

    result['title'] = context['dict_cls']((
        ('is_outline', is_outline),
        ('content', result['title']['content']),
        ('index', result['title']['index']),
    ))

    if result['examples'] and not is_outline:
        raise ParseError(
            'Scenario block has examples section - should be \'scenario outline\'',
            line_index=result['title']['index']
        )

    if is_outline and not result['examples']:
        raise ParseError(
            'Scenario Outline block is missing an examples section',
            line_index=result['title']['index']
        )

    return result
