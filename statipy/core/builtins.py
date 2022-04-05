from statipy.core.abstract_object import (AbstractObject,
                                          Int, Str, List, Tuple, Set, Dict, Bool, Slice,
                                          BuiltinFunction,
                                          Undefined)

from statipy.core.basic_func import (py_add, py_sub, py_mul, py_div, py_floordiv, py_mod, py_pow, py_lshift, py_rshift,
                                     py_or, py_xor, py_and, py_matmul,
                                     py_inplace_add, py_inplace_sub, py_inplace_mul, py_inplace_div,
                                     py_inplace_floordiv, py_inplace_mod, py_inplace_pow, py_inplace_lshift,
                                     py_inplace_rshift, py_inplace_or, py_inplace_xor, py_inplace_and,
                                     py_inplace_matmul,
                                     py_abs,
                                     py_call,
                                     py_getattr, py_setattr, py_getattr_string, py_setattr_string,
                                     py_get_iter, py_iter_next,
                                     py_negative, py_positive, py_invert)
from statipy.core.environment import Environment

import statipy.errors as errors


def wrap(func):
    def wrapper(env: Environment, args: list[AbstractObject], kwargs: dict[str, AbstractObject]):
        return func(env, *args, **kwargs)
    return wrapper


abs_ = BuiltinFunction().create_instance(wrap(py_abs))

