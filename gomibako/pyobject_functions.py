from statipy.core.abstract_object import AbstractObject
import statipy.errors as errors
from gomibako.type_slot import descrget_func
from typing import Optional


def pyobject_getattr(v: AbstractObject, name: str):
    tp = v.type
    result = None
    if tp.slot.tp_getattro is not None:
        result = tp.slot.tp_getattro(v, name)
    else:
        errors.AttributeError()

    if result is None:
        errors.AttributeError()

    return result


def pyobject_generic_get_attr_with_dict(obj: AbstractObject, name: str, dict_: AbstractObject, suppress: int):
    tp = obj.type
    descr: Optional[AbstractObject] = None
    res: Optional[AbstractObject] = None
    f: Optional[descrget_func] = None

    # ToDo!
