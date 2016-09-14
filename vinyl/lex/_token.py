import re
from abc import ABC, abstractmethod
from enum import Enum, IntEnum, unique
from numbers import Integral, Real
from typing import Optional
from ._stream import Location, StreamBase

__all__ = [
    'SymbolTokenKind',
    'KeywordTokenKind',
    'FloatKind',
    'IntegerKind',
    'IntegerBase',
    'Matchers',
    'BaseToken',
    'SyntacticalError',
    'NumberTokenBase',
    'IntegerToken',
    'FloatToken',
    'IdentifierToken',
    'SymbolToken',
    'KeywordToken',
    'CommentToken'
]


@unique
class SymbolTokenKind(Enum):
    ARROW = '->'
    SCOPE = '::'
    COMMA = ','
    DOT = '.'
    PLUS = '+'
    MINUS = '-'
    LESS_THAN = '<'
    GREATER_THAN = '>'
    EQUAL = '='
    SEMI_COLON = ';'
    COLON = ':'
    PAREN_OPEN = '('
    PAREN_CLOSE = ')'
    QUOTE_SINGLE = '\''
    ASTERISK = '*'
    EXCLAMATION_POINT = '!'
    BRACKET_OPEN = '['
    BRACKET_CLOSE = ']'
    BRACE_OPEN = '{'
    BRACE_CLOSE = '}'


@unique
class KeywordTokenKind(Enum):
    TRAIT = 'trait'
    TUPLE = 'tuple'
    ALIAS = 'alias'
    DEF = 'def'
    MOD = 'mod'


@unique
class FloatKind(Enum):
    NONE = ''
    F32 = 'f32'
    F64 = 'f64'


@unique
class IntegerKind(Enum):
    NONE = ''
    INT_8 = 'i8'
    UINT_8 = 'u8'
    INT_16 = 'i16'
    UINT_16 = 'u16'
    INT_32 = 'i32'
    UINT_32 = 'u32'
    INT_64 = 'i64'
    UINT_64 = 'u64'
    INT = 'i'
    UINT = 'u'


@unique
class IntegerBase(IntEnum):
    base2 = 2
    base8 = 8
    base10 = 10
    base16 = 16


class Matchers(ABC):
    _SEPARATORS = {enum.value[0] for enum in SymbolTokenKind}

    @staticmethod
    def is_number_separator(prev: Optional[str], c: str) -> bool:
        if prev is not None and prev in 'eE' and c in '+-':
            return False
        return Matchers.is_separator(prev, c)

    @staticmethod
    def is_separator(prev: Optional[str], c: str) -> bool:
        return c.isspace() or c in Matchers._SEPARATORS

    @staticmethod
    def is_not_space(prev: Optional[str], c: str) -> bool:
        return not c.isspace()

    @staticmethod
    def is_comment_terminator(prev: Optional[str], c: str) -> bool:
        return prev == '*' and c == '/'


class BaseToken(ABC):
    @property
    def start_location(self) -> Location:
        return self._start_location

    @property
    def end_location(self) -> Location:
        return self._end_location

    @property
    def text(self) -> str:
        return self._text

    @staticmethod
    @abstractmethod
    def short_name() -> str:
        pass

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__()
        self._text = text
        self._start_location = start_location
        self._end_location = end_location

    def __eq__(self, other: 'BaseToken') -> bool:
        if type(self) is not type(other):
            return False
        return self._text == other._text

    def __repr__(self) -> str:
        return '{}(text=\'{}\')'.format(type(self).__name__, self._text)


class SyntacticalError(Exception):
    @property
    def token(self) -> BaseToken:
        return self._token

    @property
    def message(self) -> str:
        return self._message

    def __init__(self, token: BaseToken, message: str=''):
        super().__init__()
        self._token = token
        self._message = message

    def __str__(self) -> str:
        return self._message


class NumberTokenBase(BaseToken):
    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        self._clean_text = text.replace('_', '').lower()


