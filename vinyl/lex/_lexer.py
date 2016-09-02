from typing import Iterator
from ._token import *
from ._cs import *


class BaseLexer(Iterator[BaseToken]):
    def skip_spaces(self) -> None:
        self._istream.read_until(Matchers.is_not_space)
        if self._istream.ended:
            raise StopIteration

    def __init__(self, istream: StreamBase):
        super().__init__()
        self._istream = istream

    def __iter__(self) -> Iterator[BaseToken]:
        return self


class Lexer(BaseLexer):
    def __next__(self) -> BaseToken:
        self.skip_spaces()
        c = self._istream.peek()
        if c.isdigit():
            return next(NumberLexer(self._istream))
        elif c.isidentifier():
            return next(IdentifierLexer(self._istream))
        elif c == '/' and self._istream.peek(2) == '//':
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
        except TokenError:
            return IntegerToken(s, start_location, end_location)


class IdentifierLexer(Iterator[IdentifierToken], BaseLexer):
    def __next__(self) -> IdentifierToken:
        self.skip_spaces()
        start_location = self._istream.location
        s = self._istream.read_until(Matchers.is_separator)
        end_location = self._istream.location
        try:
            return KeywordToken(s, start_location, end_location)
        except TokenError:
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
            except TokenError:
                continue
        # Give up and raise the exception
        s = self._istream.read(1)
        end_location = self._istream.location
        return SymbolToken(s, start_location, end_location)


class CommentLexer(Iterator[CommentToken], BaseLexer):
    def __next__(self) -> NumberTokenBase:
        self.skip_spaces()
        start_location = self._istream.location
        s = self._istream.read_until_exactly('\n')
        end_location = self._istream.location
        return CommentToken(s, start_location, end_location)
