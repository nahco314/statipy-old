from __future__ import annotations

import statipy.errors as errors
from typing import Optional, TypeAlias, Callable, NamedTuple
from collections import defaultdict


# richcompare operators
NE = 0
EQ = 1
LE = 2
GE = 3
LT = 4
GT = 5


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
        self.function: Optional[function] = None

        # self.attr["__class__"] = type_

    def get_type(self):
        return self.type.get_obj()

    def replace(self, obj: AbstractObject):
        """replace self with obj"""
        if self is obj:
            return
        if self.parent is not None:
            self.parent.replace(obj)
        else:
            self.parent = obj

    def get_obj(self):
        if self.parent is None:
            return self
        else:
            obj = self.parent.get_obj()
            assert self is not obj
            self.parent = obj
            return obj

    def unification(self, target: AbstractObject):
        target = target.get_obj()
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
        ("name", ["__name__"]),
        ("doc", ["__doc__"]),
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
        ("divmod", ["__divmod__", "__rdivmod__"]),
        ("abs", ["__abs__"]),
        ("length", ["__len__"]),
        ("concat", ["__add__", "__radd__"]),
        ("repeat", ["__mul__", "__rmul__"]),
        ("get_item", ["__getitem__"]),
        ("ass_item", []),
        ("contains", ["__contains__"]),
        ("inplace_concat", ["__iadd__"]),
        ("inplace_repeat", ["__imul__"]),
        ("negative", ["__neg__"]),
        ("positive", ["__pos__"]),
        ("invert", ["__invert__"]),
        ("getattro", ["__getattr__", "__getattribute__"]),
        ("setattro", ["__setattr__"]),
        ("getattr", []),
        ("setattr", []),
        ("iter", ["__iter__"]),
        ("next", ["__next__"]),
        ("call", ["__call__"]),
        ("richcompare", ["__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__"]),
        ("index", ["__index__"]),
        ("descr_get", ["__get__"]),
        ("descr_set", ["__set__"]),
        ("int", ["__int__"]),
        ("float", ["__float__"]),
        ("complex", ["__complex__"]),
        ("bool", ["__bool__"]),
        ("hash", ["__hash__"]),
        ("new", ["__new__"]),
        ("init", ["__init__"]),
    )

    generic_names: tuple[str] = None

    def __init__(self):
        super().__init__(Type())

        self.name: str = ""
        self.doc: str = ""

        self.repr: Optional[obj_repr_func] = None
        self.str: Optional[obj_repr_func] = None

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
        self.divmod: Optional[binary_func] = None

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
        self.call: Optional[call_function] = None

        self.richcompare: Optional[richcmp_func] = None

        self.index: Optional[unary_func] = None

        self.descr_get: Optional[descr_get_func] = None
        self.descr_set: Optional[descr_set_func] = None

        self.int: Optional[unary_func] = None
        self.float: Optional[unary_func] = None
        self.complex: Optional[unary_func] = None
        self.bool: Optional[unary_func] = None

        self.hash: Optional[unary_func] = None

        self.new: Optional[call_function] = None
        self.init: Optional[call_function] = None

        self.mro: list[AbstractType] = []
        self.base: Optional[AbstractType] = None

    def unification(self, target: AbstractObject):
        # ここはこのままじゃだめそう
        # 少なくとも継承に関しては絶対にだめで、継承を含む場合のアルゴリズムについては考える必要がある

        if self is not target:
            raise errors.TypingError()
        else:
            pass

    def create_instance(self, generics: dict[str, AbstractObject] | list[AbstractObject] = None):
        obj = AbstractObject(self)
        if generics is not None:
            if isinstance(generics, list):
                if self.__class__.generic_names is None:
                    raise Exception("Generic types are not defined.")
                generics = dict(zip(self.__class__.generic_names, generics))
            for key, value in generics.items():
                print(obj.special_attr, repr(value), key)
                obj.special_attr[key].unification(value)
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


class Object(BuiltinType):
    def __init__(self):
        super(Object, self).__init__()


