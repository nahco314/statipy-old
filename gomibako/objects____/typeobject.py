from typing import Optional, NamedTuple

from statipy.core.abstract_object import AbstractObject, AbstractType, BuiltinType
from gomibako.type_slot import repr_func, new_func, binary_func, ternary_func, descrget_func, \
    getattr_func, setattr_func, init_proc,\
    Slot, PyNumberMethods, \
    PyMethodDef, PyGetSetDef
import statipy.errors as errors
import statipy.versions as versions
import gomibako.objects____.object as object_

# type type


slotdefs = (
    ("__getattribute__", "tp_getattr"),
    ("__getattr__", "tp_getattr"),
    ("__setattr__", "tp_setattr"),
    ("__delattr__", "tp_setattr"),
    ("__repr__", "tp_repr"),
    ("__hash__", "tp_hash"),
    ("__call__", "tp_call"),
    ("__str__", "tp_str"),
    ("__getattribute__", "tp_getattro"),
    ("__getattr__", "tp_getattro"),
    ("__setattr__", "tp_setattro"),
    ("__delattr__", "tp_setattro"),
    ("__lt__", "tp_richcompare"),
    ("__le__", "tp_richcompare"),
    ("__eq__", "tp_richcompare"),
    ("__ne__", "tp_richcompare"),
    ("__gt__", "tp_richcompare"),
    ("__ge__", "tp_richcompare"),
    ("__iter__", "tp_iter"),
    ("__next__", "tp_iternext"),
    ("__get__", "tp_descr_get"),
    ("__set__", "tp_descr_set"),
    ("__delete__", "tp_descr_set"),
    ("__init__", "tp_init"),
    ("__new__", "tp_new"),
    ("__del__", "tp_finalize"),
    ("__await__", "am_await"),
    ("__aiter__", "am_aiter"),
    ("__anext__", "am_anext"),
    ("__add__", "nb_add"),
    ("__radd__", "nb_add"),
    ("__sub__", "nb_subtract"),
    ("__rsub__", "nb_subtract"),
    ("__mul__", "nb_multiply"),
    ("__rmul__", "nb_multiply"),
    ("__mod__", "nb_remainder"),
    ("__rmod__", "nb_remainder"),
    ("__divmod__", "nb_divmod"),
    ("__rdivmod__", "nb_divmod"),
    ("__pow__", "nb_power"),
    ("__rpow__", "nb_power"),
    ("__neg__", "nb_negative"),
    ("__pos__", "nb_positive"),
    ("__abs__", "nb_absolute"),
    ("__bool__", "nb_bool"),
    ("__invert__", "nb_invert"),
    ("__lshift__", "nb_lshift"),
    ("__rlshift__", "nb_lshift"),
    ("__rshift__", "nb_rshift"),
    ("__rrshift__", "nb_rshift"),
    ("__and__", "nb_and"),
    ("__rand__", "nb_and"),
    ("__xor__", "nb_xor"),
    ("__rxor__", "nb_xor"),
    ("__or__", "nb_or"),
    ("__ror__", "nb_or"),
    ("__int__", "nb_int"),
    ("__float__", "nb_float"),
    ("__iadd__", "nb_inplace_add"),
    ("__isub__", "nb_inplace_subtract"),
    ("__imul__", "nb_inplace_multiply"),
    ("__imod__", "nb_inplace_remainder"),
    ("__ipow__", "nb_inplace_power"),
    ("__ilshift__", "nb_inplace_lshift"),
    ("__irshift__", "nb_inplace_rshift"),
    ("__iand__", "nb_inplace_and"),
    ("__ixor__", "nb_inplace_xor"),
    ("__ior__", "nb_inplace_or"),
    ("__floordiv__", "nb_floor_divide"),
    ("__rfloordiv__", "nb_floor_divide"),
    ("__truediv__", "nb_true_divide"),
    ("__rtruediv__", "nb_true_divide"),
    ("__ifloordiv__", "nb_inplace_floor_divide"),
    ("__itruediv__", "nb_inplace_true_divide"),
    ("__index__", "nb_index"),
    ("__matmul__", "nb_matrix_multiply"),
    ("__rmatmul__", "nb_matrix_multiply"),
    ("__imatmul__", "nb_inplace_matrix_multiply"),
    ("__len__", "mp_length"),
    ("__getitem__", "mp_subscript"),
    ("__setitem__", "mp_ass_subscript"),
    ("__delitem__", "mp_ass_subscript"),
    ("__len__", "sq_length"),
    ("__add__", "sq_concat"),
    ("__mul__", "sq_repeat"),
    ("__rmul__", "sq_repeat"),
    ("__getitem__", "sq_item"),
    ("__setitem__", "sq_ass_item"),
    ("__delitem__", "sq_ass_item"),
    ("__contains__", "sq_contains"),
    ("__iadd__", "sq_inplace_concat"),
    ("__imul__", "sq_inplace_repeat"),

)


