import unittest
from abc import ABC, abstractmethod
from typing import List
import vinyl.lex as lex
from vinyl.cs import StringStream


from ..patch_unittest import *


class TestLexerBase(ABC, unittest.TestCase):
    @staticmethod
    @abstractmethod
    def good_inputs() -> List[str]:
        return []

    @staticmethod
    @abstractmethod
    def bad_inputs() -> List[str]:
        return []

    @staticmethod
    @abstractmethod
    def token_class() -> type(lex.BaseToken):
        return lex.BaseToken

    def test_good_inputs(self) -> None:
        for good in self.good_inputs():
            istream = StringStream(good)
            self.assertIsInstance(next(lex.Lexer(istream)), self.token_class())

    def test_bad_inputs(self) -> None:
        for bad in self.bad_inputs():
            istream = StringStream(bad)
            try:
                self.assertNotEqual(type(next(lex.Lexer(istream))), self.token_class())
            except StopIteration:
                self.assertTrue(istream.ended)
            except Exception as e:
                self.assertIsInstance(e, lex.TokenError)


class TestIdentifierLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [
            'a',
            'hello',
            'こんにちは',
            ' \tafter_Whitespace',
            'hasANumber42',
        ]

    @staticmethod
    def bad_inputs() -> List[str]:
        return [enum.value for enum in lex.KeywordTokenKind] + \
               [enum.value for enum in lex.SymbolTokenKind] + [
            '1number',
            '.E13',
            '1e3',
            ' ',
            '\n\n\n\n\n\n\n\n'
        ]

    @staticmethod
    def token_class() -> type(lex.IdentifierToken):
        return lex.IdentifierToken


class TestKeywordLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [enum.value for enum in lex.KeywordTokenKind]

    @staticmethod
    def bad_inputs() -> List[str]:
        return [enum.value for enum in lex.SymbolTokenKind]

    @staticmethod
    def token_class() -> type(lex.KeywordToken):
        return lex.KeywordToken


class TestSymbolLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [enum.value for enum in lex.SymbolTokenKind]

    @staticmethod
    def bad_inputs() -> List[str]:
        return [enum.value for enum in lex.KeywordTokenKind]

    @staticmethod
    def token_class() -> type(lex.SymbolToken):
        return lex.SymbolToken
