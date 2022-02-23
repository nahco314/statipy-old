from __future__ import annotations

import statipy.core.abstract_object as a
from typing import Optional, TypeAlias, Callable, NamedTuple

# type aliases
# 参考: https://docs.python.org/ja/3/c-api/typeobj.html
getattr_func = Callable[[a.AbstractObject, str], a.AbstractObject]
setattr_func = Callable[[a.AbstractObject, str, a.AbstractObject], None]
repr_func = Callable[[a.AbstractObject], str]
hash_func = Callable[[a.AbstractObject], int]
inquiry = Callable[[a.AbstractObject], int]
richcmp_func = Callable[[a.AbstractObject, a.AbstractObject, int], bool]
getiter_func = Callable[[a.AbstractObject], a.AbstractObject]
iternext_func = Callable[[a.AbstractObject], a.AbstractObject]
descrget_func = Callable[[a.AbstractObject, a.AbstractObject, a.AbstractType], a.AbstractObject]
descrset_func = Callable[[a.AbstractObject, a.AbstractObject, a.AbstractObject], int]
init_proc = Callable[[a.AbstractObject, ...], None]
alloc_func = Callable[[a.AbstractObject, ...], a.AbstractType]
new_func = Callable[[a.AbstractObject, ...], a.AbstractObject]
free_func = Callable[[None], None]
destructor = Callable[[a.AbstractObject], None]
vectorcall_func = Callable[[a.AbstractObject, int, int, int, ...], a.AbstractObject]  # これなに？
unary_func = Callable[[a.AbstractObject], a.AbstractObject]
send_func = Callable[[a.AbstractObject, a.AbstractObject, a.AbstractObject], a.AbstractObject]
binary_func = Callable[[a.AbstractObject, a.AbstractObject], a.AbstractObject]
ternary_func = Callable[[a.AbstractObject, a.AbstractObject, a.AbstractObject], a.AbstractObject]
len_func = Callable[[a.AbstractObject], int]
objobjarg_proc = Callable[[a.AbstractObject, a.AbstractObject, a.AbstractObject], int]  # これなに？
ssizearg_func = Callable[[a.AbstractObject, int], a.AbstractObject]
ssizeobjarg_proc = Callable[[a.AbstractObject, int], int]
objobj_proc = Callable[[a.AbstractObject, a.AbstractObject], int]
getbuffer_proc = Callable[[a.AbstractObject, int], int]
releasegetbuffer_proc = Callable[[a.AbstractObject, ], None]  # Py_buffer ってなに？


class Slot(NamedTuple):
    tp_name: str = None
    # tp_basicsize: int
    # tp_itemsize: int
    # tp_dealloc: int
    # vectorcall_offset: int
    # tp_getattr: getattr_func
    # tp_setattr: setattr_func
    # tp_as_async: PyAsyncMethods
    tp_repr: repr_func = None
    tp_as_number: PyNumberMethods = None
    tp_as_sequence: PySequenceMethods = None
    tp_as_mapping: PyMappingMethods = None
    tp_hash: hash_func = None  # これいる？
    tp_call: Optional[Callable[[a.AbstractObject, ...], a.AbstractObject]] = None
    tp_str: repr_func = None
    tp_getattro: getattr_func = None
    tp_setattro: setattr_func = None
    # tp_as_buffer: PyBufferProcs
    # tp_flags: int
    tp_doc: str = None
    # tp_traverse: TraverseProc
    # tp_clear: inquiry
    tp_richcompare: richcmp_func = None
    # tp_weaklistoffset: a.AbstractObject
    tp_iter: getiter_func = None
    tp_iternext: iternext_func = None
    tp_methods: PyMethodDef = None
    tp_members: PyMemberDef = None
    tp_getset: PyGetSetDef = None
    tp_base: a.AbstractType = None
    tp_dict: dict[str, a.AbstractObject] = None
    tp_descr_get: descrget_func = None
    tp_descr_set: descrset_func = None
    # tp_dictoffset: int
    tp_init: init_proc = None
    tp_alloc: alloc_func = None
    tp_new: new_func = None
    # tp_free: free_func  # これなに？
    # tp_is_gc: inquiry
    tp_bases: tuple[a.AbstractType, ...] = None
    tp_mro: tuple[a.AbstractType, ...] = None
    # tp_cache: a.AbstractObject
    # tp_subclasses: list[a.AbstractObject]
    # tp_weaklist: a.AbstractObject
    # tp_del: destructor
    # tp_version_tag: int
    # tp_finalize: destructor
    # tp_vectorcall: vectorcall_func


class PyAsyncMethods(NamedTuple):
    am_await: unary_func = None
    am_aiter: unary_func = None
    am_anext: unary_func = None
    am_send: send_func = None  # これなに？


class PyNumberMethods(NamedTuple):
    nb_add: binary_func = None
    nb_inplace_add: binary_func = None
    nb_subtract: binary_func = None
    nb_inplace_subtract: binary_func = None
    nb_multiply: binary_func = None
    nb_inplace_multiply: binary_func = None
    nb_remainder: binary_func = None
    nb_inplace_remainder: binary_func = None
    nb_divmod: binary_func = None
    nb_power: ternary_func = None
    nb_inplace_power: ternary_func = None
    nb_negative: unary_func = None
    nb_positive: unary_func = None
    nb_absolute: unary_func = None
    nb_bool: inquiry = None
    nb_invert: unary_func = None
    nb_lshift: binary_func = None
    nb_inplace_lshift: binary_func = None
    nb_and: binary_func = None
    nb_inplace_and: binary_func = None
    nb_xor: binary_func = None
    nb_inplace_xor: binary_func = None
    nb_or: binary_func = None
    nb_inplace_or: binary_func = None
    nb_int: unary_func = None
    nb_reserved: None = None
    nb_float: unary_func = None
    nb_floor_divide: binary_func = None
    nb_inplace_floor_divide: binary_func = None
    nb_true_divide: binary_func = None
    nb_inplace_true_divide: binary_func = None
    nb_index: unary_func = None
    nb_matrix_multiply: binary_func = None
    nb_inplace_matrix_multiply: binary_func = None


class PySequenceMethods(NamedTuple):
    sq_length: len_func = None
    sq_concat: binary_func = None
    sq_repeat: ssizearg_func = None
    sq_item: ssizearg_func = None
    sq_ass_item: ssizeobjarg_proc = None
    sq_contains: objobj_proc = None
    sq_inplace_concat: binary_func = None
    sq_inplace_repeat: ssizearg_func = None


class PyMappingMethods(NamedTuple):
    mp_length: len_func = None
    mp_subscript: binary_func = None
    mp_ass_subscript: objobjarg_proc = None


class PyBufferProcs(NamedTuple):
    bf_getbuffer: getbuffer_proc = None
    bf_releasebuffer: releasegetbuffer_proc = None


PyMethodDef = dict[str, Callable]

PyMemberDef = dict[str, Callable]

PyGetSetDef = dict[str, Callable]
