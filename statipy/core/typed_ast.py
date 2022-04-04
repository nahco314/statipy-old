from __future__ import annotations

from statipy.core.abstract_object import AbstractObject
from typing import Optional

import ast


class TypedAST(ast.AST):
    def get_pos(self) -> tuple[int, int, int, int]:
        if not hasattr(self, 'lineno'):
            raise Exception('AST node has no lineno attribute')
        else:
            return self.lineno, self.col_offset, self.end_lineno, self.end_col_offset


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
                 target: Typedexpr, annotation: Typedexpr, value: Typedexpr, simple: int):
        super(TypedAnnAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target: Typedexpr = target
        self.annotation: Typedexpr = annotation
        self.value: Typedexpr = value
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
        self.annotation: Typedexpr = annotation
        self.type_comment = type_comment


class Typedarguments(ast.arguments, TypedAST):
    def __init__(self, posonlyargs: list[Typedarg], args: list[Typedarg], vararg: Typedarg,
                 kwonlyargs: list[Typedarg], kw_defaults: list[Typedexpr], kwarg: Typedarg,
                 defaults: list[Typedexpr]):
        super(Typedarguments, self).__init__()
        self.posonlyargs: list[Typedarg] = posonlyargs
        self.args: list[Typedarg] = args
        self.vararg: Typedarg = vararg
        self.kwonlyargs: list[Typedarg] = kwonlyargs
        self.kw_defaults: list[Typedexpr] = kw_defaults
        self.kwarg: Typedarg = kwarg
        self.defaults: list[Typedexpr] = defaults


class TypedAssert(ast.Assert, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, msg: Typedexpr):
        super(TypedAssert, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test: Typedexpr = test
        self.msg: Typedexpr = msg


class TypedAssign(ast.Assign, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 targets: list[Typedexpr], value: Typedexpr, type_comment: Optional[str]):
        super(TypedAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.targets: list[Typedexpr] = targets
        self.value: Typedexpr = value
        self.type_comment = type_comment


# AsyncFor
# AsyncFunctionDef
# AsyncWith


class Typedexpr(ast.expr, TypedAST):
    def __init__(self,  lineno: int, end_lineno: int, col_offset: int, end_col_offset: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.abstract_obj: Optional[AbstractObject] = None


class TypedAttribute(ast.Attribute, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, attr: str, ctx: ast.expr_context):
        super(TypedAttribute, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value
        self.attr = attr
        self.ctx = ctx


class TypedAugAssign(ast.AugAssign, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, op: operator, value: Typedexpr):
        super(TypedAugAssign, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target: Typedexpr = target
        self.op: operator = op
        self.value: Typedexpr = value


# Await


class TypedBinOp(ast.BinOp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 left: Typedexpr, op: operator, right: Typedexpr):
        super(TypedBinOp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.left: Typedexpr = left
        self.op: operator = op
        self.right: Typedexpr = right


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
        super(TypedBoolOp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.ops: list[boolop] = ops
        self.values: list[Typedexpr] = values


class TypedBreak(ast.Break, Typedstmt):
    # これはastのものと変わらないから必要ないかも
    pass


class TypedCall(ast.Call, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 func: Typedexpr, args: list[Typedexpr], keywords: list[Typedkeyword]):
        super(TypedCall, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.func: Typedexpr = func
        self.args: list[Typedexpr] = args
        self.keywords: list[Typedkeyword] = keywords


class TypedClassDef(ast.ClassDef, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str, bases: list[Typedexpr], keywords: list[Typedkeyword],
                 body: list[Typedstmt], decorator_list: list[Typedexpr]):
        super(TypedClassDef, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.name = name
        self.bases: list[Typedexpr] = bases
        self.keywords: list[Typedkeyword] = keywords
        self.body: list[Typedstmt] = body
        self.decorator_list: list[Typedexpr] = decorator_list


class cmpop(ast.cmpop, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int):
        super(cmpop, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset


class TypedCompare(ast.Compare, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 left: Typedexpr, ops: list[cmpop], comparators: list[Typedexpr]):
        super(TypedCompare, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.left: Typedexpr = left
        self.ops: list[cmpop] = ops
        self.comparators: list[Typedexpr] = comparators


class Typedcomprehension(ast.comprehension, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, iter_: Typedexpr, ifs: list[Typedexpr], is_async: bool):
        super(Typedcomprehension, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.target: Typedexpr = target
        self.iter: Typedexpr = iter_
        self.ifs: list[Typedexpr] = ifs
        self.is_async = is_async


class TypedConstant(ast.Constant, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: object):
        super(TypedConstant, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value = value


class TypedContinue(ast.Continue, Typedstmt):
    pass


# expr_context


class TypedDelete(ast.Delete, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 targets: list[Typedexpr]):
        super(TypedDelete, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.targets: list[Typedexpr] = targets


class TypedDict(ast.Dict, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 keys: list[Typedexpr], values: list[Typedexpr]):
        super(TypedDict, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.keys: list[Typedexpr] = keys
        self.values: list[Typedexpr] = values


class TypedDictComp(ast.DictComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 key: Typedexpr, value: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedDictComp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.key: Typedexpr = key
        self.value: Typedexpr = value
        self.generators: list[Typedcomprehension] = generators


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
        self.type: Typedexpr = type_
        self.name = name
        self.body: list[Typedstmt] = body


class TypedExpr(ast.Expr, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedExpr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value


class Typedmod(ast.mod, TypedAST):
    pass


class TypedExpression(ast.Expression, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: Typedexpr):
        super(TypedExpression, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body: Typedexpr = body


class FloorDiv(ast.FloorDiv, operator):
    pass


class TypedFor(ast.For, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 target: Typedexpr, iter_: Typedexpr, body: list[Typedstmt], orelse: list[Typedstmt],
                 type_comment: Optional[str]):
        super(TypedFor, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.target: Typedexpr = target
        self.iter: Typedexpr = iter_
        self.body: list[Typedstmt] = body
        self.orelse: list[Typedstmt] = orelse
        self.type_comment = type_comment


class TypedFormattedValue(ast.FormattedValue, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, conversion: int, format_spec: Typedexpr):
        super(TypedFormattedValue, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value
        self.conversion = conversion
        self.format_spec: Typedexpr = format_spec


class TypedFunctionDef(ast.FunctionDef, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 name: str, args: Typedarguments, body: list[Typedstmt], decorator_list: list[Typedexpr],
                 returns: Typedexpr, type_comment: Optional[str]):
        super(TypedFunctionDef, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.name = name
        self.args: Typedarguments = args
        self.body: list[Typedstmt] = body
        self.decorator_list: list[Typedexpr] = decorator_list
        self.returns: Typedexpr = returns
        self.type_comment = type_comment


class TypedFunctionType(ast.FunctionType, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 argtypes: Typedarguments, returns: Typedexpr):
        super(TypedFunctionType, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.argtypes: Typedarguments = argtypes
        self.returns: Typedexpr = returns


class TypedGeneratorExp(ast.GeneratorExp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedGeneratorExp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt: Typedexpr = elt
        self.generators: list[Typedcomprehension] = generators


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
        self.test: Typedexpr = test
        self.body: list[Typedstmt] = body
        self.orelse: list[Typedstmt] = orelse


class TypedIfExp(ast.IfExp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, body: Typedexpr, orelse: Typedexpr):
        super(TypedIfExp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test: Typedexpr = test
        self.body: Typedexpr = body
        self.orelse: Typedexpr = orelse


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
        self.names: list[Typedalias] = names
        self.level = level


class In(ast.In, cmpop):
    pass


class TypedInteractive(ast.Interactive, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt]):
        super(TypedInteractive, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body: list[Typedstmt] = body


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


class TypedJoinedStr(ast.JoinedStr, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 values: list[Typedexpr]):
        super(TypedJoinedStr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.values: list[Typedexpr] = values


class Typedkeyword(ast.keyword, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 arg: str, value: Typedexpr):
        super(Typedkeyword, self).__init__()
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.arg = arg
        self.value: Typedexpr = value


class TypedLambda(ast.Lambda, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 args: Typedarguments, body: Typedexpr):
        super(TypedLambda, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.args: Typedarguments = args
        self.body: Typedexpr = body


class TypedList(ast.List, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr], ctx: ast.expr_context):
        super(TypedList, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts: list[Typedexpr] = elts
        self.ctx = ctx


class TypedListComp(ast.ListComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedListComp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt: Typedexpr = elt
        self.generators: list[Typedcomprehension] = generators


class LShift(ast.LShift, operator):
    pass


class Lt(ast.Lt, cmpop):
    pass


class LtE(ast.LtE, cmpop):
    pass


class TypedMatch(ast.Match, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 subject: Typedexpr, cases: list[Typedmatch_case]):
        super(TypedMatch, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.subject: Typedexpr = subject
        self.cases: list[Typedmatch_case] = cases


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
        self.pattern: Typedpattern = pattern
        self.name = name


class TypedMatchClass(ast.MatchClass, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 cls: Typedexpr, patterns: list[Typedpattern], kwd_attrs: list[str], kwd_patterns: list[Typedpattern]):
        super(TypedMatchClass, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.cls: Typedexpr = cls
        self.patterns: list[Typedpattern] = patterns
        self.kwd_attrs = kwd_attrs
        self.kwd_patterns: list[Typedpattern] = kwd_patterns


class TypedMatchMapping(ast.MatchMapping, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 keys: list[Typedexpr], patterns: list[Typedpattern], rest: Optional[str]):
        super(TypedMatchMapping, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.keys: list[Typedexpr] = keys
        self.patterns: list[Typedpattern] = patterns
        self.rest = rest


class TypedMatchOr(ast.MatchOr, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 patterns: list[Typedpattern]):
        super(TypedMatchOr, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.patterns: list[Typedpattern] = patterns


class TypedMatchSequence(ast.MatchSequence, Typedpattern):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 patterns: list[Typedpattern]):
        super(TypedMatchSequence, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.patterns: list[Typedpattern] = patterns


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
        self.value: Typedexpr = value


class Typedmatch_case(ast.match_case, TypedAST):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 pattern: Typedpattern, guard: Typedexpr, body: list[Typedstmt]):
        super(Typedmatch_case, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.pattern: Typedpattern = pattern
        self.guard: Typedexpr = guard
        self.body: list[Typedstmt] = body


class MatMult(ast.MatMult, operator):
    pass


class Mod(ast.Mod, operator):
    pass


class TypedModule(ast.Module, Typedmod):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt], type_ignores: list[ast.TypeIgnore]):
        super(TypedModule, self).__init__()
        self.body: list[Typedstmt] = body
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
        self.target: Typedexpr = target
        self.value: Typedexpr = value


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
        self.exc: Typedexpr = exc
        self.cause: Typedexpr = cause


class TypedReturn(ast.Return, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedReturn, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value


class RShift(ast.RShift, operator):
    pass


class TypedSet(ast.Set, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr]):
        super(TypedSet, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts: list[Typedexpr] = elts


class TypedSetComp(ast.SetComp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elt: Typedexpr, generators: list[Typedcomprehension]):
        super(TypedSetComp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elt: Typedexpr = elt
        self.generators: list[Typedcomprehension] = generators


class TypedSlice(ast.Slice, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 lower: Typedexpr, upper: Typedexpr, step: Typedexpr):
        super(TypedSlice, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.lower: Typedexpr = lower
        self.upper: Typedexpr = upper
        self.step: Typedexpr = step


class TypedStarred(ast.Starred, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, ctx: ast.expr_context):
        super(TypedStarred, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value
        self.ctx = ctx


class Sub(ast.Sub, operator):
    pass


class TypedSubscript(ast.Subscript, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr, slice_: Typedexpr, ctx: ast.expr_context):
        super(TypedSubscript, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value
        self.slice: Typedexpr = slice_
        self.ctx = ctx


class TypedTry(ast.Try, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 body: list[Typedstmt], handlers: list[TypedExceptHandler],
                 orelse: list[Typedstmt], finalbody: list[Typedstmt]):
        super(TypedTry, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.body: list[Typedstmt] = body
        self.handlers: list[TypedExceptHandler] = handlers
        self.orelse: list[Typedstmt] = orelse
        self.finalbody: list[Typedstmt] = finalbody


class TypedTuple(ast.Tuple, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 elts: list[Typedexpr], ctx: ast.expr_context):
        super(TypedTuple, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.elts: list[Typedexpr] = elts
        self.ctx = ctx


# type_ignore


class UAdd(ast.UAdd, unaryop):
    pass


class TypedUnaryOp(ast.UnaryOp, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 op: unaryop, operand: Typedexpr):
        super(TypedUnaryOp, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.op: unaryop = op
        self.operand: Typedexpr = operand


class USub(ast.USub, unaryop):
    pass


class TypedWhile(ast.While, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 test: Typedexpr, body: list[Typedstmt], orelse: list[Typedstmt]):
        super(TypedWhile, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.test: Typedexpr = test
        self.body: list[Typedstmt] = body
        self.orelse: list[Typedstmt] = orelse


class TypedWith(ast.With, Typedstmt):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 items: list[Typedwithitem], body: list[Typedstmt], type_comment: Optional[str]):
        super(TypedWith, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.items: list[Typedwithitem] = items
        self.body: list[Typedstmt] = body
        self.type_comment = type_comment


class Typedwithitem(ast.withitem, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 context_expr: Typedexpr, optional_vars: Typedexpr):
        super(Typedwithitem, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.context_expr: Typedexpr = context_expr
        self.optional_vars: Typedexpr = optional_vars


class TypedYield(ast.Yield, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedYield, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value


class TypedYieldFrom(ast.YieldFrom, Typedexpr):
    def __init__(self, lineno: int, end_lineno: int, col_offset: int, end_col_offset: int,
                 value: Typedexpr):
        super(TypedYieldFrom, self).__init__(lineno, end_lineno, col_offset, end_col_offset)
        self.value: Typedexpr = value
