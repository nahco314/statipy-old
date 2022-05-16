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

        # todo: atteの管理方法を変える
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
        self.bases: Optional[list[AbstractType]] = None

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
                obj.special_attr[key].unification(value)
        return obj

    def is_subtype(self, type_: AbstractType):
        # ToDo
        return self is type_


class BuiltinTypeMeta(type):
    """
    singleton
    """

    def __new__(mcs, name, bases, attrs):
        if name != "BuiltinType":
            __init__ = attrs.get("__init__", object.__init__)

            def wrapper(self, *args, **kwargs):
                if self.__class__._init:
                    return
                self.__class__._init = True
                __init__(self, *args, **kwargs)

            attrs["__init__"] = wrapper

        return super().__new__(mcs, name, bases, attrs)


class BuiltinType(AbstractType, metaclass=BuiltinTypeMeta):
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

    def __repr__(self):
        return f"<BuiltinType {self.__class__.__name__}>"


def object_new(env, type_: AbstractType, *args, **kwargs):
    return type_.create_instance()


class Object(BuiltinType):
    def __init__(self):
        super(Object, self).__init__()

        self.new = object_new

        type_ready(self)


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


def type_ready_set_bases(type_: AbstractType):
    base = type_.base
    if base is None and type_ is not Object():
        base = Object()
    type_.base = base

    # initialize the base class?

    bases = type_.bases
    if bases is None:
        base = type_.base
        if base is None:
            bases = []
        else:
            bases = [base]
        type_.bases = bases


def pmerge(acc: list[AbstractObject], to_merge: list[list[AbstractType]]):
    remain = [0] * len(to_merge)
    empty_cnt = 0
    while True:
        for i in range(len(to_merge)):
            cur_tuple = to_merge[i]
            if remain[i] >= len(cur_tuple):
                empty_cnt += 1
                continue

            candidate = cur_tuple[remain[i]]
            skip = False
            for j in range(len(to_merge)):
                j_lst = to_merge[j]
                if any(a == candidate for a in j_lst[remain[j]+1:]):
                    skip = True
                    break
            if skip:
                continue
            acc.append(candidate)

            for j in range(len(to_merge)):
                j_lst = to_merge[j]
                if remain[j] < len(j_lst) and j_lst[remain[j]] == candidate:
                    remain[j] += 1
            break
        else:
            break
        continue

    if empty_cnt != len(to_merge):
        raise Exception  # todo: mro error


def mro_impl(type_: AbstractType):
    bases = type_.bases
    if len(bases) == 1:
        base = bases[0]
        return [type_, *base.mro]
    to_marge = [*(base.mro for base in bases), bases]

    result = [type_]
    pmerge(result, to_marge)
    return result


def mro_invoke(type_: AbstractType):
    # custom is nani
    mro_result = mro_impl(type_)

    new_mro = mro_result.copy()

    return new_mro


def mro_internal(type_: AbstractType):
    old_mro = type_.mro
    new_mro = mro_invoke(type_)
    # reent = type_.mro != old_mro ?

    type_.mro = new_mro

    # type_mro_modified is nani

    # PyType_Modified is nani

    return old_mro


def type_ready_mro(type_: AbstractType):
    mro_internal(type_)
    # 処理よくわかりません tp_flags考えないといけないんか？


def type_ready(type_: AbstractType):
    # ここいらの関数が必要かどうかは要検討そう
    type_ready_set_bases(type_)
    type_ready_mro(type_)
    # set_new
    # fill_dict
    type_ready_inherit(type_)
    # set_hash
    # add_subclasses
    # post_checks


def type_new_inpl(env, ctx: TypeNewCtx):
    type_ = type_new_init(env, ctx)

    pytype_ready(type_)

    # module
    # doc?
    # ToDo: __new__, __init_subclass__, __class_getitem__, type_new_descriptors, type_new_set_slots,
    #  type_new_set_classcell, type_new_set_names, type_new_init_subclass
    return type_


def type_new(env, metatype: AbstractType, args: list[AbstractObject], kwargs: dict[str, AbstractObject]):
    name, bases, orig_dict = args
    # name を渡せないが...
    ctx = TypeNewCtx(metatype, args, kwargs, orig_dict, "", bases, None, [], 0, 0, 0, 0, 0)

    res, type_ = type_new_get_bases(env, ctx)
    if res == 1:
        return type_
    type_ = type_new_inpl(env, ctx)
    return type_


def copyslot(type_: AbstractType, base: AbstractType, slot_name: str):
    if getattr(type_, slot_name) is None:
        setattr(type_, slot_name, getattr(base, slot_name))


