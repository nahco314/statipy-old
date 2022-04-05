from __future__ import annotations

import statipy.errors as errors
from typing import Optional, TypeAlias, Callable, NamedTuple
from collections import defaultdict


class AbstractObject:
    # rootかどうかが間違いやすそうだし、get_objが必要なのかがよくわからない
    # どうにかできそうだけど

    defined = True

    def __init__(self, type_: AbstractType):
        self.parent: Optional[AbstractObject] = None  # Object to replace this object

        self.type = type_

        self.attr: Attr = defaultdict(Undefined)
        self.special_attr: Attr = defaultdict(Undefined)
        self.special_attr["type"] = self.type
        self.is_builtin: bool = isinstance(type_, BuiltinType)

        # if and only if self.type is BuiltinFunction
        self.function: Optional[Callable[["Environment", list[AbstractObject], dict[str, AbstractObject]], AbstractObject]] = None

        # self.attr["__class__"] = type_

    def get_type(self):
        return self.type.get_obj()

    def replace(self, obj: AbstractObject):
        """replace self with obj"""
        if self.parent is not None:
            self.parent.replace(obj)
        else:
            self.parent = obj

    def get_obj(self):
        if self.parent is None:
            return self
        else:
            obj = self.parent.get_obj()
            self.parent = obj
            return obj

    def unification(self, target: AbstractObject):
        if self is target:
            return

        if isinstance(target, Undefined):
            target.attr = self.attr
            target.special_attr = self.special_attr

        else:
            for name in {*self.attr, *target.attr}:
                self.attr[name].get_obj().unification(target.attr[name].get_obj())

            for name in {*self.special_attr, *target.special_attr}:
                self.special_attr[name].get_obj().unification(target.special_attr[name].get_obj())

        self.replace(target)

    def assert_root(self):
        assert self.parent is None

    def __repr__(self):
        if self.is_builtin:
            return f"<{self.type.__class__.__name__}>"
        else:
            # ToDo
            return "???"

    def __eq__(self, other):
        # ToDO: これどうすれば？
        return self.get_type() is other.get_type()


class Undefined(AbstractObject):
    defined = False

    def __init__(self):
        super().__init__(None)
        self.special_attr.pop("type")

    def unification(self, target: AbstractObject):
        self.attr = target.attr
        self.special_attr = target.special_attr
        self.replace(target)


