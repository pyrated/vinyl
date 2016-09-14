from abc import ABC, abstractmethod
from typing import Iterator
from ._token import *
from ._stream import *

__all__ = [
    'BaseLexer',
    'PeekLexer',
    'Lexer',
    'NumberLexer',
    'IdentifierLexer',
    'SymbolLexer',
    'CommentLexer'
]


class BaseLexer(ABC, Iterator[BaseToken]):
    def skip_spaces(self):
        self._istream.read_until(Matchers.is_not_space)
        if self._istream.ended:
            raise StopIteration

    def __init__(self, istream: StreamBase):
        super().__init__()
        self._istream = istream

    def __iter__(self) -> Iterator[BaseToken]:
        return self

    @abstractmethod
    def __next__(self) -> BaseToken:
        pass


class PeekLexer(Iterator[BaseToken]):
    def __init__(self, lexer: BaseLexer):
        self._lexer = lexer
        self._exception = None
        try:
            self._token = next(self._lexer)
        except BaseException as e:
            self._token = None
            self._exception = e

    def __iter__(self) -> Iterator[BaseToken]:
        return self

    def __next__(self) -> BaseToken:
        if self._exception is not None:
            raise self._exception
        if self._token is None:
            raise StopIteration()
        tok = self._token
        try:
            self._token = next(self._lexer)
        except StopIteration:
            self._token = None
        return tok

    @classmethod
    def from_stream(cls, istream: StreamBase):
        return cls(Lexer(istream))

    def read(self) -> BaseToken:
        return next(self)

    def peek(self) -> BaseToken:
        if isinstance(self._exception, StopIteration):
            return None
        if self._exception is not None:
            raise self._exception
        return self._token


class Lexer(BaseLexer):
    def __next__(self) -> BaseToken:
        self.skip_spaces()
        c = self._istream.peek()
        if c.isdigit():
            return next(NumberLexer(self._istream))
        elif c.isidentifier():
            return next(IdentifierLexer(self._istream))
        elif self._istream.peek(2) in ['//', '/*']:
            return next(CommentLexer(self._istream))
        return next(SymbolLexer(self._istream))


class NumberLexer(Iterator[NumberTokenBase], BaseLexer):
    def __next__(self) -> NumberTokenBase:
        self.skip_spaces()
        start_location = self._istream.location
        s = self._istream.read_until(Matchers.is_number_separator)
        end_location = self._istream.location
        try:
            return FloatToken(s, start_location, end_location)
        except SyntacticalError:
            return IntegerToken(s, start_location, end_location)


class IdentifierLexer(Iterator[IdentifierToken], BaseLexer):
    def __next__(self) -> IdentifierToken:
        self.skip_spaces()
        start_location = self._istream.location
        s = self._istream.read_until(Matchers.is_separator)
        end_location = self._istream.location
        try:
            return KeywordToken(s, start_location, end_location)
        except SyntacticalError:
            return IdentifierToken(s, start_location, end_location)


class SymbolLexer(Iterator[SymbolToken], BaseLexer):
    _LONGEST_SYMBOL = max(SymbolTokenKind, key=lambda sym: len(sym.value))

    def __next__(self) -> SymbolToken:
        self.skip_spaces()
        start_location = self._istream.location
        for i in range(len(self._LONGEST_SYMBOL.value), 0, -1):
            s = self._istream.peek(i)
            try:
                SymbolToken(s, Location(), Location())
                s = self._istream.read(i)
                end_location = self._istream.location
                return SymbolToken(s, start_location, end_location)
            except SyntacticalError:
                continue
        # Give up and raise the exception
        s = self._istream.read(1)
        end_location = self._istream.location
        return SymbolToken(s, start_location, end_location)


class CommentLexer(Iterator[CommentToken], BaseLexer):
    def __next__(self) -> NumberTokenBase:
        self.skip_spaces()
        start_location = self._istream.location
        c = self._istream.peek(2)
        if c == '/*':
            s = self._istream.read_until(Matchers.is_comment_terminator)
            s += self._istream.read()
        else:
            s = self._istream.read_until_exactly('\n')
        end_location = self._istream.location
        return CommentToken(s, start_location, end_location)