class Type(BuiltinType):
    """type type
    参考: CPython/Objects/typeobject.c
    """

    def __init__(self):
        super(Type, self).__init__()

        def type_call(env, type_: AbstractType, args: list[AbstractObject], kwargs: dict[str, AbstractObject]):
            if type_ is Type():
                if len(args) == 1 and len(kwargs) == 0:
                    obj = args[0].get_type()
                    return obj

                if len(args) != 3:
                    raise errors.TypingError

            if type_.new is None:
                raise errors.TypingError

            obj = type_.new(env, type_, args, kwargs)
            if not obj.get_type().is_subtype(type_):
                raise errors.TypingError

            type_ = obj.get_type()
            if type_.init is not None:
                obj = type_.init(env, obj, args, kwargs)
            return obj

        class TypeNewCtx(NamedTuple):
            metatype: AbstractType
            args: list[AbstractObject]
            kwargs: dict[str, AbstractObject]
            orig_dict: dict[str, AbstractObject]
            name: str
            bases: list[AbstractType]
            base: Optional[AbstractType]
            slots: list[str]
            nslot: int
            add_dict: int
            add_weak: int
            may_add_dict: int
            may_add_weak: int

        def calculate_metaclass(metatype: AbstractType, bases: list[AbstractType]):
            winner = metatype
            for tmp in bases:
                tmptype = tmp.get_type()
                if winner.is_subtype(tmptype):
                    continue
                if tmptype.is_subtype(winner):
                    winner = tmptype
                    continue
                raise errors.TypingError
            return winner

        def solid_base(type_: AbstractType):
            base: AbstractType
            if type_.base:
                base = solid_base(type_.base.get_obj())
            else:
                base = Object()
            # extra_ivers ってなんなんや
            return base

        def best_base(bases: list[AbstractType]):
            base = None
            winner = None
            for base_proto in bases:
                if not base_proto.get_type().is_subtype(Type()):
                    raise errors.TypingError
                base_i: AbstractType = base_proto
                candidate = solid_base(base_i)
                if winner is None:
                    winner = candidate
                    base = base_i
                elif winner.is_subtype(candidate):
                    pass
                elif candidate.is_subtype(winner):
                    winner = candidate
                    base = base_i
                else:
                    raise errors.TypingError
            return base

        def type_new_get_bases(env, ctx: TypeNewCtx) -> tuple[int, Optional[AbstractType]]:
            nbases = len(ctx.bases)
            if nbases == 0:
                ctx.base = Object()
                ctx.bases = [ctx.base]
                return 0, None

            # mro_entries?

            winner = calculate_metaclass(ctx.metatype, ctx.bases)
            type_ = None
            if winner != ctx.metatype:
                if winner.new != type_new:
                    type_ = winner.new(env, winner, ctx.args, ctx.kwargs)
                    assert isinstance(type_, AbstractType)
                    return 1, type_
                ctx.metatype = winner

            base = best_base(ctx.bases)

            ctx.base = base
            return 0, type_

        def type_new_init(env, ctx: TypeNewCtx):
            dict_ = ctx.orig_dict.copy()
            # type_new_alloc の意味ある？
            type_ = AbstractType()
            type_.bases = ctx.bases
            type_.base = ctx.base
            type_.name = ctx.name

            type_.attr.update(ctx.orig_dict)  # dictってなに
            # etってなに

            return type_

        def type_new_inpl(env, ctx: TypeNewCtx):
            type_ = type_new_init(env, ctx)
            # module
            # doc?
            # ToDo: __new__, __init_subclass__, __class_getitem__, type_new_descriptors, type_new_set_slots,
            #  type_new_set_classcell, type_new_set_names, type_new_init_subclass
            return type_

        def type_new(env, metatype: AbstractType, args: list[AbstractObject], kwargs: dict[str, AbstractObject]):
            name, bases, orig_dict = args
            # name を渡せないが...
            ctx = TypeNewCtx(metatype, args, kwargs, orig_dict, "", bases, None, [], 0, 0, 0, 0, 0)

            self.call = type_call
            res, type_ = type_new_get_bases(env, ctx)
            if res == 1:
                return type_
            type_ = type_new_inpl(env, ctx)
            return type_

        self.call = type_call
        self.new = type_new


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

        self.length = obj_len_func
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

        def divmod_func(env, a: AbstractObject, b: AbstractObject) -> AbstractObject:
            if a.get_type().is_subtype(Int()) and b.type.is_subtype(Int()):
                res = Tuple().create_instance()
                res.special_attr["elt"] = Int().create_instance()
                return res
            return py_not_implemented

        self.add = int_bin_func
        self.sub = int_bin_func
        self.mul = int_bin_func
        self.div = true_div
        self.floordiv = int_bin_func
        self.mod = int_bin_func
        self.pow = pow_func
        self.lshift = int_bin_func
        self.rshift = int_bin_func
        self.or_ = int_bin_func
        self.xor = int_bin_func
        self.and_ = int_bin_func
        # matmul is not implemented
        self.divmod = divmod_func
        self.inplace_add = int_bin_func
        self.inplace_sub = int_bin_func
        self.inplace_mul = int_bin_func
        self.inplace_div = true_div
        self.inplace_floordiv = int_bin_func
        self.inplace_mod = int_bin_func
        self.inplace_pow = pow_func
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


class Complex(BuiltinType):
    def __init__(self):
        super().__init__()


class List(BuiltinType):
    generic_names = ("elt",)

    def __init__(self):
        super().__init__()

        def list_getitem(env, self: AbstractObject, index: int):
            return self.get_obj().special_attr["elt"]

        self.special_attr["elt"] = Undefined()

        self.get_item = list_getitem


