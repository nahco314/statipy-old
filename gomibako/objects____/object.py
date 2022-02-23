from typing import Optional

from statipy.core.abstract_object import AbstractObject, BuiltinType
from gomibako.type_slot import inquiry, repr_func, descrset_func, \
    Slot, PyNumberMethods, \
    PyMethodDef
import statipy.errors as errors
import gomibako.objects____.typeobject as typeobject

# NoneType

none_bool: inquiry = lambda op: 0
none_repr: repr_func = lambda op: "None"


def none_new(type_, *args, **kwargs):
    if args or kwargs:
        raise errors.TypeError
    return BuiltinType.get("NoneType").create_instance()


none_as_number = PyNumberMethods(
    nb_bool=none_bool,
)

BuiltinType.register("NoneType", Slot(
    tp_name="NoneType",
    tp_repr=lambda self: "None",
    tp_new=none_new,
))

# NotImplementedType

NotImplemented_repr: repr_func = lambda op: "NotImplemented"
NotImplemented_reduce = lambda op, Py_UNUSED: "NotImplemented"

notimplemented_methods: PyMethodDef = {
    "__reduce__": NotImplemented_reduce,
}


def notimplemented_new(type_, *args, **kwargs):
    if args or kwargs:
        raise errors.TypeError
    return BuiltinType.get("NotImplementedType").create_instance()


notimplemented_bool: inquiry = lambda v: 1  # todo: Warn?

notimplemented_as_number = PyNumberMethods(
    nb_bool=notimplemented_bool,
)


BuiltinType.register("NotImplementedType", Slot(
    tp_name="NotImplementedType",
    tp_repr=NotImplemented_repr,
    tp_as_number=notimplemented_as_number,
    tp_methods=notimplemented_methods,
    tp_new=notimplemented_new,
))


def pyobject_generic_setattr_with_dict(obj: AbstractObject, name: str, value: AbstractObject,
                                       dict_: Optional[dict[str, AbstractObject]]):
    tp = obj.type
    descr: AbstractObject
    f: descrset_func
    res = -1

    descr = typeobject.pytype_lookup(tp, name)

    if descr is not None:
        f = descr.type.slot.tp_descr_set
        if f is not None:
            res = f(descr, obj, value)
    else:
        if dict_ is None:
            dict_ = obj.attr
            if dict_ is None:
                if descr is None:
                    raise errors.AttributeError(f"{tp.slot.tp_name} has no attribute {name}")
                else:
                    raise errors.AttributeError(f"'{tp.slot.tp_name}' object attribute '{name}' is read-only")
            else:
                dict_[name].unification(value)
                res = 0

        else:
            if value is None:
                if name in dict_:
                    res = 0
                    dict_.pop(name)
                else:
                    res = -1
            else:
                dict_[name].unification(value)

    if res < 0:
        raise errors.AttributeError

    return res
