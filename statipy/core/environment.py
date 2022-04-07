from __future__ import annotations

from typing import Optional

from statipy.core.abstract_object import AbstractObject, Undefined
import statipy.errors as errors
import statipy.core.typed_ast as t_ast

from collections import defaultdict
import ast


class Environment:
    def __init__(self, module: t_ast.Typedmod):
        self.tree: list[t_ast.Typedmod | t_ast.Typedstmt] = [module]
        self.current_scope: Block = Block(module.body, module, None)
        self.ast_to_block: dict[t_ast.TypedAST, Block] = {module: self.current_scope}
        self.variables: dict[str, list[Variable]] = defaultdict(list)

    def set_builtin(self, name: str, value: AbstractObject):
        assert not self.variables[name]
        self.variables[name].append(Variable([name], self.current_scope, None, [], [], value))

    def step_in(self, node: t_ast.Typedstmt, body: list[t_ast.Typedstmt]):
        self.tree.append(node)
        block = Block(body, node, self.current_scope)
        self.ast_to_block[node] = block
        self.current_scope = block

    def assign_variable(self, node: t_ast.TypedAST, name: str, value: AbstractObject):
        # ToDo: 再代入
        if not self.variables[name]:
            self.variables[name].append(Variable([name], self.current_scope, node, [], [], value))
        var = self.variables[name][-1]
        var.assign(node, value)

    def get_variable(self, node: t_ast.TypedAST, name: str) -> AbstractObject:
        if not self.variables[name]:
            raise errors.TypeError
        res = self.variables[name][-1].reference(node)
        return res

    def step_out(self):
        node = self.tree.pop()
        for vars in self.variables.values():
            if vars and vars[-1].scope == self.current_scope:
                vars.pop()
        self.current_scope = self.current_scope.parent


class Block:
    def __init__(self, nodes: list[t_ast.Typedstmt], p_node: t_ast.Typedstmt | t_ast.Typedmod, parent: Optional[Block]):
        self.ast_nodes = nodes
        self.p_node = p_node
        self.parent = parent
        self.variables: dict[str, Variable] = {}


class Variable:
    def __init__(self,
                 name_candidates: list[str],
                 scope: Block,
                 definition_location: Optional[t_ast.TypedAST],
                 assign_locations: list[t_ast.TypedAST],
                 reference_locations: list[t_ast.TypedAST],
                 value: AbstractObject = None
                 ):
        if value is None:
            value = Undefined()
        self.name_candidates = name_candidates
        self.scope = scope
        self.definition_location = definition_location
        self.assign_locations = assign_locations
        self.reference_locations = reference_locations
        self.value = value

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def assign(self, node: t_ast.TypedAST, value: AbstractObject):
        self.assign_locations.append(node)
        self.value.get_obj().unification(value)

    def reference(self, node: t_ast.TypedAST):
        self.reference_locations.append(node)
        return self.value.get_obj()
