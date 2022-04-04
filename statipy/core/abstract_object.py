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

        # self.attr["__class__"] = type_

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
                self.attr[name].unification(target.attr[name])

            for name in {*self.special_attr, *target.special_attr}:
                self.special_attr[name].unification(target.special_attr[name])

        self.replace(target)

    def assert_root(self):
        assert self.parent is None

    def __repr__(self):
        if self.is_builtin:
            return f"<{self.type.__class__.__name__}>"
        else:
            # ToDo
            return "???"


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
        ("or", ["__or__", "__ror__"]),
        ("xor", ["__xor__", "__rxor__"]),
        ("and", ["__and__", "__rand__"]),
        ("matmul", ["__matmul__", "__rmatmul__"]),
        ("negative", ["__neg__"]),
        ("positive", ["__pos__"]),
        ("invert", ["__invert__"]),
    )

    def __init__(self):
        super().__init__(Type())

        self.repr: Optional[repr_func] = None
        self.str: Optional[repr_func] = None
        self.add: Optional[binary_func] = None

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
    def __init__(self):
        super().__init__()

        def str_mul(str_: AbstractObject, len_: AbstractObject):
            return Str().create_instance()

        self.mul = str_mul


class Int(BuiltinType):
    def __init__(self):
        super().__init__()

        def int_bin_func(a: AbstractObject, b: AbstractType) -> AbstractObject:
            if a.type.is_subtype(Int()) and b.type.is_subtype(Int()):
                return Int().create_instance()
            return py_not_implemented

        def int_int(a: AbstractObject) -> AbstractObject:
            return Int().create_instance()

        self.add = int_bin_func
        self.index = int_int


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


Attr: TypeAlias = dict[str, AbstractObject]

binary_func = Callable[[AbstractObject, AbstractObject], AbstractObject]
repr_func = Callable[[AbstractObject], Str]

py_not_implemented = NotImplementedType().create_instance()
