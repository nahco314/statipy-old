from statipy.core.abstract_object import AbstractObject

import ast
from ast import (expr, Attribute, Await, BinOp, BoolOp, Bytes, Call, Compare, Constant, Dict, DictComp, Ellipsis,
                 FormattedValue, GeneratorExp, IfExp, JoinedStr, Lambda, List, ListComp, Name, NameConstant, NamedExpr,
                 Num, Set, SetComp, Slice, Starred, Str, Subscript, Tuple, UnaryOp, Yield, YieldFrom)


class Typedexpr(expr):
    def __init__(self, *args, abstract_obj: AbstractObject, **kwargs):
        super().__init__(*args, **kwargs)
        self.abstract_obj = abstract_obj


class TypedAttribute(Attribute, Typedexpr):
    _fields = (
        'value',
        'attr',
        'ctx',
        'abstract_obj',
    )


class TypedAwait(Await, Typedexpr):
    _fields = (
        'value',
        'abstract_obj',
    )


class TypedBinOp(BinOp, Typedexpr):
    _fields = (
        'left',
        'op',
        'right',
        'abstract_obj',
    )


class TypedBoolOp(BoolOp, Typedexpr):
    _fields = (
        'op',
        'values',
        'abstract_obj',
    )


class TypedBytes(Bytes, Typedexpr):
    _fields = (
        's',
        'abstract_obj',
    )


class TypedCall(Call, Typedexpr):
    _fields = (
        'func',
        'args',
        'keywords',
        'abstract_obj',
    )


class TypedCompare(Compare, Typedexpr):
    _fields = (
        'left',
        'ops',
        'comparators',
        'abstract_obj',
    )


class TypedConstant(Constant, Typedexpr):
    _fields = (
        'value',
        'kind',
        'abstract_obj',
    )


class TypedDict(Dict, Typedexpr):
    _fields = (
        'keys',
        'values',
        'abstract_obj',
    )


class TypedDictComp(DictComp, Typedexpr):
    _fields = (
        'key',
        'value',
        'generators',
        'abstract_obj',
    )


class TypedEllipsis(Ellipsis, Typedexpr):
    _fields = (
        'abstract_obj',
    )


class TypedFormattedValue(FormattedValue, Typedexpr):
    _fields = (
        'value',
        'conversion',
        'format_spec',
        'abstract_obj',
    )


class TypedGeneratorExp(GeneratorExp, Typedexpr):
    _fields = (
        'elt',
        'generators',
        'abstract_obj',
    )


class TypedIfExp(IfExp, Typedexpr):
    _fields = (
        'test',
        'body',
        'orelse',
        'abstract_obj',
    )


class TypedJoinedStr(JoinedStr, Typedexpr):
    _fields = (
        'values',
        'abstract_obj',
    )


class TypedLambda(Lambda, Typedexpr):
    _fields = (
        'args',
        'body',
        'abstract_obj',
    )


class TypedList(List, Typedexpr):
    _fields = (
        'elts',
        'ctx',
        'abstract_obj',
    )


class TypedListComp(ListComp, Typedexpr):
    _fields = (
        'elt',
        'generators',
        'abstract_obj',
    )


class TypedName(Name, Typedexpr):
    _fields = (
        'id',
        'ctx',
        'abstract_obj',
    )


class TypedNameConstant(NameConstant, Typedexpr):
    _fields = (
        'value',
        'kind',
        'abstract_obj',
    )


class TypedNamedExpr(NamedExpr, Typedexpr):
    _fields = (
        'target',
        'value',
        'abstract_obj',
    )


class TypedNum(Num, Typedexpr):
    _fields = (
        'n',
        'abstract_obj',
    )


class TypedSet(Set, Typedexpr):
    _fields = (
        'elts',
        'abstract_obj',
    )


class TypedSetComp(SetComp, Typedexpr):
    _fields = (
        'elt',
        'generators',
        'abstract_obj',
    )


class TypedSlice(Slice, Typedexpr):
    _fields = (
        'lower',
        'upper',
        'step',
        'abstract_obj',
    )


class TypedStarred(Starred, Typedexpr):
    _fields = (
        'value',
        'ctx',
        'abstract_obj',
    )


class TypedStr(Str, Typedexpr):
    _fields = (
        's',
        'abstract_obj',
    )


class TypedSubscript(Subscript, Typedexpr):
    _fields = (
        'value',
        'slice',
        'ctx',
        'abstract_obj',
    )


class TypedTuple(Tuple, Typedexpr):
    _fields = (
        'elts',
        'ctx',
        'abstract_obj',
    )


class TypedUnaryOp(UnaryOp, Typedexpr):
    _fields = (
        'op',
        'operand',
        'abstract_obj',
    )


class TypedYield(Yield, Typedexpr):
    _fields = (
        'value',
        'abstract_obj',
    )


class TypedYieldFrom(YieldFrom, Typedexpr):
    _fields = (
        'value',
        'abstract_obj',
    )


def from_node(node: expr, abstract_obj: AbstractObject) -> Typedexpr:
    cls_name = node.__class__.__name__
    typed_cls = globals()[f'Typed{cls_name}']

    kwargs = {"abstract_obj": abstract_obj}
    for kw in node.__class__._fields:
        kwargs[kw] = getattr(node, kw)

    typed_node = typed_cls(**kwargs)
    return typed_node