class TypeNewCtx(NamedTuple):
    metatype: AbstractType
    args: list[AbstractObject]
    kwargs: dict[str, AbstractObject]
    orig_dict: dict[str, AbstractObject]  # ?
    name: str
    bases: Optional[tuple[AbstractObject]]
    base: Optional[AbstractObject]
    slots: None  # ToDo: ?
    nslot: int
    add_dict: int
    add_weak: int
    may_add_dict: int
    may_add_weak: int


def is_dunder_name(name: str):
    return len(name) > 4 and name[0] == name[1] == name[-1] == name[-2] == "_"


def find_name_in_mro(type_: AbstractType, name: str):
    mro = type_.slot.tp_mro

    for base in mro:
        dict_ = base.slot.tp_dict
        res = dict_.get(name)
        if res:
            return res

    return None


def pytype_lookup(type_: AbstractType, name: str):
    # todo: cache? (Objects.typeobject.c: 3829)
    res = find_name_in_mro(type_, name)
    return res


def type_module(type_: AbstractType, context):
    # ToDo
    pass


def type_repr(type_: AbstractType):
    if type_.slot.tp_name is None:
        return f"<class at {id(type_)}>"

    mod = None  # ToDo: module (Objects.typeobject.c: 1052)

    return f"<class {type_.slot.tp_name}>"


def type_call(type_: AbstractType, *args: AbstractObject, **kwargs: AbstractObject):
    obj: AbstractObject

    if type_ == BuiltinType.get("type"):
        assert len(args) != 0
        assert len(kwargs) == 0

        if len(args) == 1:
            obj = type_.type
            return obj

        if len(args) != 3:
            raise errors.TypeError("type() takes 1 or 3 arguments")

    if type_.slot.tp_new is None:
        raise errors.TypeError(f"cannot create '{type_.slot.tp_name}' instances")

    obj = type_.slot.tp_new(type_, *args, **kwargs)
    # _Py_CheckFunctionResult is 何？
    if obj is None:
        return None

    if not pytype_is_subtype(obj.type, type_):
        return obj

    type_ = obj.type
    if type_.slot.tp_init is not None:
        res = type_.slot.tp_init(obj, *args, **kwargs)
        assert res is None

    return obj


def type_getattro(type_: AbstractType, name: str):
    metatype = type_.type
    meta_attrute = pytype_lookup(metatype, name)
    meta_get = None

    if meta_attrute:
        meta_get = meta_attrute.type.slot.tp_descr_get

        if (meta_get is not None) and (meta_attrute.type.slot.tp_descr_set is not None):
            res = meta_get(meta_attrute, type_, metatype)
            return res

    attribute = pytype_lookup(type_, name)
    if attribute:
        local_get: descrget_func = attribute.type.slot.tp_descr_get

        if local_get is not None:
            res = local_get(attribute, None, type_)  # None はなに...? わからん
            return res

        return attribute

    if meta_get:
        res = meta_get(meta_attrute, type_, metatype)
        return res

    if meta_attrute:
        return meta_attrute

    raise errors.AttributeError(f"type object '{type_.slot.tp_name}' has no attribute '{name}'")


def update_slot(type_: AbstractType, name: str):
    slots = []
    for method_name, slot_name in slotdefs:
        if method_name == name:
            slots.append((method_name, slot_name))

    for method_name, slot_name in slots:
        setattr(type_.slot, slot_name, getattr(type_.attr, method_name))

    return 0  # update_subclasses()が何をしているのかわかりません！


def type_setattro(type_: AbstractType, name: str, value: AbstractObject):
    res = object_.pyobject_generic_setattr_with_dict(type_, name, value, None)
    if res == 0:
        if is_dunder_name(name):
            res = update_slot(type_, name)

    return res


def pytype_calculate_metaclass(metatype: AbstractType, bases: tuple[AbstractType]):
    winner = metatype
    for tmp in bases:
        tmptype = tmp.type
        if pytype_is_subtype(winner, tmptype):
            continue
        if pytype_is_subtype(tmptype, winner):
            winner = tmptype
            continue
        raise errors.TypeError("metaclass conflict: "
                        "the metaclass of a derived class "
                        "must be a (non-strict) subclass "
                        "of the metaclasses of all its bases")

    return winner


