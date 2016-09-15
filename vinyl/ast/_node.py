from abc import ABC
from typing import List, Optional
from vinyl.lex import *

__all__ = [
    'BaseNode',
    'IdentifierNode',
    'TypeNameNode',
    'ArgumentNode',
    'StatementNode',
    'ExpressionNode',
    'IfStatementNode',
    'VariableDeclarationNode',
    'FunctionDefinitionNode'
]


class BaseNode(ABC):
    pass


class IdentifierNode(BaseNode):
    @property
    def identifier(self) -> IdentifierToken:
        return self._identifier

    def __init__(self, identifier: IdentifierToken):
        self._identifier = identifier


class TypeNameNode(IdentifierNode):
    pass


class ArgumentNode(BaseNode):
    @property
    def identifier(self) -> IdentifierNode:
        return self._identifier

    @property
    def type_name(self) -> TypeNameNode:
        return self._type_name

    def __init__(self, identifier: IdentifierNode, type_name: TypeNameNode):
        self._identifier = identifier
        self._type_name = type_name


class StatementNode(BaseNode):
    pass


class ExpressionNode(StatementNode):
    pass


class IfStatementNode(StatementNode):
    @property
    def expression(self) -> ExpressionNode:
        return self.expression

    @property
    def when_true(self) -> List[StatementNode]:
        return self._when_true

    @property
    def when_false(self) -> List[StatementNode]:
        return self._when_false

    def __init__(self, expression: ExpressionNode, when_true: List[StatementNode], when_false: List[StatementNode]):
        self._expression = expression
        self._when_true = when_true
        self._when_false = when_false


class VariableDeclarationNode(StatementNode):
    @property
    def identifier(self) -> IdentifierNode:
        return self._identifier

    @property
    def type_name(self) -> TypeNameNode:
        return self._type_name

    @property
    def value(self) -> ExpressionNode:
        return self._value

    def __init__(self, identifier: IdentifierNode, type_name: TypeNameNode, value: Optional[ExpressionNode]):
        self._identifier = identifier
        self._type_name = type_name
        self._value = value


class FunctionDefinitionNode(BaseNode):
    @property
    def identifier(self) -> IdentifierNode:
        return self._identifier

    @property
    def arguments(self) -> List[ArgumentNode]:
        return self._arguments

    @property
    def return_type(self) -> Optional[TypeNameNode]:
        return self._return_type

    @property
    def block(self) -> List[StatementNode]:
        return self._block

    def __init__(self,
                 identifier: IdentifierNode,
                 arguments: List[ArgumentNode],
                 return_type: Optional[TypeNameNode],
                 block: List[StatementNode]):
        self._identifier = identifier
        self._arguments = arguments
        self._return_type = return_type
        self._block = block
