from statipy.core.abstract_object import AbstractObject
from typing import Optional

import ast


class TypedAST(ast.AST):
    pass


class Typedexpr(ast.expr, TypedAST):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.abstract_obj: Optional[AbstractObject] = None


class Typedstmt(ast.stmt, TypedAST):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypedAttribute(ast.Attribute, Typedexpr):
    def __init__(self, value, attr, ctx):
        self.value: Typedexpr = value
        self.attr: Typedexpr = attr
        self.ctx: Typedexpr = ctx


class TypedAwait(ast.Await, Typedexpr):
    def __init__(self, value):
        self.value: Typedexpr = value


class TypedBinOp(ast.BinOp, Typedexpr):
    def __init__(self, left, op, right):
        self.left: Typedexpr = left
        self.op: Typedexpr = op
        self.right: Typedexpr = right


class TypedBoolOp(ast.BoolOp, Typedexpr):
    def __init__(self, op, values):
        self.op: Typedexpr = op
        self.values: list[Typedexpr] = values


class TypedBytes(ast.Bytes, Typedexpr):
    def __init__(self, s):
        self.s: list[Typedexpr] = s


class TypedCall(ast.Call, Typedexpr):
    def __init__(self, func, args, keywords):
        self.func: Typedexpr = func
        self.args: list[Typedexpr] = args
        self.keywords: list[Typedexpr] = keywords


class TypedCompare(ast.Compare, Typedexpr):
    def __init__(self, left, ops, comparators):
        self.left: Typedexpr = left
        self.ops: list[Typedexpr] = ops
        self.comparators: list[Typedexpr] = comparators


class TypedConstant(ast.Constant, Typedexpr):
    def __init__(self, value, kind):
        self.value: Typedexpr = value
        self.kind: Typedexpr = kind


class TypedDict(ast.Dict, Typedexpr):
    def __init__(self, keys, values):
        self.keys: list[Typedexpr] = keys
        self.values: list[Typedexpr] = values


class TypedDictComp(ast.DictComp, Typedexpr):
    def __init__(self, key, value, generators):
        self.key: Typedexpr = key
        self.value: Typedexpr = value
        self.generators: list[Typedexpr] = generators


class TypedEllipsis(ast.Ellipsis, Typedexpr):
    pass


class TypedFormattedValue(ast.FormattedValue, Typedexpr):
    def __init__(self, value, conversion, format_spec):
        self.value: Typedexpr = value
        self.conversion: Typedexpr = conversion
        self.format_spec: Typedexpr = format_spec


class TypedGeneratorExp(ast.GeneratorExp, Typedexpr):
    def __init__(self, elt, generators):
        self.elt: Typedexpr = elt
        self.generators: list[Typedexpr] = generators


class TypedIfExp(ast.IfExp, Typedexpr):
    def __init__(self, test, body, orelse):
        self.test: Typedexpr = test
        self.body: Typedexpr = body
        self.orelse: Typedexpr = orelse


class TypedJoinedStr(ast.JoinedStr, Typedexpr):
    def __init__(self, values):
        self.values: list[Typedexpr] = values


class TypedLambda(ast.Lambda, Typedexpr):
    def __init__(self, args, body):
        self.args: list[Typedexpr] = args
        self.body: Typedexpr = body


class TypedList(ast.List, Typedexpr):
    def __init__(self, elts, ctx):
        self.elts: list[Typedexpr] = elts
        self.ctx: Typedexpr = ctx


class TypedListComp(ast.ListComp, Typedexpr):
    def __init__(self, elt, generators):
        self.elt: Typedexpr = elt
        self.generators: list[Typedexpr] = generators


class TypedName(ast.Name, Typedexpr):
    def __init__(self, id, ctx):
        self.id: Typedexpr = id
        self.ctx: Typedexpr = ctx


class TypedNameConstant(ast.NameConstant, Typedexpr):
    def __init__(self, value, kind):
        self.value: Typedexpr = value
        self.kind: Typedexpr = kind


