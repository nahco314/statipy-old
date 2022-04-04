import ast
from ast import NodeTransformer

from statipy.core.typed_ast import *
from statipy.core.node_preprocesser import NodePreprocessor
from statipy.core.abstract_object import (AbstractObject,
                                          Int, Str, List, Tuple, Set, Dict, Bool,
                                          Undefined)

from statipy.core.basic_func import (py_add, py_sub, py_mul, py_div, py_floordiv, py_mod, py_pow, py_lshift, py_rshift,
                                     py_or, py_xor, py_and, py_matmul,
                                     py_inplace_add, py_inplace_mul,
                                     py_negative, py_positive, py_invert)

from statipy.core.environment import Environment
import statipy.errors as errors

from typing import Any


class Typer(NodeTransformer):
    def __init__(self, code: str, context: Environment = None):
        self.t_ast = NodePreprocessor(code).make_ast()
        if context is None:
            context = Environment(self.t_ast)
        self.context = context

    def analysis(self) -> Typedmod:
        self.visit(self.t_ast)
        return self.t_ast

    def visit_Constant(self, node: TypedConstant) -> TypedConstant:
        match node.value:
            case int():
                res = Int().create_instance()
            case str():
                res = Str().create_instance()
            case _:
                raise errors.Mijissou(repr(node.value))

        node.abstract_object = res

        return node

    def visit_FormattedValue(self, node: TypedFormattedValue) -> TypedFormattedValue:
        self.generic_visit(node)
        node.abstract_object = Str().create_instance()
        return node

    def visit_JoinedStr(self, node: TypedJoinedStr) -> TypedJoinedStr:
        self.generic_visit(node)
        node.abstract_object = Str().create_instance()
        return node

    def visit_List(self, node: TypedList) -> TypedList:
        self.generic_visit(node)
        a_objects = [elt.abstract_obj.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = List().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_Tuple(self, node: TypedTuple) -> TypedTuple:
        self.generic_visit(node)
        a_objects = [elt.abstract_obj.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = Tuple().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_Set(self, node: TypedSet) -> TypedSet:
        self.generic_visit(node)
        a_objects = [elt.abstract_obj.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = Set().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_Dict(self, node: TypedDict) -> TypedDict:
        self.generic_visit(node)
        key_a_objects = [elt.abstract_obj.get_obj() for elt in node.keys]
        value_a_objects = [elt.abstract_obj.get_obj() for elt in node.values]
        for obj in key_a_objects:
            obj.unification(key_a_objects[0].get_obj())
        for obj in value_a_objects:
            obj.unification(value_a_objects[0].get_obj())
        res = Dict().create_instance()
        res.special_attr["key"] = key_a_objects[0].get_obj()
        res.special_attr["value"] = value_a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_Name(self, node: TypedName) -> TypedName:
        res = self.context.get_variable(node, node.id)
        node.abstract_object = res
        return node

    def visit_Starred(self, node: TypedStarred) -> TypedStarred:
        self.generic_visit(node)
        res = List().create_instance()
        res.special_attr["elt"] = node.value.abstract_obj.get_obj()
        node.abstract_object = res
        # ?
        return node

    def visit_Expr(self, node: TypedExpr) -> TypedExpr:
        self.generic_visit(node)
        return node

    def visit_UnaryOp(self, node: TypedUnaryOp) -> TypedUnaryOp:
        self.generic_visit(node)
        match node.op:
            case Not():
                # ToDo: __bool__ の評価
                res = Bool().create_instance()
            case USub():
                res = py_negative(node.operand.abstract_obj.get_obj())
            case UAdd():
                res = py_positive(node.operand.abstract_obj.get_obj())
            case Invert():
                res = py_invert(node.operand.abstract_obj.get_obj())
            case _:
                raise Exception
        node.abstract_object = res
        return node

    def visit_BinOp(self, node: TypedBinOp) -> TypedBinOp:
        self.generic_visit(node)
        match node.op:
            case Add():
                res = py_add(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case Sub():
                res = py_sub(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case Mult():
                res = py_mul(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case Div():
                res = py_div(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case FloorDiv():
                res = py_floordiv(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case Mod():
                res = py_mod(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case Pow():
                res = py_pow(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case LShift():
                res = py_lshift(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case RShift():
                res = py_rshift(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case BitOr():
                res = py_or(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case BitXor():
                res = py_xor(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case BitAnd():
                res = py_and(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case MatMult():
                res = py_matmul(node.left.abstract_obj.get_obj(), node.right.abstract_obj.get_obj())
            case _:
                raise Exception
        node.abstract_object = res
        return node