def extra_ivars(type_: AbstractType, base: AbstractType):
    # TODO
    return False


def solid_base(type_: AbstractType):
    base: AbstractType
    if type_.slot.tp_base:
        base = solid_base(type_.slot.tp_base)
    else:
        base = BuiltinType.get("object").create_instance()

    if extra_ivars(type_, base):
        return type_
    else:
        return base


def best_base(bases: tuple[AbstractType]):
    base = None
    winner = None
    for base_proto in bases:
        candidate = solid_base(base_proto)
        if winner is None:
            winner = candidate
            base = base_proto
        elif pytype_is_subtype(winner, candidate):
            pass
        elif pytype_is_subtype(candidate, winner):
            winner = candidate
            base = base_proto
        else:
            raise errors.TypeError("multiple bases have "
                "instance lay-out conflict")

    assert base is not None

    return base


def type_new_get_bases(ctx: TypeNewCtx):
    if ctx.bases is None or len(ctx.bases) == 0:
        ctx.base = BuiltinType.get("object").create_instance()
        new_bases = (ctx.base,)
        ctx.bases = new_bases
        return 0

    ctx.bases: tuple[AbstractType]  # for type checker (PyCharm)

    for base in ctx.bases:
        pass  # ToDo: ?

    winner = pytype_calculate_metaclass(ctx.metatype, ctx.bases)
    if winner != ctx.metatype:
        if winner.slot.tp_new != type_new:
            type_ = winner.slot.tp_new(winner, *ctx.args, **ctx.kwargs)
            return type_, 1

        ctx.metatype = winner

    base = best_base(ctx.bases)
    ctx.base = base
    return None, 0


def type_init(metatype: AbstractType, *args, **kwargs):
    if len(kwargs) != 0:
        raise errors.TypeError("type.__init__() takes no keyword arguments")
    if len(args) != 1 and len(args) != 3:
        raise errors.TypeError("type.__init__() takes 1 or 3 arguments")

    return 0


def type_new_alloc(ctx: TypeNewCtx):
    metatype = ctx.metatype
    type_ = metatype.slot.tp_alloc(metatype, ctx.nslot)
    if type_ is None:
        return None
    et = type_
    type_.slot.tp_bases = ctx.bases
    type_.base = ctx.base
    return type_


def type_new_init(ctx: TypeNewCtx):
    # これはなに
    dict_ = ctx.orig_dict.copy()
    type_ = type_new_alloc(ctx)

    type_.slot.tp_dict = dict_
    return type_


def type_new_impl(ctx: TypeNewCtx):
    type_ = type_new_init(ctx)
    # set_attrs
    type_.slot.tp_name = ctx.name

    # ToDo: type_new_init

    return type_


def type_new(metatype: AbstractType, *args, **kwargs):
    assert len(args) != 0
    assert len(kwargs) == 0

    # ToDo: ?
    name = args[0]
    bases = args[1] if len(args) > 1 else None
    orig_dict = args[2] if len(args) > 2 else None

    ctx = TypeNewCtx(
        metatype=metatype,
        args=args,  # type...
        kwargs=kwargs,
        orig_dict=orig_dict,
        name=name,
        bases=bases,
        base=None,
        slots=None,
        nslot=0,
        add_dict=0,
        add_weak=0,
        may_add_dict=0,
        may_add_weak=0,
    )

    res, type_ = type_new_get_bases(ctx)
    if res == 1:
        return type_

    type_ = type_new_impl(ctx)
    return type_


_Py_union_type_or: Optional[binary_func] = None  # ToDo: union type (Objects.typeobject.c: 4339)
if versions.HAS_TYPE_UNION:
    pass

type_as_number = PyNumberMethods(
    nb_or=_Py_union_type_or,
)

type_methods: PyMethodDef = {
    # ToDo
}


type_members: PyMethodDef = {
    # ToDo
}


type_getsets: PyGetSetDef = {
    # ToDo
}

type_repr: repr_func
type_call: ternary_func
type_getattro: getattr_func
type_setattro: setattr_func
type_init: init_proc
type_new: new_func  # type check をいい感じにする

BuiltinType.register("type", Slot(
    tp_name="type",
    tp_repr=type_repr,
    tp_as_number=type_as_number,
    tp_call=type_call,
    tp_getattro=type_getattro,
    tp_setattro=type_setattro,
    tp_methods=type_methods,
    tp_members=type_members,
    tp_getset=type_getsets,
    tp_init=type_init,
    tp_new=type_new,
))


def pytype_is_subtype(a: AbstractType, b: AbstractType) -> bool:
    # ToDo
    return True