class TypedNamedExpr(ast.NamedExpr, Typedexpr):
    def __init__(self, target, value):
        self.target: Typedexpr = target
        self.value: Typedexpr = value


class TypedNum(ast.Num, Typedexpr):
    def __init__(self, n):
        self.n: Typedexpr = n


class TypedSet(ast.Set, Typedexpr):
    def __init__(self, elts):
        self.elts: list[Typedexpr] = elts


class TypedSetComp(ast.SetComp, Typedexpr):
    def __init__(self, elt, generators):
        self.elt: Typedexpr = elt
        self.generators: list[Typedexpr] = generators


class TypedSlice(ast.Slice, Typedexpr):
    def __init__(self, lower, upper, step):
        self.lower: Typedexpr = lower
        self.upper: Typedexpr = upper
        self.step: Typedexpr = step


class TypedStarred(ast.Starred, Typedexpr):
    def __init__(self, value, ctx):
        self.value: Typedexpr = value
        self.ctx: Typedexpr = ctx


class TypedStr(ast.Str, Typedexpr):
    def __init__(self, s):
        self.s: list[Typedexpr] = s


class TypedSubscript(ast.Subscript, Typedexpr):
    def __init__(self, value, slice, ctx):
        self.value: Typedexpr = value
        self.slice: Typedexpr = slice
        self.ctx: Typedexpr = ctx


class TypedTuple(ast.Tuple, Typedexpr):
    def __init__(self, elts, ctx):
        self.elts: list[Typedexpr] = elts
        self.ctx: Typedexpr = ctx


class TypedUnaryOp(ast.UnaryOp, Typedexpr):
    def __init__(self, op, operand):
        self.op: Typedexpr = op
        self.operand: Typedexpr = operand


class TypedYield(ast.Yield, Typedexpr):
    def __init__(self, value):
        self.value: Typedexpr = value


class TypedYieldFrom(ast.YieldFrom, Typedexpr):
    def __init__(self, value):
        self.value: Typedexpr = value


class TypedAnnAssign(ast.AnnAssign, Typedstmt):
    def __init__(self, target, annotation, value, simple):
        self.target: Typedstmt = target
        self.annotation: Typedstmt = annotation
        self.value: Typedstmt = value
        self.simple: Typedstmt = simple


class TypedAssert(ast.Assert, Typedstmt):
    def __init__(self, test, msg):
        self.test: Typedstmt = test
        self.msg: Typedstmt = msg


class TypedAssign(ast.Assign, Typedstmt):
    def __init__(self, targets, value, type_comment):
        self.targets: list[Typedstmt] = targets
        self.value: Typedstmt = value
        self.type_comment: Typedstmt = type_comment


class TypedAsyncFor(ast.AsyncFor, Typedstmt):
    def __init__(self, target, iter, body, orelse, type_comment):
        self.target: Typedstmt = target
        self.iter: Typedstmt = iter
        self.body: Typedstmt = body
        self.orelse: Typedstmt = orelse
        self.type_comment: Typedstmt = type_comment


class TypedAsyncFunctionDef(ast.AsyncFunctionDef, Typedstmt):
    def __init__(self, name, args, body, decorator_list, returns, type_comment):
        self.name: Typedstmt = name
        self.args: list[Typedstmt] = args
        self.body: Typedstmt = body
        self.decorator_list: Typedstmt = decorator_list
        self.returns: list[Typedstmt] = returns
        self.type_comment: Typedstmt = type_comment


class TypedAsyncWith(ast.AsyncWith, Typedstmt):
    def __init__(self, items, body, type_comment):
        self.items: list[Typedstmt] = items
        self.body: Typedstmt = body
        self.type_comment: Typedstmt = type_comment


class TypedAugAssign(ast.AugAssign, Typedstmt):
    def __init__(self, target, op, value):
        self.target: Typedstmt = target
        self.op: Typedstmt = op
        self.value: Typedstmt = value


