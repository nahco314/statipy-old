class Error(Exception):
    pass


class TypingError(Error):
    pass


class TypeError(TypingError):
    pass


class AttributeError(TypingError):
    pass


class Mijissou(Error):
    pass
