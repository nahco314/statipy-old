import ast
from ast import NodeTransformer

from statipy.core.typed_ast import *
from statipy.core.node_preprocesser import NodePreprocessor
from statipy.core.abstract_object import (AbstractObject,
                                          Int, Str, List, Tuple, Set, Dict, Bool, Slice,
                                          Undefined)

from statipy.core.basic_func import (py_add, py_sub, py_mul, py_div, py_floordiv, py_mod, py_pow, py_lshift, py_rshift,
                                     py_or, py_xor, py_and, py_matmul,
                                     py_inplace_add, py_inplace_sub, py_inplace_mul, py_inplace_div,
                                     py_inplace_floordiv, py_inplace_mod, py_inplace_pow, py_inplace_lshift,
                                     py_inplace_rshift, py_inplace_or, py_inplace_xor, py_inplace_and,
                                     py_inplace_matmul,
                                     py_call,
                                     py_getattr, py_setattr, py_getattr_string, py_setattr_string,
                                     py_get_iter, py_iter_next,
                                     py_negative, py_positive, py_invert)

from statipy.core.environment import Environment
import statipy.errors as errors

from typing import Any


class Typer(NodeTransformer):
    def __init__(self, code: str, env: Environment = None):
        self.t_ast = NodePreprocessor(code).make_ast()
        if env is None:
            env = Environment(self.t_ast)
        self.env = env
        self.ignore_vars = set()

    def analyze(self) -> Typedmod:
        self.visit(self.t_ast)
        return self.t_ast

    def assign(self, assign_node: TypedAST, target: Typedexpr, value: AbstractObject):
        match target:
            case TypedName(id=name):
                self.env.assign_variable(assign_node, name, value)
            case TypedSubscript(value=t_value, slice=slice_):
                self.assign_subscript(t_value, slice_, value)
            case TypedAttribute(value=t_value, attr=attr):
                self.assign_attribute(t_value, attr, value)
            case TypedTuple(elts=elts):
                raise errors.Mijissou
            case _:
                raise errors.Mijissou

    def assign_subscript(self, target: Typedexpr, slice_: Typedexpr, value: AbstractObject):
        if not target.is_builtin:
            raise errors.Mijissou
        match slice_:
            case TypedSlice(lower=lower, upper=upper, step=step):
                raise errors.Mijissou
            case _:
                if isinstance(target, List):
                    target.special_attr["elt"].get_obj().unification(value)
                elif isinstance(target, Dict):
                    target.special_attr["key"].get_obj().unification(slice_)
                    target.special_attr["value"].get_obj().unification(value)
                else:
                    raise errors.Mijissou

    def assign_attribute(self, target: Typedexpr, attr: str, value: AbstractObject):
        raise errors.Mijissou

    def visit_TypedConstant(self, node: TypedConstant) -> TypedConstant:
        match node.value:
            case int():
                res = Int().create_instance()
            case str():
                res = Str().create_instance()
            case _:
                raise errors.Mijissou(repr(node.value))

        node.abstract_object = res

        return node

    def visit_TypedFormattedValue(self, node: TypedFormattedValue) -> TypedFormattedValue:
        self.generic_visit(node)
        node.abstract_object = Str().create_instance()
        return node

    def visit_TypedJoinedStr(self, node: TypedJoinedStr) -> TypedJoinedStr:
        self.generic_visit(node)
        node.abstract_object = Str().create_instance()
        return node

    def visit_TypedList(self, node: TypedList) -> TypedList:
        self.generic_visit(node)
        a_objects = [elt.abstract_object.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = List().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_TypedTuple(self, node: TypedTuple) -> TypedTuple:
        self.generic_visit(node)
        a_objects = [elt.abstract_object.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = Tuple().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_TypedSet(self, node: TypedSet) -> TypedSet:
        self.generic_visit(node)
        a_objects = [elt.abstract_object.get_obj() for elt in node.elts]
        for obj in a_objects:
            obj.unification(a_objects[0].get_obj())
        res = Set().create_instance()
        res.special_attr["elt"] = a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_TypedDict(self, node: TypedDict) -> TypedDict:
        self.generic_visit(node)
        key_a_objects = [elt.abstract_object.get_obj() for elt in node.keys]
        value_a_objects = [elt.abstract_object.get_obj() for elt in node.values]
        for obj in key_a_objects:
            obj.unification(key_a_objects[0].get_obj())
        for obj in value_a_objects:
            obj.unification(value_a_objects[0].get_obj())
        res = Dict().create_instance()
        res.special_attr["key"] = key_a_objects[0].get_obj()
        res.special_attr["value"] = value_a_objects[0].get_obj()
        node.abstract_object = res
        return node

    def visit_TypedName(self, node: TypedName) -> TypedName:
        if node.id in self.ignore_vars:
            return node
        res = self.env.get_variable(node, node.id)
        node.abstract_object = res
        return node

    def visit_TypedStarred(self, node: TypedStarred) -> TypedStarred:
        self.generic_visit(node)
        res = List().create_instance()
        res.special_attr["elt"] = node.value.abstract_object.get_obj()
        node.abstract_object = res
        # ?
        return node

    def visit_TypedExpr(self, node: TypedExpr) -> TypedExpr:
        self.generic_visit(node)
        return node

    def visit_TypedUnaryOp(self, node: TypedUnaryOp) -> TypedUnaryOp:
        self.generic_visit(node)
        match node.op:
            case Not():
                # ToDo: __bool__ の評価
                res = Bool().create_instance()
            case USub():
                res = py_negative(self.env, node.operand.abstract_object.get_obj())
            case UAdd():
                res = py_positive(self.env, node.operand.abstract_object.get_obj())
            case Invert():
                res = py_invert(self.env, node.operand.abstract_object.get_obj())
            case _:
                raise Exception
        node.abstract_object = res
        return node

    def visit_TypedBinOp(self, node: TypedBinOp) -> TypedBinOp:
        self.generic_visit(node)
        match node.op:
            case Add():
                res = py_add(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case Sub():
                res = py_sub(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case Mult():
                res = py_mul(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case Div():
                res = py_div(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case FloorDiv():
                res = py_floordiv(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case Mod():
                res = py_mod(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case Pow():
                res = py_pow(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case LShift():
                res = py_lshift(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case RShift():
                res = py_rshift(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case BitOr():
                res = py_or(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case BitXor():
                res = py_xor(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case BitAnd():
                res = py_and(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case MatMult():
                res = py_matmul(self.env, node.left.abstract_object.get_obj(), node.right.abstract_object.get_obj())
            case _:
                raise Exception
        node.abstract_object = res
        return node

    def visit_TypedBoolOp(self, node: TypedBoolOp) -> TypedBoolOp:
        # ToDo: いい感じのエラーメッセージを出す
        self.generic_visit(node)
        first_obj = node.values[0].abstract_object.get_obj()
        for value in node.values:
            value.abstract_object.get_obj().unification(first_obj)
        node.abstract_object = first_obj
        return node

    def visit_TypedCompare(self, node: TypedCompare) -> TypedCompare:
        self.generic_visit(node)
        # ToDo: __eq__とかの評価をする
        res = Bool().create_instance()
        node.abstract_object = res
        return node

    def visit_TypedCall(self, node: TypedCall) -> TypedCall:
        self.generic_visit(node)
        if node.keywords:
            raise errors.Mijissou
        if any(isinstance(arg, TypedStarred) for arg in node.args):
            raise errors.Mijissou

        args = [arg.abstract_object.get_obj() for arg in node.args]
        res = py_call(self.env, node.func.abstract_object.get_obj(), args, {})
        node.abstract_object = res
        return node

    def visit_TypedIfExp(self, node: TypedIfExp) -> TypedIfExp:
        self.generic_visit(node)
        # ToDo: node.testの__bool__を評価する
        body, orelse = node.body.abstract_object.get_obj(), node.orelse.abstract_object.get_obj()
        body.unification(orelse)
        node.abstract_object = body.get_obj()
        return node

    def visit_TypedAttribute(self, node: TypedAttribute) -> TypedAttribute:
        self.generic_visit(node)
        if not isinstance(node.attr, TypedConstant):
            raise errors.Mijissou
        attr = node.attr.value
        assert isinstance(attr, str)

        res = py_getattr_string(self.env, node.value.abstract_object.get_obj(), attr)
        node.abstract_object = res
        return node

    def visit_TypedNamedExpr(self, node: TypedNamedExpr) -> TypedNamedExpr:
        self.generic_visit(node)
        self.assign(node, node.target, node.value.abstract_object.get_obj())
        node.abstract_object = node.target.abstract_object.get_obj()
        return node

    def visit_TypedSubscript(self, node: TypedSubscript) -> TypedSubscript:
        self.generic_visit(node)
        if isinstance(node.slice, TypedSlice):
            raise errors.Mijissou
        val = node.value.abstract_object.get_obj()
        if not val.is_builtin:
            raise errors.Mijissou

        if isinstance(val, (List, Tuple)):
            res = val.special_attr["elt"].get_obj()
        elif isinstance(val, Dict):
            val.special_attr["key"].unification(node.slice.value.abstract_object.get_obj())
            res = val.special_attr["item"].get_obj()
        else:
            raise errors.Mijissou

        node.abstract_object = res
        return node

    def visit_TypedSlice(self, node: TypedSlice) -> TypedSlice:
        # index? あたりを評価しないといけなさそう
        self.generic_visit(node)
        res = Slice().create_instance()
        node.abstract_object = res
        return node

    def visit_TypedListComp(self, node: TypedListComp) -> TypedListComp:
        raise errors.Mijissou

    def visit_TypedSetComp(self, node: TypedSetComp) -> TypedSetComp:
        raise errors.Mijissou

    def visit_TypedGeneratorExp(self, node: TypedGeneratorExp) -> TypedGeneratorExp:
        raise errors.Mijissou

    def visit_TypedDictComp(self, node: TypedDictComp) -> TypedDictComp:
        raise errors.Mijissou

    def visit_Typedcomprehension(self, node: Typedcomprehension) -> Typedcomprehension:
        raise errors.Mijissou

    def visit_TypedAssign(self, node: TypedAssign) -> TypedAssign:
        tree = [node.targets]
        now_vars = []
        while tree:
            now = tree.pop()
            if isinstance(now, list):
                tree.extend(now)
            elif isinstance(now, TypedTuple):
                tree.extend(now.elts)
            elif isinstance(now, TypedName):
                self.ignore_vars.add(now.id)
                now_vars.append(now.id)
            elif isinstance(now, TypedStarred) and isinstance(now.value, ast.Name):
                self.ignore_vars.add(now.value.id)
                now_vars.append(now.value.id)

        self.generic_visit(node)
        for target in node.targets:
            self.assign(node, target, node.value.abstract_object.get_obj())

        for var in now_vars:
            self.ignore_vars.remove(var)

        node.abstract_object = node.value.abstract_object.get_obj()
        return node

    def visit_TypedAnnAssign(self, node: TypedAnnAssign) -> TypedAnnAssign:
        self.generic_visit(node)
        # annotation を考慮する機能はあると嬉しそうだよね
        self.assign(node, node.target, node.value.abstract_object.get_obj())
        node.abstract_object = node.target.abstract_object.get_obj()
        return node

    def visit_TypedAugAssign(self, node: TypedAugAssign) -> TypedAugAssign:
        self.generic_visit(node)
        match node.op:
            case Add():
                res = py_inplace_add(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case Sub():
                res = py_inplace_sub(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case Mult():
                res = py_inplace_mul(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case Div():
                res = py_inplace_div(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case FloorDiv():
                res = py_inplace_floordiv(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case Mod():
                res = py_inplace_mod(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case Pow():
                res = py_inplace_pow(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case LShift():
                res = py_inplace_lshift(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case RShift():
                res = py_inplace_rshift(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case BitOr():
                res = py_inplace_or(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case BitXor():
                res = py_inplace_xor(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case BitAnd():
                res = py_inplace_and(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case MatMult():
                res = py_inplace_matmul(self.env, node.target.abstract_object.get_obj(), node.value.abstract_object.get_obj())
            case _:
                raise Exception

        self.env.assign_variable(node, node.target.id, res)
        node.abstract_object = res
        return node

    def visit_TypedRaise(self, node: TypedRaise) -> TypedRaise:
        raise errors.Mijissou

    def visit_TypedAssert(self, node: TypedAssert) -> TypedAssert:
        raise errors.Mijissou

    def visit_TypedDelete(self, node: TypedDelete) -> TypedDelete:
        raise errors.Mijissou  # あんま使わんからな

    def visit_TypedPass(self, node: TypedPass) -> TypedPass:
        return node

    def visit_TypedImport(self, node: TypedImport) -> TypedImport:
        raise errors.Mijissou

    def visit_TypedImportFrom(self, node: TypedImportFrom) -> TypedImportFrom:
        raise errors.Mijissou

    def visit_Typedalias(self, node: Typedalias) -> Typedalias:
        raise errors.Mijissou

    def visit_TypedIf(self, node: TypedIf) -> TypedIf:
        test = self.visit(node.test)  # __bool__ を評価しないといけない

        self.env.step_in(node, node.body)
        for stmt in node.body:
            self.visit(stmt)
        self.env.step_out()

        self.env.step_in(node, node.orelse)
        for stmt in node.orelse:
            self.visit(stmt)
        self.env.step_out()

        return node

    def visit_TypedFor(self, node: TypedFor) -> TypedFor:
        self.env.step_in(node, node.body)
        iter_obj = py_get_iter(self.env, node.iter.abstract_object.get_obj())
        item = py_iter_next(self.env, iter_obj)
        self.assign(node, node.target, item)
        for stmt in node.body:
            self.visit(stmt)
        self.env.step_out()

        self.env.step_in(node, node.orelse)
        for stmt in node.orelse:
            self.visit(stmt)
        self.env.step_out()

        return node

    def visit_TypedWhile(self, node: TypedWhile) -> TypedWhile:
        test = self.visit(node.test)  # __bool__ を評価しないといけない

        self.env.step_in(node, node.body)
        for stmt in node.body:
            self.visit(stmt)
        self.env.step_out()

        self.env.step_in(node, node.orelse)
        for stmt in node.orelse:
            self.visit(stmt)
        self.env.step_out()

        return node

    def visit_TypedBreak(self, node: TypedBreak) -> TypedBreak:
        return node

    def visit_TypedContinue(self, node: TypedContinue) -> TypedContinue:
        return node

    def visit_TypedTry(self, node: TypedTry) -> TypedTry:
        raise errors.Mijissou

    def visit_TypedExceptHandler(self, node: TypedExceptHandler) -> TypedExceptHandler:
        raise errors.Mijissou

    def visit_TypedWith(self, node: TypedWith) -> TypedWith:
        raise errors.Mijissou

    def visit_Typedwithitem(self, node: Typedwithitem) -> Typedwithitem:
        raise errors.Mijissou

    def visit_TypedMatch(self, node: TypedMatch) -> TypedMatch:
        raise errors.Mijissou

    def visit_Typedmatch_case(self, node: Typedmatch_case) -> Typedmatch_case:
        raise errors.Mijissou

    def visit_TypedMatchValue(self, node: TypedMatchValue) -> TypedMatchValue:
        raise errors.Mijissou

    def visit_TypedMatchSingleton(self, node: TypedMatchSingleton) -> TypedMatchSingleton:
        raise errors.Mijissou

    def visit_TypedMatchSequence(self, node: TypedMatchSequence) -> TypedMatchSequence:
        raise errors.Mijissou

    def visit_TypedMatchStar(self, node: TypedMatchStar) -> TypedMatchStar:
        raise errors.Mijissou

    def visit_TypedMatchMapping(self, node: TypedMatchMapping) -> TypedMatchMapping:
        raise errors.Mijissou

    def visit_TypedMatchClass(self, node: TypedMatchClass) -> TypedMatchClass:
        raise errors.Mijissou

    def visit_TypedMatchAs(self, node: TypedMatchAs) -> TypedMatchAs:
        raise errors.Mijissou

    def visit_TypedMatchOr(self, node: TypedMatchOr) -> TypedMatchOr:
        raise errors.Mijissou

    def visit_TypedFunctionDef(self, node: TypedFunctionDef) -> TypedFunctionDef:
        raise errors.Mijissou

    def visit_TypedLambda(self, node: TypedLambda) -> TypedLambda:
        raise errors.Mijissou

    def visit_Typedarguments(self, node: Typedarguments) -> Typedarguments:
        raise errors.Mijissou

    def visit_Typedarg(self, node: Typedarg) -> Typedarg:
        raise errors.Mijissou

    def visit_TypedReturn(self, node: TypedReturn) -> TypedReturn:
        raise errors.Mijissou

    def visit_TypedYield(self, node: TypedYield) -> TypedYield:
        raise errors.Mijissou

    def visit_TypedYieldFrom(self, node: TypedYieldFrom) -> TypedYieldFrom:
        raise errors.Mijissou

    def visit_TypedGlobal(self, node: TypedGlobal) -> TypedGlobal:
        raise errors.Mijissou

    def visit_TypedNonlocal(self, node: TypedNonlocal) -> TypedNonlocal:
        raise errors.Mijissou

    def visit_TypedClassDef(self, node: TypedClassDef) -> TypedClassDef:
        raise errors.Mijissou

    #  def visit_TypedAsyncFunctionDef(self, node: TypedAsyncFunctionDef) -> TypedAsyncFunctionDef:
    #      raise errors.Mijissou

    #  def visit_TypedAwait(self, node: TypedAwait) -> TypedAwait:
    #      raise errors.Mijissou

    #  def visit_TypedAsyncFor(self, node: TypedAsyncFor) -> TypedAsyncFor:
    #      raise errors.Mijissou

    #  def visit_TypedAsyncWith(self, node: TypedAsyncWith) -> TypedAsyncWith:
    #      raise errors.Mijissou

    def visit_TypedModule(self, node: TypedModule) -> TypedModule:
        self.generic_visit(node)
        return node
