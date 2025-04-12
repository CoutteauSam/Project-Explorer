"""Datastructures related to querying projects"""

from pathlib import Path
from typing import TypeAlias

from lark import Lark, Transformer, UnexpectedInput, Token
from pydantic import BaseModel

grammar_file = Path(__file__).parent / "query-grammar.lark"

with open(grammar_file, "r", encoding="utf-8") as file:
    grammar = Lark(file.read())


class QueryLiteral(BaseModel):
    """A primitive query condition"""

    id: str
    value: str
    inverted: bool

    def evaluate(self, context: dict[str, list[str] | str]) -> bool:
        """Checks if a given context matches this query"""

        if not self.id in context:
            return False ^ self.inverted

        value = context[self.id]

        if isinstance(value, list):
            return (self.value in value) ^ self.inverted

        return (str(value) == self.value) ^ self.inverted


class QueryOr(BaseModel):
    """A compound of primitives query condition"""

    components: list[QueryLiteral]

    def evaluate(self, context: dict[str, list[str] | str]) -> bool:
        """Checks if a given context matches this query"""
        return any(component.evaluate(context) for component in self.components)


class QueryAnd(BaseModel):
    """A compound of compounds query condition"""

    components: list[QueryOr | QueryLiteral]

    def evaluate(self, context: dict[str, list[str] | str]) -> bool:
        """Checks if a given context matches this query"""
        return all(component.evaluate(context) for component in self.components)


Query: TypeAlias = QueryLiteral | QueryAnd | QueryOr


class _QueryTransformer(Transformer[Token, Query]):
    """Transforms a parse result into a query"""

    # pylint: disable=missing-function-docstring
    def or_base_expression(
        self, items: tuple[str, str] | tuple[str, str, str]
    ) -> QueryLiteral:
        return QueryLiteral(id=items[0], value=items[-1], inverted=len(items) == 3)

    # pylint: disable=missing-function-docstring
    def and_base_expression(
        self, items: tuple[QueryOr | QueryLiteral]
    ) -> QueryOr | QueryLiteral:
        return items[0]

    # pylint: disable=missing-function-docstring
    def or_expression(self, items: list[QueryLiteral]) -> QueryOr:
        return QueryOr(components=items)

    # pylint: disable=missing-function-docstring
    def and_expression(self, items: list[QueryLiteral | QueryOr]) -> QueryAnd:
        return QueryAnd(components=items)

    # pylint: disable=missing-function-docstring
    def start(self, items: tuple[Query]) -> Query:
        return items[0]


class InvalidQuery(BaseModel):
    """A malformed query"""

    diagnosis: str


def parse_query(query: str) -> Query | InvalidQuery:
    """Converts a string into a proper query"""

    try:
        tree = grammar.parse(query)
        return _QueryTransformer().transform(tree)
    except UnexpectedInput as unexpected_input:
        return InvalidQuery(diagnosis=unexpected_input.get_context(query))
