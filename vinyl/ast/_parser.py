from typing import List, cast
from vinyl.lex import *
from ._node import *

__all__ = [
    'Parser'
]


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
                if self._is_keyword(token, KeywordTokenKind.LET):
                    nodes.append(self._consume_variable_declaration())
                elif self._is_keyword(token, KeywordTokenKind.DEF):
                    nodes.append(self._consume_function_definition())
                elif self._is_symbol(token, SymbolTokenKind.SEMI_COLON):
                    self._lexer.read()
                else:
                    raise SyntacticalError(token, 'Unexpected {}: "{}"'.format(token.short_name(), token.text))

        except SyntacticalError as e:
            raise e

        return nodes

    def _consume_function_definition(self) -> FunctionDefinitionNode:
        self._consume_keyword(KeywordTokenKind.DEF, 'Function definitions must begin with "{}"')
        name = self._consume_identifier('The {}: "{}" is not a valid function name')

        self._consume_symbol(SymbolTokenKind.PAREN_OPEN, 'Expected "{}" to begin function argument list')
        args = []
        if not self._is_symbol(self._lexer.peek(), SymbolTokenKind.PAREN_CLOSE):
            while True:
                identifier = self._consume_identifier('The {}: "{}" is not a valid argument name')
                type_name = self._consume_type_name('The {} "{}" is not a valid argument type')
                args.append(ArgumentNode(identifier, type_name))
                if not self._is_symbol(self._lexer.peek(), SymbolTokenKind.COMMA):
                    break
                else:
                    self._lexer.read()
        self._consume_symbol(SymbolTokenKind.PAREN_CLOSE, 'Expected "{}" to end function argument list')

        return_type = None
        if not self._is_symbol(self._lexer.peek(), SymbolTokenKind.BRACE_OPEN):
            return_type = self._consume_type_name('Unexpected {}: "{}" as function return type')

        block = self._consume_block('the function body of "{}"'.format(name.identifier.text))

        return FunctionDefinitionNode(name, args, return_type, block)

    def _consume_block(self, block_type: str) -> List[StatementNode]:
        self._consume_symbol(SymbolTokenKind.BRACE_OPEN, 'Expected "{{}}" to begin {}'.format(block_type))
        block = []
        while not self._is_symbol(self._lexer.peek(), SymbolTokenKind.BRACE_CLOSE):
            block.append(self._consume_statement())

        self._consume_symbol(SymbolTokenKind.BRACE_CLOSE, 'Expected "{{}}" to end {}'.format(block_type))
        return block

    def _consume_statement(self) -> StatementNode:
        statement = None
        token = self._lexer.peek()
        if self._is_keyword(token, KeywordTokenKind.LET):
            statement = self._consume_variable_declaration()
        elif self._is_keyword(token, KeywordTokenKind.IF):
            statement = self._consume_if_statement()

        else:
            self._consume_symbol(SymbolTokenKind.SEMI_COLON, 'Expected "{}" to end statement')
        return statement

    def _consume_if_statement(self) -> IfStatementNode:
        self._consume_keyword(KeywordTokenKind.IF, 'If statements must begin with "{}"')
        expression = self._consume_expression()
        when_true = self._consume_block('true-condition of if statement')
        when_false = []
        if self._is_keyword(self._lexer.peek(), KeywordTokenKind.ELSE):
            self._lexer.read()
            when_false = self._consume_block('false-condition of if statement')
        return IfStatementNode(expression, when_true, when_false)

    def _consume_variable_declaration(self) -> VariableDeclarationNode:
        self._consume_keyword(KeywordTokenKind.LET, 'Variable declarations must begin with "{}"')
        identifier = self._consume_identifier('The {}: "{}" is not a valid variable name')
        type_name = self._consume_type_name('The {} "{}" is not a valid variable type')
        value = None
        if self._is_symbol(self._lexer.peek(), SymbolTokenKind.EQUAL):
            self._lexer.read()
            value = self._consume_expression()
        return VariableDeclarationNode(identifier, type_name, value)

    def _consume_expression(self) -> ExpressionNode:
        self._lexer.read()
        pass

    def _consume_type_name(self, error_message: str) -> TypeNameNode:
        token = self._lexer.peek()
        if not self._is_identifier(token):
            raise SyntacticalError(token, error_message.format(token.short_name(), token.text))
        return TypeNameNode(cast(IdentifierToken, self._lexer.read()))

    def _consume_identifier(self, error_message: str) -> IdentifierNode:
        token = self._lexer.peek()
        if not self._is_identifier(token):
            raise SyntacticalError(token, error_message.format(token.short_name(), token.text))
        return IdentifierNode(cast(IdentifierToken, self._lexer.read()))

    def _consume_symbol(self, kind: SymbolTokenKind, error_message: str) -> SymbolToken:
        token = self._lexer.peek()
        if not self._is_symbol(token, kind):
            raise SyntacticalError(token, error_message.format(kind.value))
        return self._lexer.read()

    def _consume_keyword(self, kind: KeywordTokenKind, error_message: str) -> KeywordToken:
        token = self._lexer.peek()
        if not self._is_keyword(token, kind):
            raise SyntacticalError(token, error_message.format(kind.value))
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