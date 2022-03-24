from __future__ import annotations

import ast
from statipy.core.typed_ast import *


class NodePreprocessor(ast.NodeTransformer):
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split("\n")

    def get_code_slice(self, start_lineno: int, start_col_offset: int, end_lineno: int, end_col_offset: int) -> str:
        start_lineno -= 1
        end_lineno -= 1
        for i in range(start_lineno, end_lineno + 1):
            if i == start_lineno:
                yield from self.lines[i][start_col_offset:]
            elif i == end_lineno:
                yield from self.lines[i][:end_col_offset]
            else:
                yield from self.lines[i]

    def get_code_slice_with_index(self, start_lineno: int, start_col_offset: int, end_lineno: int, end_col_offset: int) \
            -> tuple[str, int, int]:
        start_lineno -= 1  # ここ0-indexedでもいいかも
        end_lineno -= 1
        for i in range(start_lineno, end_lineno + 1):
            if i == start_lineno == end_lineno:
                for j in range(start_col_offset, end_col_offset):
                    yield self.lines[i][j], i+1, j
            elif i == start_lineno:
                for j in range(start_col_offset, len(self.lines[i])):
                    yield self.lines[i][j], i+1, j
            elif i == end_lineno:
                for j in range(end_col_offset):
                    yield self.lines[i][j], i+1, j
            else:
                for j in range(len(self.lines[i])):
                    yield self.lines[i][j], i+1, j

    def visit_Constant(self, node: ast.Constant) -> TypedConstant:
        return TypedConstant(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             node.value)

    def visit_FormattedValue(self, node: ast.FormattedValue) -> TypedFormattedValue:
        value = self.visit(node.value)
        format_spec = self.visit(node.format_spec)
        return TypedFormattedValue(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                   value, node.conversion, format_spec)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> TypedJoinedStr:
        values = [self.visit(value) for value in node.values]
        return TypedJoinedStr(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              values)

    def visit_List(self, node: ast.List) -> TypedList:
        elts = [self.visit(elt) for elt in node.elts]
        return TypedList(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         elts, node.ctx)

    def visit_Tuple(self, node: ast.Tuple) -> TypedTuple:
        elts = [self.visit(elt) for elt in node.elts]
        return TypedTuple(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          elts, node.ctx)

    def visit_Set(self, node: ast.Set) -> TypedSet:
        elts = [self.visit(elt) for elt in node.elts]
        return TypedSet(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                        elts)

    def visit_Dict(self, node: ast.Dict) -> TypedDict:
        keys = [self.visit(key) for key in node.keys]
        values = [self.visit(value) for value in node.values]
        return TypedDict(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         keys, values)

    def visit_Name(self, node: ast.Name) -> TypedName:
        return TypedName(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         node.id, node.ctx)

    def visit_Starred(self, node: ast.Starred) -> TypedStarred:
        value = self.visit(node.value)
        return TypedStarred(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            value, node.ctx)

    def visit_Expr(self, node: ast.Expr) -> TypedExpr:
        value = self.visit(node.value)
        return TypedExpr(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         value)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> TypedUnaryOp:
        operand = self.visit(node.operand)

        match node.op:
            case ast.UAdd():
                op = UAdd(node.lineno, node.end_lineno, node.col_offset, node.col_offset + 1)
            case ast.USub():
                op = USub(node.lineno, node.end_lineno, node.col_offset, node.col_offset + 1)
            case ast.Not():
                op = Not(node.lineno, node.end_lineno, node.col_offset, node.col_offset + 3)
            case ast.Invert():
                op = Invert(node.lineno, node.end_lineno, node.col_offset, node.col_offset + 1)
            case _:
                raise Exception

        return TypedUnaryOp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            op, operand)

    def visit_UAdd(self, node: ast.UAdd):
        raise Exception

    def visit_USub(self, node: ast.USub):
        raise Exception

    def visit_Not(self, node: ast.Not):
        raise Exception

    def visit_Invert(self, node: ast.Invert):
        raise Exception

    def visit_BinOp(self, node: ast.BinOp) -> TypedBinOp:
        left = self.visit(node.left)
        right = self.visit(node.right)

        op_start = (10 ** 9, 10 ** 9)
        op_end = (-1, -1)

        for c, i, j in self.get_code_slice_with_index(node.left.end_lineno, node.left.end_col_offset,
                                                      node.right.lineno, node.right.col_offset):
            if c != " " and c != "\t" and c != "\n" and c != "\\":
                op_start = min(op_start, (i, j))
                op_end = max(op_end, (i, j))

        op_lineno, op_col_offset = op_start
        op_end_lineno, op_end_col_offset = op_end
        op_end_col_offset += 1

        match node.op:
            case ast.Add():
                op = Add(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.Sub():
                op = Sub(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.Mult():
                op = Mult(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.Div():
                op = Div(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.FloorDiv():
                op = FloorDiv(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.Mod():
                op = Mod(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.Pow():
                op = Pow(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.LShift():
                op = LShift(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.RShift():
                op = RShift(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.BitOr():
                op = BitOr(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.BitXor():
                op = BitXor(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.BitAnd():
                op = BitAnd(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case ast.MatMult():
                op = MatMult(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)
            case _:
                raise Exception

        return TypedBinOp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          left, op, right)

    def visit_Add(self, node: ast.Add):
        raise Exception

    def visit_Sub(self, node: ast.Sub):
        raise Exception

    def visit_Mult(self, node: ast.Mult):
        raise Exception

    def visit_Div(self, node: ast.Div):
        raise Exception

    def visit_FloorDiv(self, node: ast.FloorDiv):
        raise Exception

    def visit_Mod(self, node: ast.Mod):
        raise Exception

    def visit_Pow(self, node: ast.Pow):
        raise Exception

    def visit_LShift(self, node: ast.LShift):
        raise Exception

    def visit_RShift(self, node: ast.RShift):
        raise Exception

    def visit_BitOr(self, node: ast.BitOr):
        raise Exception

    def visit_BitXor(self, node: ast.BitXor):
        raise Exception

    def visit_BitAnd(self, node: ast.BitAnd):
        raise Exception

    def visit_MatMult(self, node: ast.MatMult):
        raise Exception

    def visit_BoolOp(self, node: ast.BoolOp) -> TypedBoolOp:
        values = [self.visit(v) for v in node.values]
        op_cls = And if node.op.__class__ is ast.And else Or
        ops = []

        for i in range(len(values) - 1):
            op_start = (10 ** 9, 10 ** 9)
            op_end = (-1, -1)

            for c, i, j in self.get_code_slice_with_index(values[i].end_lineno, values[i].end_col_offset,
                                                          values[i + 1].lineno, values[i + 1].col_offset):
                if c != " " and c != "\t" and c != "\n" and c != "\\":
                    op_start = min(op_start, (i, j))
                    op_end = max(op_end, (i, j))

            op_lineno, op_col_offset = op_start
            op_end_lineno, op_end_col_offset = op_end
            op_end_col_offset += 1

            ops.append(op_cls(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset))

        return TypedBoolOp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           ops, values)

    def visit_And(self, node: And):
        raise Exception

    def visit_Or(self, node: Or):
        raise Exception

    def visit_Compare(self, node: ast.Compare) -> TypedCompare:
        left = self.visit(node.left)
        comparators = [self.visit(c) for c in node.comparators]
        ops = []

        values = [left, *comparators]

        for i in range(len(values) - 1):
            op_cls = {
                ast.Eq: Eq, ast.NotEq: NotEq, ast.Lt: Lt, ast.LtE: LtE, ast.Gt: Gt, ast.GtE: GtE,
                ast.Is: Is, ast.IsNot: IsNot, ast.In: In, ast.NotIn: NotIn
            }.get(node.ops[i].__class__)

            op_start = (10 ** 9, 10 ** 9)
            op_end = (-1, -1)

            for c, i, j in self.get_code_slice_with_index(
                    values[i].end_lineno, values[i].end_col_offset, values[i + 1].lineno, values[i + 1].col_offset):
                if c != " " and c != "\t" and c != "\n" and c != "\\":
                    op_start = min(op_start, (i, j))
                    op_end = max(op_end, (i, j))

            op_lineno, op_col_offset = op_start
            op_end_lineno, op_end_col_offset = op_end
            op_end_col_offset += 1

            ops.append(op_cls(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset))

        return TypedCompare(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            left, ops, comparators)

    def visit_Eq(self, node: Eq):
        raise Exception

    def visit_NotEq(self, node: NotEq):
        raise Exception

    def visit_Lt(self, node: Lt):
        raise Exception

    def visit_LtE(self, node: LtE):
        raise Exception

    def visit_Gt(self, node: Gt):
        raise Exception

    def visit_GtE(self, node: GtE):
        raise Exception

    def visit_Is(self, node: Is):
        raise Exception

    def visit_IsNot(self, node: IsNot):
        raise Exception

    def visit_In(self, node: In):
        raise Exception

    def visit_NotIn(self, node: NotIn):
        raise Exception

    def visit_Call(self, node: ast.Call) -> TypedCall:
        func = self.visit(node.func)
        args = [self.visit(a) for a in node.args]
        keywords = [self.visit(k) for k in node.keywords]
        return TypedCall(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         func, args, keywords)

    def visit_keyword(self, node: ast.keyword) -> Typedkeyword:
        value = self.visit(node.value)
        return Typedkeyword(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            node.arg, value)

    def visit_IfExp(self, node: ast.IfExp) -> TypedIfExp:
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        return TypedIfExp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          test, body, orelse)

    def visit_Attribute(self, node: ast.Attribute) -> TypedAttribute:
        value = self.visit(node.value)
        return TypedAttribute(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              value, node.attr, node.ctx)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> TypedNamedExpr:
        target = self.visit(node.target)
        value = self.visit(node.value)
        return TypedNamedExpr(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              target, value)

    def visit_Subscript(self, node: ast.Subscript) -> TypedSubscript:
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        return TypedSubscript(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              value, slice, node.ctx)

    def visit_Slice(self, node: ast.Slice) -> TypedSlice:
        lower = self.visit(node.lower)
        upper = self.visit(node.upper)
        step = self.visit(node.step)
        return TypedSlice(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          lower, upper, step)

    def visit_ListComp(self, node: ast.ListComp) -> TypedListComp:
        elt = self.visit(node.elt)
        generators = [self.visit(g) for g in node.generators]
        return TypedListComp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             elt, generators)

    def visit_SetComp(self, node: ast.SetComp) -> TypedSetComp:
        elt = self.visit(node.elt)
        generators = [self.visit(g) for g in node.generators]
        return TypedSetComp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            elt, generators)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> TypedGeneratorExp:
        elt = self.visit(node.elt)
        generators = [self.visit(g) for g in node.generators]
        return TypedGeneratorExp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                 elt, generators)

    def visit_DictComp(self, node: ast.DictComp) -> TypedDictComp:
        key = self.visit(node.key)
        value = self.visit(node.value)
        generators = [self.visit(g) for g in node.generators]
        return TypedDictComp(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             key, value, generators)

    def visit_comprehension(self, node: ast.comprehension) -> Typedcomprehension:
        target = self.visit(node.target)
        iter = self.visit(node.iter)
        ifs = [self.visit(i) for i in node.ifs]
        return Typedcomprehension(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                  target, iter, ifs, node.is_async)

    def visit_Assign(self, node: ast.Assign) -> TypedAssign:
        targets = [self.visit(t) for t in node.targets]
        value = self.visit(node.value)
        return TypedAssign(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           targets, value, node.type_comment)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> TypedAnnAssign:
        target = self.visit(node.target)
        annotation = self.visit(node.annotation)
        value = self.visit(node.value)
        return TypedAnnAssign(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              target, annotation, value, node.simple)

    def visit_AugAssign(self, node: ast.AugAssign) -> TypedAugAssign:
        target = self.visit(node.target)
        value = self.visit(node.value)

        op_cls = {
            ast.Add: Add, ast.Sub: Sub, ast.Mult: Mult, ast.MatMult: MatMult, ast.Div: Div, ast.Mod: Mod, ast.Pow: Pow,
            ast.LShift: LShift, ast.RShift: RShift, ast.BitOr: BitOr, ast.BitXor: BitXor, ast.BitAnd: BitAnd,
            ast.FloorDiv: FloorDiv,
        }.get(type(node.op))

        op_start = (10 ** 9, 10 ** 9)
        op_end = (-1, -1)

        for c, i, j in self.get_code_slice_with_index(node.target.end_lineno, node.target.end_col_offset,
                                                      node.value.lineno, node.value.col_offset):
            if c != " " and c != "\t" and c != "\n" and c != "\\":
                op_start = min(op_start, (i, j))
                op_end = max(op_end, (i, j))

        op_lineno, op_col_offset = op_start
        op_end_lineno, op_end_col_offset = op_end
        op_end_col_offset += 1

        op = op_cls(op_lineno, op_end_lineno, op_col_offset, op_end_col_offset)

        return TypedAugAssign(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              target, op, value)

    def visit_Raise(self, node: ast.Raise) -> TypedRaise:
        exc = self.visit(node.exc)
        cause = self.visit(node.cause) if node.cause is not None else None
        return TypedRaise(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          exc, cause)

    def visit_Assert(self, node: ast.Assert) -> TypedAssert:
        test = self.visit(node.test)
        msg = self.visit(node.msg) if node.msg is not None else None
        return TypedAssert(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           test, msg)

    def visit_Delete(self, node: ast.Delete) -> TypedDelete:
        targets = [self.visit(t) for t in node.targets]
        return TypedDelete(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           targets)

    def visit_Pass(self, node: ast.Pass) -> TypedPass:
        return TypedPass(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset)

    def visit_Import(self, node: ast.Import) -> TypedImport:
        names = [self.visit(n) for n in node.names]
        return TypedImport(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> TypedImportFrom:
        names = [self.visit(n) for n in node.names]
        return TypedImportFrom(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                               node.module, names, node.level)

    def visit_alias(self, node: ast.alias) -> Typedalias:
        return Typedalias(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          node.name, node.asname)

    def visit_If(self, node: ast.If) -> TypedIf:
        test = self.visit(node.test)
        body = [self.visit(b) for b in node.body]
        orelse = [self.visit(b) for b in node.orelse]
        return TypedIf(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                       test, body, orelse)

    def visit_For(self, node: ast.For) -> TypedFor:
        target = self.visit(node.target)
        iter_ = self.visit(node.iter)
        body = [self.visit(b) for b in node.body]
        orelse = [self.visit(b) for b in node.orelse]
        return TypedFor(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                        target, iter_, body, orelse, node.type_comment)

    def visit_While(self, node: ast.While) -> TypedWhile:
        test = self.visit(node.test)
        body = [self.visit(b) for b in node.body]
        orelse = [self.visit(b) for b in node.orelse]
        return TypedWhile(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          test, body, orelse)

    def visit_Break(self, node: ast.Break) -> TypedBreak:
        return TypedBreak(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset)

    def visit_Continue(self, node: ast.Continue) -> TypedContinue:
        return TypedContinue(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset)

    def visit_Try(self, node: ast.Try) -> TypedTry:
        body = [self.visit(b) for b in node.body]
        handlers = [self.visit(h) for h in node.handlers]
        orelse = [self.visit(b) for b in node.orelse]
        finalbody = [self.visit(b) for b in node.finalbody]
        return TypedTry(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                        body, handlers, orelse, finalbody)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> TypedExceptHandler:
        type_ = self.visit(node.type)
        body = [self.visit(b) for b in node.body]
        return TypedExceptHandler(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                  type_, node.name, body)

    def visit_With(self, node: ast.With) -> TypedWith:
        items = [self.visit(i) for i in node.items]
        body = [self.visit(b) for b in node.body]
        return TypedWith(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                         items, body, node.type_comment)

    def visit_withitem(self, node: ast.withitem) -> Typedwithitem:
        context_expr = self.visit(node.context_expr)
        optional_vars = self.visit(node.optional_vars)
        return Typedwithitem(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             context_expr, optional_vars)

    def visit_Match(self, node: ast.Match) -> TypedMatch:
        expr = self.visit(node.subject)
        cases = [self.visit(c) for c in node.cases]
        return TypedMatch(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          expr, cases)

    def visit_match_case(self, node: ast.match_case) -> Typedmatch_case:
        pattern = self.visit(node.pattern)
        guard = self.visit(node.guard)
        body = [self.visit(b) for b in node.body]
        return Typedmatch_case(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              pattern, guard, body)

    def visit_MatchValue(self, node: ast.MatchValue) -> TypedMatchValue:
        value = self.visit(node.value)
        return TypedMatchValue(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                               value)

    def visit_MatchSingleton(self, node: ast.MatchSingleton) -> TypedMatchSingleton:
        return TypedMatchSingleton(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                   node.value)

    def visit_MatchSequence(self, node: ast.MatchSequence) -> TypedMatchSequence:
        patterns = [self.visit(p) for p in node.patterns]
        return TypedMatchSequence(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                  patterns)

    def visit_MatchStar(self, node: ast.MatchStar) -> TypedMatchStar:
        return TypedMatchStar(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> TypedMatchMapping:
        keys = [self.visit(k) for k in node.keys]
        patterns = [self.visit(p) for p in node.patterns]
        return TypedMatchMapping(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                 keys, patterns, node.rest)


    def visit_MatchClass(self, node: ast.MatchClass) -> TypedMatchClass:
        cls = self.visit(node.cls)
        patterns = [self.visit(p) for p in node.patterns]
        kwd_patterns = [self.visit(p) for p in node.kwd_patterns]
        return TypedMatchClass(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                               cls, patterns, node.kwd_attrs, kwd_patterns)

    def visit_MatchAs(self, node: ast.MatchAs) -> TypedMatchAs:
        pattern = self.visit(node.pattern)
        return TypedMatchAs(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            pattern, node.name)

    def visit_MatchOr(self, node: ast.MatchOr) -> TypedMatchOr:
        patterns = [self.visit(p) for p in node.patterns]
        return TypedMatchOr(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                            patterns)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> TypedFunctionDef:
        args = self.visit(node.args)
        body = [self.visit(b) for b in node.body]
        decorator_list = [self.visit(d) for d in node.decorator_list]
        returns = self.visit(node.returns) if node.returns is not None else None
        return TypedFunctionDef(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                                node.name, args, body, decorator_list, returns, node.type_comment)

    def visit_Lambda(self, node: ast.Lambda) -> TypedLambda:
        args = self.visit(node.args)
        body = self.visit(node.body)
        return TypedLambda(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           args, body)

    def visit_arguments(self, node: ast.arguments) -> Typedarguments:
        posonlyargs = [self.visit(a) for a in node.posonlyargs]
        args = [self.visit(a) for a in node.args]
        vararg = self.visit(node.vararg) if node.vararg is not None else None
        kwonlyargs = [self.visit(a) for a in node.kwonlyargs]
        kw_defaults = [self.visit(d) for d in node.kw_defaults]
        kwarg = self.visit(node.kwarg) if node.kwarg is not None else None
        defaults = [self.visit(d) for d in node.defaults]
        return Typedarguments(posonlyargs, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults)

    def visit_arg(self, node: ast.arg) -> Typedarg:
        annotation = self.visit(node.annotation) if node.annotation is not None else None
        return Typedarg(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                        node.arg, annotation, node.type_comment)

    def visit_Return(self, node: ast.Return) -> TypedReturn:
        value = self.visit(node.value)
        return TypedReturn(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           value)

    def visit_Yield(self, node: ast.Yield) -> TypedYield:
        value = self.visit(node.value)
        return TypedYield(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                          value)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> TypedYieldFrom:
        value = self.visit(node.value)
        return TypedYieldFrom(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                              value)

    def visit_Global(self, node: ast.Global) -> TypedGlobal:
        return TypedGlobal(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                           node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> TypedNonlocal:
        return TypedNonlocal(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             node.names)

    def visit_ClassDef(self, node: ast.ClassDef) -> TypedClassDef:
        bases = [self.visit(b) for b in node.bases]
        keywords = [self.visit(k) for k in node.keywords]
        body = [self.visit(b) for b in node.body]
        decorator_list = [self.visit(d) for d in node.decorator_list]
        return TypedClassDef(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
                             node.name, bases, keywords, body, decorator_list)

    #  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> TypedAsyncFunctionDef:
    #      args = self.visit(node.args)
    #      body = [self.visit(b) for b in node.body]
    #      decorator_list = [self.visit(d) for d in node.decorator_list]
    #      returns = self.visit(node.returns)
    #      return TypedAsyncFunctionDef(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
    #                                   node.name, args, body, decorator_list, returns, node.type_comment)

    #  def visit_Await(self, node: ast.Await) -> TypedAwait:
    #      value = self.visit(node.value)
    #      return TypedAwait(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
    #                        value)

    #  def visit_AsyncFor(self, node: ast.AsyncFor) -> TypedAsyncFor:
    #      target = self.visit(node.target)
    #      iter_ = self.visit(node.iter)
    #      body = [self.visit(b) for b in node.body]
    #      orelse = [self.visit(b) for b in node.orelse]
    #       return TypedAsyncFor(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
    #                           target, iter_, body, orelse, node.type_comment)


    #  def visit_AsyncWith(self, node: ast.AsyncWith) -> TypedAsyncWith:
    #      items = [self.visit(i) for i in node.items]
    #      body = [self.visit(b) for b in node.body]
    #      return TypedAsyncWith(node.lineno, node.end_lineno, node.col_offset, node.end_col_offset,
    #                            items, body, node.type_comment)
