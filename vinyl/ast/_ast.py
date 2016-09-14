from abc import ABC
from typing import List, cast
from vinyl.lex import *

__all__ = [
    'BaseNode',
    'FunctionDefinitionNode',
    'IdentifierNode',
    'Parser'
]


class BaseNode(ABC):
    pass


class FunctionDefinitionNode(BaseNode):
    pass


class IdentifierNode(BaseNode):
    @property
    def id(self) -> IdentifierToken:
        return self._id

    def __init__(self, id: IdentifierToken):
        self._id = id


class TypeNameNode(IdentifierNode):
    pass


class Parser:
    @property
    def lexer(self) -> PeekLexer:
        return self._lexer

    def __init__(self, lexer: PeekLexer):
        self._lexer = lexer

    @classmethod
    def from_stream(cls, istream: StreamBase):
        return cls(PeekLexer.from_stream(istream))

    def parse(self) -> List[BaseNode]:
        nodes = []
        try:
            while True:
                token = self._lexer.peek()
                if not token:
                    break
                if isinstance(token, KeywordToken):
                    if token.kind is KeywordTokenKind.DEF:
                        nodes.append(self._consume_function_definition())
                        continue

                raise SyntacticalError(token, 'Unexpected "{}"'.format(token.text))

        except SyntacticalError as e:
            raise e

        return nodes

    def _consume_function_definition(self) -> FunctionDefinitionNode:
        self._consume_keyword(KeywordTokenKind.DEF, 'Function definitions must begin with "def"')
        name = self._consume_identifier('The {}: "{}" is not a valid function name')
        self._consume_symbol(SymbolTokenKind.PAREN_OPEN, 'Expected "(" to begin function argument list')

        self.args = []

        if not self._is_symbol(self._lexer.peek(), SymbolTokenKind.PAREN_CLOSE):
            while True:
                self.args.append(self._consume_identifier('The {}: "{}" is not a valid argument name'))
                self._consume_symbol(SymbolTokenKind.COLON, 'Expected ":" for argument type')
                self.args.append(self._consume_type_name('The {}: "{}" is not a valid argument type'))
                if not self._is_symbol(self._lexer.peek(), SymbolTokenKind.COMMA):
                    break
                else:
                    self._lexer.read()

        self._consume_symbol(SymbolTokenKind.PAREN_CLOSE, 'Expected ")" to end function argument list')

        if self._is_symbol(self._lexer.peek(), SymbolTokenKind.COLON):
            self._lexer.read()
            self._consume_type_name('Unexpected {}: "{}" as function return type')

        self._consume_symbol(SymbolTokenKind.BRACE_OPEN, 'Expected "{" to begin function body')

        self._consume_symbol(SymbolTokenKind.BRACE_CLOSE, 'Expected "}" to end function body')

        return FunctionDefinitionNode()

    def _consume_type_name(self, error_message: str) -> TypeNameNode:
        token = self._lexer.peek()
        if not self._is_identifier(token):
            raise SyntacticalError(token, error_message.format(token.short_name(), token.text))
        return TypeNameNode(cast(IdentifierToken, self._lexer.read()))

    def _consume_identifier(self, error_message: str) -> IdentifierToken:
        token = self._lexer.peek()
        if not self._is_identifier(token):
            raise SyntacticalError(token, error_message.format(token.short_name(), token.text))
        return IdentifierNode(cast(IdentifierToken, self._lexer.read()))

    def _consume_symbol(self, kind: SymbolTokenKind, error_message: str) -> SymbolToken:
        token = self._lexer.peek()
        if not self._is_symbol(token, kind):
            raise SyntacticalError(token, error_message)
        return self._lexer.read()

    def _consume_keyword(self, kind: KeywordTokenKind, error_message: str) -> KeywordToken:
        token = self._lexer.peek()
        if not self._is_keyword(token, kind):
            raise SyntacticalError(token, error_message)
        return self._lexer.read()

    @staticmethod
    def _is_identifier(token: BaseToken) -> bool:
        return isinstance(token, IdentifierToken)

    @staticmethod
    def _is_keyword(token: BaseToken, kind: KeywordTokenKind) -> bool:
        return isinstance(token, KeywordToken) and cast(KeywordToken, token).kind is kind

    @staticmethod
    def _is_symbol(token: BaseToken, kind: SymbolTokenKind) -> bool:
        return isinstance(token, SymbolToken) and cast(SymbolToken, token).kind is kind