"""Datastructures related to querying projects"""

from pathlib import Path
from typing import TypeAlias
import math

from lark import Lark, Transformer, UnexpectedInput, Token
from pydantic import BaseModel
import regex

grammar_file = Path(__file__).parent / "query-grammar.lark"

with open(grammar_file, "r", encoding="utf-8") as file:
    grammar = Lark(file.read())


class QueryLiteral(BaseModel):
    """Query literal base class"""

    id: str
    value: str
    inverted: bool

    def evaluate(self, context: dict[str, list[str] | str]) -> bool:
        """Checks if a given context matches this query"""

        if not self.id in context:
            return False ^ self.inverted

        value = context[self.id]

        if isinstance(value, list):
            return any(self._match(v) ^ self.inverted for v in value)

        return self._match(str(value)) ^ self.inverted

    def _match(self, _string: str) -> bool:
        """Check if a specific string matches the query"""
        return False


class HardQueryLiteral(QueryLiteral):
    """A primitive exact query condition"""

    def _match(self, string: str) -> bool:
        return self.value == string


class SoftQueryLiteral(QueryLiteral):
    """A primitive fuzzy query condition"""

    def _match(self, string: str) -> bool:
        n = len(self.value)
        count = max(min(math.ceil(n * 0.7), n - 1), 1)  # ~ 70% match
        return bool(regex.search(f"({self.value}){{e<={n-count}}}", string))


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
    def hard_query(
        self, items: tuple[str, str] | tuple[str, str, str]
    ) -> HardQueryLiteral:
        return HardQueryLiteral(id=items[0], value=items[-1], inverted=len(items) == 3)

    # pylint: disable=missing-function-docstring
    def soft_query(
        self, items: tuple[str, str] | tuple[str, str, str]
    ) -> SoftQueryLiteral:
        return SoftQueryLiteral(id=items[0], value=items[-1], inverted=len(items) == 3)

    # pylint: disable=missing-function-docstring
    def or_base_expression(self, items: tuple[QueryLiteral]) -> QueryLiteral:
        return items[0]

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
