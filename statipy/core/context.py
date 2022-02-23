from statipy.core.abstract_object import AbstractObject, Undefined
import statipy.errors as errors

from collections import defaultdict
import ast


class Context:
    def __init__(self):
        self.variables: dict[str, AbstractObject] = defaultdict(Undefined)

    def assign_variable(self, name: str, value: AbstractObject):
        # ToDo: 再代入
        self.variables[name].unification(value)

    def get_variable(self, name: str) -> AbstractObject:
        res = self.variables[name].get_obj()
        return res


class Variable:
    def __init__(self, name_candidates: list[str],
                 definition_location: ast.AST,
                 assign_locations: list[ast.AST],
                 reference_locations: list[ast.AST],
                 ):
        self.name_candidates = name_candidates
        self.definition_location = definition_location
        self.assign_locations = assign_locations
        self.reference_locations = reference_locations

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other