def type_ready_inherit(type_: AbstractType):
    for base in type_.mro[1:]:
        for slot_name, _ in AbstractType.method_table:
            copyslot(type_, base, slot_name)


def pytype_ready(type_: AbstractType):
    type_ready(type_)


class Type(BuiltinType):
    """type type
    参考: CPython/Objects/typeobject.c
    """

    def __init__(self):
        super(Type, self).__init__()

        self.call = type_call
        self.new = type_new

        pytype_ready(self)


class NotImplementedType(BuiltinType):
    def __init__(self):
        super(NotImplementedType, self).__init__()

        pytype_ready(self)


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


class Str(BuiltinType):
    """str type
    参考: CPython/Objects/unicodeobject.c
    """

    def __init__(self):
        super().__init__()

        self.length = obj_len_func
        self.concat = str_concat
        self.repeat = str_repeat
        self.inplace_concat = str_concat
        self.inplace_repeat = str_repeat
        self.get_item = str_getitem
        self.contains = str_contains

        pytype_ready(self)


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


class Int(BuiltinType):
    """int type
    参考: CPython/Objects/longobject.c
    """

    def __init__(self):
        super().__init__()

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

        pytype_ready(self)


class Float(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Complex(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


def list_getitem(env, self: AbstractObject, index: int):
    return self.get_obj().special_attr["elt"]


class List(BuiltinType):
    generic_names = ("elt",)

    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()

        self.get_item = list_getitem

        pytype_ready(self)


class Tuple(BuiltinType):
    generic_names = ("elt",)

    # ToDo: 定数長のタプルへの対応
    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()

        pytype_ready(self)


class Set(BuiltinType):
    generic_names = ("elt",)

    def __init__(self):
        super().__init__()

        self.special_attr["elt"] = Undefined()

        pytype_ready(self)


class Dict(BuiltinType):
    generic_names = ("key", "value")

    def __init__(self):
        super().__init__()

        self.special_attr["key"] = Undefined()
        self.special_attr["value"] = Undefined()

        pytype_ready(self)


class Bool(BuiltinType):
    def __init__(self):
        super().__init__()
        # ToDo: Intを継承させる

        pytype_ready(self)


class Slice(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Iterator(BuiltinType):
    def __init__(self):
        super().__init__()

        def iter_next(env, self: AbstractObject):
            seq = self.get_obj().special_attr["seq"]
            return seq.get_type().get_item(env, seq, 0)

        self.iter = self_iter
        self.next = iter_next

        pytype_ready(self)


def call_func(env, func: AbstractObject, args: list[AbstractObject],
              kwargs: dict[str, AbstractObject]) -> AbstractObject:
    assert func.function
    return func.function(env, args, kwargs)


class BuiltinFunction(BuiltinType):
    def __init__(self):
        super().__init__()

        self.call = call_func

        pytype_ready(self)

    def create_instance(self, function: Optional[function] = None) -> AbstractObject:
        assert function is not None
        obj = super().create_instance()
        obj.function = function
        return obj


class ByteArray(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Bytes(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Enumerate(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Filter(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Map(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class MemoryView(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


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


def range_new(env, type_: AbstractObject, args: list[AbstractObject],
              kwargs: dict[str, AbstractObject]) -> AbstractObject:
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


class Range(BuiltinType):
    """ range type
    参考: CPython/Objects/rangeobject.c
    iter は RangeIterator を返す
    """

    def __init__(self):
        super().__init__()

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

        pytype_ready(self)


def rangeiter_next(env, r: AbstractObject) -> AbstractObject:
    return Int().create_instance()


class RangeIterator(BuiltinType):
    """ range iterator
    参考: CPython/Objects/rangeobject.c
    """

    def __init__(self):
        super().__init__()

        self.name = "range_iterator"
        self.doc = ""
        # self.getattro
        self.iter = self_iter
        self.next = rangeiter_next
        # methods

        pytype_ready(self)


class Reversed(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


class Zip(BuiltinType):
    def __init__(self):
        super().__init__()

        pytype_ready(self)


Attr: TypeAlias = dict[str, AbstractObject]

binary_func: TypeAlias = Callable[["Environment", AbstractObject, AbstractObject], AbstractObject]
ternary_func: TypeAlias = Callable[
    ["Environment", AbstractObject, AbstractObject, Optional[AbstractObject]], AbstractObject]
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

call_function: TypeAlias = Callable[
    ["Environment", AbstractObject, list[AbstractObject], dict[str, AbstractObject]], AbstractObject]
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