class AbstractType(AbstractObject):
    method_table = (
        # (method name, special method name(s))
        ("repr", ["__repr__"]),
        ("str", ["__str__"]),
        ("add", ["__add__", "__radd__"]),
        ("sub", ["__sub__", "__rsub__"]),
        ("mul", ["__mul__", "__rmul__"]),
        ("div", ["__truediv__", "__rtruediv__"]),
        ("floordiv", ["__floordiv__", "__rfloordiv__"]),
        ("mod", ["__mod__", "__rmod__"]),
        ("pow", ["__pow__", "__rpow__"]),
        ("lshift", ["__lshift__", "__rlshift__"]),
        ("rshift", ["__rshift__", "__rrshift__"]),
        ("or_", ["__or__", "__ror__"]),
        ("xor", ["__xor__", "__rxor__"]),
        ("and_", ["__and__", "__rand__"]),
        ("matmul", ["__matmul__", "__rmatmul__"]),
        ("abs", ["__abs__"]),
        ("negative", ["__neg__"]),
        ("positive", ["__pos__"]),
        ("invert", ["__invert__"]),
        ("getattro", ["__getattr__", "__getattribute__"]),
        ("setattro", ["__setattr__"]),
        ("getattr", []),
        ("setattr", []),
        ("iter", ["__iter__"]),
        ("next", ["__next__"]),
    )

    def __init__(self):
        super().__init__(Type())

        self.repr: Optional[repr_func] = None
        self.str: Optional[repr_func] = None

        self.add: Optional[binary_func] = None
        self.sub: Optional[binary_func] = None
        self.mul: Optional[binary_func] = None
        self.div: Optional[binary_func] = None
        self.floordiv: Optional[binary_func] = None
        self.mod: Optional[binary_func] = None
        self.pow: Optional[ternary_func] = None
        self.lshift: Optional[binary_func] = None
        self.rshift: Optional[binary_func] = None
        self.or_: Optional[binary_func] = None
        self.xor: Optional[binary_func] = None
        self.and_: Optional[binary_func] = None
        self.matmul: Optional[binary_func] = None

        self.inplace_add: Optional[binary_func] = None
        self.inplace_sub: Optional[binary_func] = None
        self.inplace_mul: Optional[binary_func] = None
        self.inplace_div: Optional[binary_func] = None
        self.inplace_floordiv: Optional[binary_func] = None
        self.inplace_mod: Optional[binary_func] = None
        self.inplace_pow: Optional[ternary_func] = None
        self.inplace_lshift: Optional[binary_func] = None
        self.inplace_rshift: Optional[binary_func] = None
        self.inplace_or_: Optional[binary_func] = None
        self.inplace_xor: Optional[binary_func] = None
        self.inplace_and_: Optional[binary_func] = None
        self.inplace_matmul: Optional[binary_func] = None

        self.abs: Optional[unary_func] = None

        self.length: Optional[unary_func] = None
        self.concat: Optional[binary_func] = None
        self.repeat: Optional[ssizeargfunc] = None
        self.get_item: Optional[ssizeargfunc] = None
        self.ass_item: Optional[ssizeargfunc] = None
        self.contains: Optional[binary_func] = None
        self.inplace_concat: Optional[binary_func] = None
        self.inplace_repeat: Optional[ssizeargfunc] = None

        self.negative: Optional[unary_func] = None
        self.positive: Optional[unary_func] = None
        self.invert: Optional[unary_func] = None

        self.getattro: Optional[getattr_func] = None
        self.setattro: Optional[setattr_func] = None
        self.getattr: Optional[getattr_s_func] = None
        self.setattr: Optional[setattr_s_func] = None

        self.iter: Optional[iter_func] = None
        self.next: Optional[next_func] = None
        self.call: Optional[Callable] = None

    def unification(self, target: AbstractObject):
        # ここはこのままじゃだめそう
        # 少なくとも継承に関しては絶対にだめで、継承を含む場合のアルゴリズムについては考える必要がある

        if self is not target:
            raise errors.TypingError()
        else:
            pass

    def create_instance(self):
        obj = AbstractObject(self)
        return obj

    def is_subtype(self, type_: AbstractType):
        # ToDo
        return self is type_


class BuiltinType(AbstractType):
    # singleton
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        else:
            obj = super().__new__(cls)
            cls._instance = obj
            return obj

    def __init__(self):
        if self.__class__._init:
            return
        self.__class__._init = True

        super().__init__()


class Type(BuiltinType):
    def __init__(self):
        super(Type, self).__init__()


class NotImplementedType(BuiltinType):
    pass


class Str(BuiltinType):
    """str type
    参考: CPython/Objects/unicodeobject.c
    """
    def __init__(self):
        super().__init__()

        def str_concat(env, a: AbstractObject, b: AbstractObject) -> AbstractObject:
            if not a.get_type().is_subtype(Str()):
                return py_not_implemented
            if not b.get_type().is_subtype(Str()):
                return py_not_implemented

            return Str().create_instance()

        def str_repeat(env, str_: AbstractObject, len_: int):
            if not str_.get_type().is_subtype(Str()):
                return py_not_implemented

            return Str().create_instance()

        def str_getitem(env, self: AbstractObject, index: int):
            if not self.get_type().is_subtype(Str()):
                return py_not_implemented

            return Str().create_instance()

        def str_contains(env, str_: AbstractObject, substr: AbstractObject):
            if not str_.get_type().is_subtype(Str()):
                return py_not_implemented
            if not substr.get_type().is_subtype(Str()):
                return py_not_implemented

            return Bool().create_instance()

        self.length = len_func
        self.concat = str_concat
        self.repeat = str_repeat
        self.inplace_concat = str_concat
        self.inplace_repeat = str_repeat
        self.get_item = str_getitem
        self.contains = str_contains


