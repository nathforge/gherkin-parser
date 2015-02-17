class ParseError(Exception):
    """
    ParseError is raised when parsing a feature.
    """

    def __init__(self, message, line_index=None, filename=None):
        super(ParseError, self).__init__()
        self.message = message
        self.line_index = line_index
        self.filename = filename

    def __str__(self):
        string = self.message

        if self.line_index is not None:
            if self.filename:
                string = '{} (line {} of {})'.format(
                    string,
                    self.line_index + 1,
                    self.filename
                )
            else:
                string = '{} (line {})'.format(
                    string,
                    self.line_index + 1
                )

        return string

class RecoverableParseError(ParseError):
    """
    RecoverableParseError is raised when parsing a feature.

    It indicates that we may be able to backtrack and find another way to parse
    the line.
    """