class TypedBreak(ast.Break, Typedstmt):
    pass


class TypedClassDef(ast.ClassDef, Typedstmt):
    def __init__(self, name, bases, keywords, body, decorator_list):
        self.name: Typedstmt = name
        self.bases: list[Typedstmt] = bases
        self.keywords: list[Typedstmt] = keywords
        self.body: Typedstmt = body
        self.decorator_list: Typedstmt = decorator_list


class TypedContinue(ast.Continue, Typedstmt):
    pass


class TypedDelete(ast.Delete, Typedstmt):
    def __init__(self, targets):
        self.targets: list[Typedstmt] = targets


class TypedExpr(ast.Expr, Typedstmt):
    def __init__(self, value):
        self.value: Typedstmt = value


class TypedFor(ast.For, Typedstmt):
    def __init__(self, target, iter, body, orelse, type_comment):
        self.target: Typedstmt = target
        self.iter: Typedstmt = iter
        self.body: Typedstmt = body
        self.orelse: Typedstmt = orelse
        self.type_comment: Typedstmt = type_comment


class TypedFunctionDef(ast.FunctionDef, Typedstmt):
    def __init__(self, name, args, body, decorator_list, returns, type_comment):
        self.name: Typedstmt = name
        self.args: list[Typedstmt] = args
        self.body: Typedstmt = body
        self.decorator_list: Typedstmt = decorator_list
        self.returns: list[Typedstmt] = returns
        self.type_comment: Typedstmt = type_comment


class TypedGlobal(ast.Global, Typedstmt):
    def __init__(self, names):
        self.names: list[Typedstmt] = names


class TypedIf(ast.If, Typedstmt):
    def __init__(self, test, body, orelse):
        self.test: Typedstmt = test
        self.body: Typedstmt = body
        self.orelse: Typedstmt = orelse


class TypedImport(ast.Import, Typedstmt):
    def __init__(self, names):
        self.names: list[Typedstmt] = names


class TypedImportFrom(ast.ImportFrom, Typedstmt):
    def __init__(self, module, names, level):
        self.module: Typedstmt = module
        self.names: list[Typedstmt] = names
        self.level: Typedstmt = level


class TypedMatch(ast.Match, Typedstmt):
    def __init__(self, subject, cases):
        self.subject: Typedstmt = subject
        self.cases: list[Typedstmt] = cases


class TypedNonlocal(ast.Nonlocal, Typedstmt):
    def __init__(self, names):
        self.names: list[Typedstmt] = names


class TypedPass(ast.Pass, Typedstmt):
    pass


class TypedRaise(ast.Raise, Typedstmt):
    def __init__(self, exc, cause):
        self.exc: Typedstmt = exc
        self.cause: Typedstmt = cause


class TypedReturn(ast.Return, Typedstmt):
    def __init__(self, value):
        self.value: Typedstmt = value


class TypedTry(ast.Try, Typedstmt):
    def __init__(self, body, handlers, orelse, finalbody):
        self.body: Typedstmt = body
        self.handlers: list[Typedstmt] = handlers
        self.orelse: Typedstmt = orelse
        self.finalbody: Typedstmt = finalbody


class TypedWhile(ast.While, Typedstmt):
    def __init__(self, test, body, orelse):
        self.test: Typedstmt = test
        self.body: Typedstmt = body
        self.orelse: Typedstmt = orelse


class TypedWith(ast.With, Typedstmt):
    def __init__(self, items, body, type_comment):
        self.items: list[Typedstmt] = items
        self.body: Typedstmt = body
        self.type_comment: Typedstmt = type_comment


def from_node(node: ast.AST) -> TypedAST:
    cls_name = node.__class__.__name__
    typed_cls = globals()[f'Typed{cls_name}']

    kwargs = {kw: getattr(node, kw) for kw in node.__class__._fields}

    typed_node = typed_cls(**kwargs)
    return typed_node