class Int(BuiltinType):
    """int type
    参考: CPython/Objects/longobject.c
    """

    def __init__(self):
        super().__init__()

        def int_bin_func(env, a: AbstractObject, b: AbstractType) -> AbstractObject:
            if a.get_type().is_subtype(Int()) and b.type.is_subtype(Int()):
                return Int().create_instance()
            return py_not_implemented

        def true_div(env, a: AbstractObject, b: AbstractObject) -> AbstractObject:
            if a.get_type().is_subtype(Int()) and b.type.is_subtype(Int()):
                return Float().create_instance()
            return py_not_implemented

        def pow_func(env, a: AbstractObject, b: AbstractObject, c: Optional[AbstractObject]) -> AbstractObject:
            if a.get_type().is_subtype(Int()) and b.type.is_subtype(Int()) and (c is None or c.type.is_subtype(Int())):
                return Int().create_instance()
            return py_not_implemented

        def int_int(env, a: AbstractObject) -> AbstractObject:
            return Int().create_instance()

        self.add = int_bin_func
        self.sub = int_bin_func
        self.mul = int_bin_func
        self.div = true_div
        self.floordiv = int_bin_func
        self.mod = int_bin_func
        self.pow = int_bin_func
        self.lshift = int_bin_func
        self.rshift = int_bin_func
        self.or_ = int_bin_func
        self.xor = int_bin_func
        self.and_ = int_bin_func
        # matmul is not implemented
        self.inplace_add = int_bin_func
        self.inplace_sub = int_bin_func
        self.inplace_mul = int_bin_func
        self.inplace_div = true_div
        self.inplace_floordiv = int_bin_func
        self.inplace_mod = int_bin_func
        self.inplace_pow = int_bin_func
        self.inplace_lshift = int_bin_func
        self.inplace_rshift = int_bin_func
        self.inplace_or_ = int_bin_func
        self.inplace_xor = int_bin_func
        self.inplace_and_ = int_bin_func
        # matmul is not implemented
        self.abs = int_int

        self.negative = int_int
        self.positive = int_int
        self.invert = int_int
        self.index = int_int


class Float(BuiltinType):
    def __init__(self):
        super().__init__()


class List(BuiltinType):
    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()


class Tuple(BuiltinType):
    # ToDo: 定数長のタプルへの対応
    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()


class Set(BuiltinType):
    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()


class Dict(BuiltinType):
    def __init__(self):
        super().__init__()

        self.special_attr["key"] = Undefined()
        self.special_attr["value"] = Undefined()


class Bool(BuiltinType):
    def __init__(self):
        super().__init__()
        # ToDo: Intを継承させる


class Slice(BuiltinType):
    def __init__(self):
        super().__init__()


class Iterator(BuiltinType):
    def __init__(self):
        super().__init__()

        self.seq = Undefined()


class BuiltinFunction(BuiltinType):
    def __init__(self):
        super().__init__()

        def call_func(env, func: AbstractObject, args: list[AbstractObject], kwargs: dict[str, AbstractObject]) -> AbstractObject:
            assert func.function
            return func.function(env, args, kwargs)

        self.call = call_func

    def create_instance(self, function: Optional[Callable[[list[AbstractObject], dict[AbstractObject]], AbstractObject]] = None) -> AbstractObject:
        assert function is not None
        obj = super().create_instance()
        obj.function = function
        return obj


Attr: TypeAlias = dict[str, AbstractObject]


binary_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject], AbstractObject]
ternary_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject, Optional[AbstractObject]], AbstractObject]
unary_func: TypeAlias = Callable[["Environment", AbstractObject], AbstractObject]
ssizeargfunc: TypeAlias = Callable[["Environment", AbstractObject, int], AbstractObject]

repr_func: TypeAlias = Callable[["Environment", AbstractObject], Str]

getattr_s_func: TypeAlias = Callable[["Environment", AbstractObject, str], AbstractObject]
setattr_s_func: TypeAlias = Callable[["Environment", AbstractObject, str, AbstractObject], AbstractObject]
getattr_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject], AbstractObject]
setattr_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject, AbstractObject], AbstractObject]

iter_func: TypeAlias = Callable[["Environment", AbstractObject], AbstractObject]
next_func: TypeAlias = Callable[["Environment", AbstractObject], AbstractObject]

py_not_implemented = NotImplementedType().create_instance()


def len_func(self):
    return Int().create_instance()