class Tuple(BuiltinType):
    generic_names = ("elt",)

    # ToDo: 定数長のタプルへの対応
    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()


class Set(BuiltinType):
    generic_names = ("elt",)

    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()


class Dict(BuiltinType):
    generic_names = ("key", "value")

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

        def iter_next(env, self: AbstractObject):
            seq = self.get_obj().special_attr["seq"]
            return seq.get_type().get_item(env, seq, 0)

        self.iter = self_iter
        self.next = iter_next


class BuiltinFunction(BuiltinType):
    def __init__(self):
        super().__init__()

        def call_func(env, func: AbstractObject, args: list[AbstractObject], kwargs: dict[str, AbstractObject]) -> AbstractObject:
            assert func.function
            return func.function(env, args, kwargs)

        self.call = call_func

    def create_instance(self, function: Optional[function] = None) -> AbstractObject:
        assert function is not None
        obj = super().create_instance()
        obj.function = function
        return obj


class ByteArray(BuiltinType):
    def __init__(self):
        super().__init__()


class Bytes(BuiltinType):
    def __init__(self):
        super().__init__()


class Enumerate(BuiltinType):
    def __init__(self):
        super().__init__()


class Filter(BuiltinType):
    def __init__(self):
        super().__init__()


class Map(BuiltinType):
    def __init__(self):
        super().__init__()


class MemoryView(BuiltinType):
    def __init__(self):
        super().__init__()


class Range(BuiltinType):
    """ range type
    参考: CPython/Objects/rangeobject.c
    iter は RangeIterator を返す
    """

    def __init__(self):
        super().__init__()

        def range_bool(env, o: AbstractObject) -> AbstractObject:
            return Bool().create_instance()

        def range_len(env, o: AbstractObject) -> AbstractObject:
            return Int().create_instance()

        def range_item(env, r: AbstractObject, i: int) -> AbstractObject:
            return Int().create_instance()

        def range_contains(env, r: AbstractObject, obj: AbstractObject) -> AbstractObject:
            return Bool().create_instance()

        def range_richcompare(env, self: AbstractObject, other: AbstractObject, op: int) -> AbstractObject:
            if not other.get_type().is_subtype(Range()):
                return py_not_implemented
            if op == EQ:
                return Bool().create_instance()
            return py_not_implemented

        def range_iter(env, r: AbstractObject) -> AbstractObject:
            return RangeIterator().create_instance()

        def range_new(env, type_: AbstractObject, args: list[AbstractObject], kwargs: dict[str, AbstractObject]) -> AbstractObject:
            start = stop = step = None

            if len(args) == 3:
                start = args[0]
                stop = args[1]
                step = args[2]
            elif len(args) == 2:
                start = args[0]
                stop = args[1]
                step = Int().create_instance()
            elif len(args) == 1:
                start = Int().create_instance()
                stop = args[0]
                step = Int().create_instance()
            else:
                raise errors.TypingError

            obj = Range().create_instance()
            obj.attr["start"] = start
            obj.attr["stop"] = stop
            obj.attr["step"] = step

            return obj

        self.name = "range"
        self.doc = ""
        self.repr = obj_repr_func
        self.bool = range_bool
        self.length = range_len
        self.get_item = range_item
        self.contains = range_contains
        self.hash = obj_hash_func
        # self.getattro
        self.richcompare = range_richcompare
        self.iter = range_iter
        # methods
        # members
        self.new = range_new


class RangeIterator(BuiltinType):
    """ range iterator
    参考: CPython/Objects/rangeobject.c
    """

    def __init__(self):
        super().__init__()

        def rangeiter_next(env, r: AbstractObject) -> AbstractObject:
            return Int().create_instance()

        self.name = "range_iterator"
        self.doc = ""
        # self.getattro
        self.iter = self_iter
        self.next = rangeiter_next
        # methods


class Reversed(BuiltinType):
    def __init__(self):
        super().__init__()


class Zip(BuiltinType):
    def __init__(self):
        super().__init__()


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

descr_get_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject, AbstractObject], AbstractObject]
descr_set_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject, AbstractObject], AbstractObject]
richcmp_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject, int], AbstractObject]

call_function: TypeAlias = Callable[["Environment", AbstractObject, list[AbstractObject], dict[str, AbstractObject]], AbstractObject]
function: TypeAlias = Callable[["Environment", list[AbstractObject], dict[str, AbstractObject]], AbstractObject]

py_not_implemented = NotImplementedType().create_instance()


def obj_len_func(self):
    return Int().create_instance()


def obj_repr_func(self):
    return Str().create_instance()


def obj_hash_func(self):
    return Int().create_instance()


def self_iter(self):
    return self