class IntegerToken(NumberTokenBase):
    _regex2 = re.compile(r'0b([0-1]+)(i8|u8|i16|u16|i32|u32|i64|u64|i|u)?')
    _regex8 = re.compile(r'0c([0-7]+)(i8|u8|i16|u16|i32|u32|i64|u64|i|u)?')
    _regex10 = re.compile(r'([0-9]+)(i8|u8|i16|u16|i32|u32|i64|u64|i|u)?')
    _regex16 = re.compile(r'0x([0-9a-f]+)(i8|u8|i16|u16|i32|u32|i64|u64|i|u)?')

    @property
    def kind(self) -> IntegerKind:
        return self._kind

    @property
    def value(self) -> Integral:
        return self._value

    @property
    def base(self) -> IntegerBase:
        return self._base

    @staticmethod
    def short_name() -> str:
        return 'integer literal'

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        if self._clean_text.startswith('0b'):
            self._base = IntegerBase.base2
            m = re.fullmatch(self._regex2, self._clean_text)
        elif self._clean_text.startswith('0o'):
            self._base = IntegerBase.base8
            m = re.fullmatch(self._regex8, self._clean_text)
        elif self._clean_text.startswith('0x'):
            self._base = IntegerBase.base16
            m = re.fullmatch(self._regex16, self._clean_text)
        else:
            self._base = IntegerBase.base10
            m = re.fullmatch(self._regex10, self._clean_text)
        if m is None:
            raise SyntacticalError(self, 'Malformed {}'.format(self.short_name()))
        self._value = int(m.group(1), self._base.value)
        suffix = m.group(2)
        if suffix is not None:
            self._kind = IntegerKind(suffix)
        else:
            self._kind = IntegerKind.NONE

    def __repr__(self) -> str:
        return '{}(value={},kind={},base={})'.format(type(self).__name__, self._value, self._kind, self._base)

    def __eq__(self, other: 'IntegerToken') -> bool:
        if not super().__eq__(other):
            return False
        if self._kind is not other._kind:
            return False
        if self._base is not other._base:
            return False
        return self._value == other._value


class FloatToken(NumberTokenBase):
    _regex1 = re.compile(r'([0-9]+\.[0-9]*(?:e[+-]?[0-9]+)?)(f32|f64)?')
    _regex2 = re.compile(r'([0-9]+e[+-]?[0-9]+)(f32|f64)?')

    @property
    def kind(self) -> FloatKind:
        return self._kind

    @property
    def value(self) -> Real:
        return self._value

    @staticmethod
    def short_name() -> str:
        return 'floating point literal'

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        m = re.fullmatch(self._regex1, self._clean_text)
        if m is None:
            m = re.fullmatch(self._regex2, self._clean_text)
        if m is None:
            raise SyntacticalError(self, 'Malformed {}'.format(self.short_name()))
        self._value = float(m.group(1))
        suffix = m.group(2)
        if suffix is not None:
            self._kind = FloatKind(suffix)
        else:
            self._kind = FloatKind.NONE

    def __repr__(self) -> str:
        return '{}(value={},kind={})'.format(type(self).__name__, self._value, self._kind)

    def __eq__(self, other: 'FloatToken') -> bool:
        if not super().__eq__(other):
            return False
        if self._kind is not other._kind:
            return False
        return self._value == other._value


class IdentifierToken(BaseToken):
    _regex = re.compile(r'\w+')

    @staticmethod
    def short_name() -> str:
        return 'identifier'

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        m = re.fullmatch(self._regex, self._text)
        if m is None:
            raise SyntacticalError(self, 'Malformed {}'.format(self.short_name()))


class KeywordToken(BaseToken):
    @property
    def kind(self) -> KeywordTokenKind:
        return self._kind

    @staticmethod
    def short_name() -> str:
        return 'keyword'

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        for kind in KeywordTokenKind:
            if kind.value == self._text:
                self._kind = kind
                break
        else:
            self._kind = None
            raise SyntacticalError(self, 'Malformed {}'.format(self.short_name()))

    def __repr__(self) -> str:
        return '{}(text=\'{}\',kind={})'.format(type(self).__name__, self._text, self._kind)


class SymbolToken(BaseToken):
    @property
    def kind(self) -> SymbolTokenKind:
        return self._kind

    @staticmethod
    def short_name() -> str:
        return 'symbol'

    def __init__(self, text: str, start_location: Location, end_location: Location):
        super().__init__(text, start_location, end_location)
        for kind in SymbolTokenKind:
            if kind.value == self._text:
                self._kind = kind
                break
        else:
            self._kind = None
            raise SyntacticalError(self, 'Malformed {}'.format(self.short_name))

    def __repr__(self) -> str:
        return '{}(text=\'{}\',kind={})'.format(type(self).__name__, self._text, self._kind)


class CommentToken(BaseToken):
    pass
