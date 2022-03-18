from __future__ import annotations

from statipy.core.abstract_object import AbstractObject
from typing import Optional

import ast


class TypedAST(ast.AST):
    pass


class operator(ast.operator, TypedAST):
    # 演算子の位置が知りたいので
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(operator, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class Add(ast.Add, operator):
    pass


class Typedalias(ast.alias, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str, asname: Optional[str]):
        super(Typedalias, self).__init__(name, asname)
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class boolop(ast.boolop, TypedAST):
    # 演算子の位置が知りたいので
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(boolop, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class And(ast.And, boolop):
    pass


class Typedstmt(ast.stmt, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(Typedstmt, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class TypedAnnAssign(ast.AnnAssign, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, annotation: Typedexpr, value: Typedexpr, simple: bool):
        super(TypedAnnAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target = target
        self.annotation = annotation
        self.value = value
        self.simple = simple


class Typedarg(ast.arg, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 arg: str, annotation: Typedexpr, type_comment: Optional[str]):
        super(Typedarg, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.arg = arg
        self.annotation = annotation
        self.type_comment = type_comment


class Typedarguments(ast.arguments, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 posonlyargs: list[Typedarg], args: list[Typedarg], vararg: Typedarg, kwonlyargs: list[Typedarg],
                 kw_defaults: list[Typedexpr], kwarg: Typedarg, defaults: list[Typedexpr]):
        super(Typedarguments, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.posonlyargs = posonlyargs
        self.args = args
        self.vararg = vararg
        self.kwonlyargs = kwonlyargs
        self.kw_defaults = kw_defaults
        self.kwarg = kwarg
        self.defaults = defaults


class TypedAssert(ast.Assert, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, msg: Typedexpr):
        super(TypedAssert, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test = test
        self.msg = msg


class TypedAssign(ast.Assign, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 targets: list[Typedexpr], value: Typedexpr, type_comment: Optional[str]):
        super(TypedAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.targets = targets
        self.value = value
        self.type_comment = type_comment


# AsyncFor
# AsyncFunctionDef
# AsyncWith


class Typedexpr(ast.expr, TypedAST):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.abstract_obj: Optional[AbstractObject] = None


class TypedAttribute(ast.Attribute, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, attr: str, ctx: ast.expr_context):
        super(TypedAttribute, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.value = value
        self.attr = attr
        self.ctx = ctx


class TypedAugAssign(ast.AugAssign, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, op: operator, value: Typedexpr):
        super(TypedAugAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target = target
        self.op = op
        self.value = value


# Await


class TypedBinOp(ast.BinOp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 left: Typedexpr, op: operator, right: Typedexpr):
        super(TypedBinOp, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.left = left
        self.op = op
        self.right = right


class BitAnd(ast.BitAnd, operator):
    pass


class BitOr(ast.BitOr, operator):
    pass


class BitXor(ast.BitXor, operator):
    pass


class TypedBoolOp(ast.BoolOp, Typedexpr):
    # ast.BoolOpと違い、opをリストで複数持ちます。これはTypedBoolOperatorが演算子の位置を持つからです。
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 ops: list[boolop], values: list[Typedexpr]):
        super(TypedBoolOp, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.ops = ops
        self.values = values


class TypedBreak(ast.Break, Typedstmt):
    # これはastのものと変わらないから必要ないかも
    pass


class TypedCall(ast.Call, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 func: Typedexpr, args: list[Typedexpr], keywords: list[Typedkeyword]):
        super(TypedCall, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.func = func
        self.args = args
        self.keywords = keywords


class TypedClassDef(ast.ClassDef, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str, bases: list[Typedexpr], keywords: list[Typedkeyword],
                 body: list[Typedstmt], decorator_list: list[Typedexpr]):
        super(TypedClassDef, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.name = name
        self.bases = bases
        self.keywords = keywords
        self.body = body
        self.decorator_list = decorator_list


class cmpop(ast.cmpop, operator):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(cmpop, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class TypedCompare(ast.Compare, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 left: Typedexpr, ops: list[cmpop], comparators: list[Typedexpr]):
        super(TypedCompare, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.left = left
        self.ops = ops
        self.comparators = comparators


class Typedcomprehension(ast.comprehension, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, iter: Typedexpr, ifs: list[Typedexpr], is_async: bool):
        super(Typedcomprehension, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.target = target
        self.iter = iter
        self.ifs = ifs
        self.is_async = is_async


class TypedConstant(ast.Constant, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: object):
        super(TypedConstant, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.value = value


class TypedContinue(ast.Continue, Typedstmt):
    pass


# expr_context


class TypedDelete(ast.Delete, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 targets: list[Typedexpr]):
        super(TypedDelete, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.targets = targets


class TypedDict(ast.Dict, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 keys: list[Typedexpr], values: list[Typedexpr]):
        super(TypedDict, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.keys = keys
        self.values = values


class TypedDictComp(ast.DictComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 key: Typedexpr, value: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedDictComp, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.key = key
        self.value = value
        self.generators = generators


class Div(ast.Div, operator):
    pass


class Eq(ast.Eq, operator):
    pass


class Typedexcepthandler(ast.excepthandler, TypedAST):
    # これなんですか？
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(Typedexcepthandler, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class TypedExceptHandler(ast.ExceptHandler, Typedexcepthandler):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 type_: Typedexpr, name: str, body: list[Typedstmt]):
        super(TypedExceptHandler, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.type = type_
        self.name = name
        self.body = body


class TypedExpr(ast.Expr, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedExpr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class Typedmod(ast.mod, TypedAST):
    pass


class TypedExpression(ast.Expression, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: Typedexpr):
        super(TypedExpression, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body = body


class FloorDiv(ast.FloorDiv, operator):
    pass


class TypedFor(ast.For, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, iter: Typedexpr, body: list[Typedstmt], orelse: list[Typedstmt]):
        super(TypedFor, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target = target
        self.iter = iter
        self.body = body
        self.orelse = orelse


class TypedFormattedValue(ast.FormattedValue, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, conversion: int, format_spec: Typedexpr):
        super(TypedFormattedValue, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value
        self.conversion = conversion
        self.format_spec = format_spec


class TypedFunctionDef(ast.FunctionDef, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str, args: Typedarguments, body: list[Typedstmt], decorator_list: list[Typedexpr],
                 returns: Typedexpr):
        super(TypedFunctionDef, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.name = name
        self.args = args
        self.body = body
        self.decorator_list = decorator_list
        self.returns = returns


class TypedFunctionType(ast.FunctionType, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 argtypes: Typedarguments, returns: Typedexpr):
        super(TypedFunctionType, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.argtypes = argtypes
        self.returns = returns


class TypedGeneratorExp(ast.GeneratorExp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedGeneratorExp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt = elt
        self.generators = generators


class TypedGlobal(ast.Global, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 names: list[str]):
        super(TypedGlobal, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.names = names


class Gt(ast.Gt, operator):
    pass


class GtE(ast.GtE, operator):
    pass


class TypedIf(ast.If, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, body: list[Typedstmt], orelse: list[Typedstmt]):
        super(TypedIf, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test = test
        self.body = body
        self.orelse = orelse


class TypedIfExp(ast.IfExp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, body: Typedexpr, orelse: Typedexpr):
        super(TypedIfExp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test = test
        self.body = body
        self.orelse = orelse


class TypedImport(ast.Import, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 names: list[Typedalias]):
        super(TypedImport, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.names = names


class TypedImportFrom(ast.ImportFrom, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 module: str, names: list[Typedalias], level: int):
        super(TypedImportFrom, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.module = module
        self.names = names
        self.level = level


class In(ast.In, cmpop):
    pass


class TypedInteractive(ast.Interactive, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt]):
        super(TypedInteractive, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body = body


class unaryop(ast.unaryop, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(unaryop, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class Invert(ast.Invert, unaryop):
    pass


class Is(ast.Is, cmpop):
    pass


class IsNot(ast.IsNot, cmpop):
    pass


class JoinedStr(ast.JoinedStr, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 values: list[Typedexpr]):
        super(JoinedStr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.values = values


class Typedkeyword(ast.keyword, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 arg: str, value: Typedexpr):
        super(Typedkeyword, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.arg = arg
        self.value = value


class TypedLambda(ast.Lambda, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 args: Typedarguments, body: Typedexpr):
        super(TypedLambda, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.args = args
        self.body = body


class TypedList(ast.List, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr], ctx: ast.expr_context):
        super(TypedList, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts = elts
        self.ctx = ctx


class TypedListComp(ast.ListComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedListComp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt = elt
        self.generators = generators


class LShift(ast.LShift, operator):
    pass


class Lt(ast.Lt, cmpop):
    pass


class LtE(ast.LtE, cmpop):
    pass


class Match(ast.Match, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 subject: Typedexpr, cases: list[Typedmatch_case]):
        super(Match, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.subject = subject
        self.cases = cases


class Typedpattern(ast.pattern, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(Typedpattern, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class TypedMatchAs(ast.MatchAs, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 pattern: Typedpattern, name: str):
        super(TypedMatchAs, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.pattern = pattern
        self.name = name


class TypedMatchClass(ast.MatchClass, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 cls: Typedexpr, patterns: list[Typedpattern], kwd_attrs: list[str], kwd_patterns: list[Typedpattern]):
        super(TypedMatchClass, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.cls = cls
        self.patterns = patterns
        self.kwd_attrs = kwd_attrs
        self.kwd_patterns = kwd_patterns


class TypedMatchMapping(ast.MatchMapping, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 keys: list[Typedexpr], patterns: list[Typedpattern], rest: Optional[str]):
        super(TypedMatchMapping, self).__init__(lineno, end_lineno, col_offset, end_col_offset)


class TypedMatchOr(ast.MatchOr, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 patterns: list[Typedpattern]):
        super(TypedMatchOr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.patterns = patterns


class TypedMatchSequence(ast.MatchSequence, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 patterns: list[Typedpattern]):
        super(TypedMatchSequence, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.patterns = patterns


class TypedMatchSingleton(ast.MatchSingleton, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: bool | None):
        super(TypedMatchSingleton, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class TypedMatchStar(ast.MatchStar, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str):
        super(TypedMatchStar, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.name = name


class TypedMatchValue(ast.MatchValue, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedMatchValue, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class Typedmatch_case(ast.match_case, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 pattern: Typedpattern, guard: Typedexpr, body: list[Typedstmt]):
        super(Typedmatch_case, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.pattern = pattern
        self.guard = guard
        self.body = body


class MatMult(ast.MatMult, operator):
    pass


class Mod(ast.Mod, operator):
    pass


class TypedModule(ast.Module, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt], type_ignores: list[ast.TypeIgnore]):
        super(TypedModule, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body = body
        self.type_ignores = type_ignores


class Mult(ast.Mult, operator):
    pass


class TypedName(ast.Name, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 id: str, ctx: ast.expr_context):
        super(TypedName, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.id = id
        self.ctx = ctx


class TypedNamedExpr(ast.NamedExpr, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, value: Typedexpr):
        super(TypedNamedExpr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target = target
        self.value = value


class TypedNonlocal(ast.Nonlocal, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 names: list[str]):
        super(TypedNonlocal, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.names = names


class Not(ast.Not, unaryop):
    pass


class NotEq(ast.NotEq, cmpop):
    pass


class NotIn(ast.NotIn, cmpop):
    pass


class Or(ast.Or, boolop):
    pass


class TypedPass(ast.Pass, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(TypedPass, self).__init__(lineno, end_lineno, col_offset, end_col_offset)


class Pow(ast.Pow, operator):
    pass


class TypedRaise(ast.Raise, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 exc: Typedexpr, cause: Typedexpr):
        super(TypedRaise, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.exc = exc
        self.cause = cause


class TypedReturn(ast.Return, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedReturn, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class RShift(ast.RShift, operator):
    pass


class TypedSet(ast.Set, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr]):
        super(TypedSet, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts = elts


class TypedSetComp(ast.SetComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedSetComp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt = elt
        self.generators = generators


class TypedSlice(ast.Slice, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 lower: Typedexpr, upper: Typedexpr, step: Typedexpr):
        super(TypedSlice, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.lower = lower
        self.upper = upper
        self.step = step


class TypedStarred(ast.Starred, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, ctx: ast.expr_context):
        super(TypedStarred, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value
        self.ctx = ctx


class Sub(ast.Sub, operator):
    pass


class TypedSubscript(ast.Subscript, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, slice_: Typedexpr, ctx: ast.expr_context):
        super(TypedSubscript, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value
        self.slice = slice_
        self.ctx = ctx


class TypedTry(ast.Try, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt], handlers: list[TypedExceptHandler],
                 orelse: list[Typedstmt], finalbody: list[Typedstmt]):
        super(TypedTry, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body = body
        self.handlers = handlers
        self.orelse = orelse
        self.finalbody = finalbody


class TypedTuple(ast.Tuple, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr], ctx: ast.expr_context):
        super(TypedTuple, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts = elts
        self.ctx = ctx


# type_ignore


class UAdd(ast.UAdd, unaryop):
    pass


class TypedUnaryOp(ast.UnaryOp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 op: unaryop, operand: Typedexpr):
        super(TypedUnaryOp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.op = op
        self.operand = operand


class USub(ast.USub, unaryop):
    pass


class TypedWhile(ast.While, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, body: list[Typedstmt], orelse: list[Typedstmt]):
        super(TypedWhile, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test = test
        self.body = body
        self.orelse = orelse


class TypedWith(ast.With, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 items: list[Typedwithitem], body: list[Typedstmt], type_comment: Optional[str]):
        super(TypedWith, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.items = items
        self.body = body
        self.type_comment = type_comment


class Typedwithitem(ast.withitem, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 context_expr: Typedexpr, optional_vars: Typedexpr):
        super(Typedwithitem, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.context_expr = context_expr
        self.optional_vars = optional_vars


class TypedYield(ast.Yield, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedYield, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class TypedYieldFrom(ast.YieldFrom, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedYieldFrom, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value
