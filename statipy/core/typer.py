import ast
from ast import NodeTransformer
from ast import Add, Mult, BinOp, Constant, Assign, AugAssign, Name

from statipy.core.typed_ast import from_node, Typedexpr, TypedBinOp, TypedConstant, TypedName
from statipy.core.abstract_object import AbstractObject, Int, Str, Undefined

from statipy.core.basic_func import py_add, py_mul, py_inplace_add, py_inplace_mul

from statipy.core.context import Context
import statipy.errors as errors

from typing import Any


class Typer(NodeTransformer):
    def __init__(self, context: Context = None):
        if context is None:
            context = Context()
        self.context = context

    def assign_sub(self, node: ast.AST, value: AbstractObject):
        match node:
            case Name():
                self.context.assign_variable(node.id, value)

    def visit_Constant(self, node: Constant) -> TypedConstant:
        match node.value:
            case int():
                res = Int().create_instance()
            case str():
                res = Str().create_instance()
            case _:
                raise errors.Mijissou(repr(node.value))

        res_node = from_node(node, res)
        assert isinstance(res_node, TypedConstant)
        return res_node

    def visit_BinOp(self, node: BinOp) -> TypedBinOp:
        self.generic_visit(node)

        n_left, n_right = node.left, node.right
        assert isinstance(n_left, Typedexpr) and isinstance(n_right, Typedexpr)
        left, right = n_left.abstract_obj, n_right.abstract_obj

        match node.op:
            case Add():
                res = py_add(left, right)
            case Mult():
                res = py_mul(left, right)
            case _:
                raise errors.Mijissou()

        res_node = from_node(node, res)
        assert isinstance(res_node, TypedBinOp)
        return res_node

    def visit_Name(self, node: Name) -> TypedName:
        obj = self.context.get_variable(node.id)

        if isinstance(obj, Undefined):
            raise errors.TypeError

        res_node = from_node(node, obj)
        assert isinstance(res_node, TypedName)
        return res_node

    def visit_Assign(self, node: Assign) -> Assign:
        if len(node.targets) != 1 or not isinstance(node.targets[0], Name):
            raise errors.Mijissou()

        node.value = self.visit(node.value)
        assert isinstance(node.value, Typedexpr)

        self.assign_sub(node.targets[0], node.value.abstract_obj)

        return node

    def visit_AugAssign(self, node: AugAssign) -> AugAssign:
        self.generic_visit(node)

        n_left, n_right = node.target, node.value
        assert isinstance(n_left, Typedexpr) and isinstance(n_right, Typedexpr)
        left, right = n_left.abstract_obj, n_right.abstract_obj

        match node.op:
            case Add():
                res = py_inplace_add(left, right)
            case Mult():
                res = py_inplace_mul(left, right)
            case _:
                raise errors.Mijissou()

        self.assign_sub(node.target, res)

        return node


c = """
a = 10
if a > 5:
    a = 5
else:
    pass

"""
n = ast.parse(c)
t = Typer()
t.visit(n)

print(ast.dump(n, indent=4))
