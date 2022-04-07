from statipy.core.abstract_object import (AbstractObject,
                                          Type, Object, Int, Float, Complex, Str, List, Tuple, Set, Dict, Bool, Slice,
                                          BuiltinFunction, ByteArray, Bytes, Enumerate, Filter, Map, MemoryView,
                                          Range, Reversed, Zip,
                                          Undefined)

from statipy.core.basic_func import (py_add, py_sub, py_mul, py_div, py_floordiv, py_mod, py_pow, py_lshift, py_rshift,
                                     py_or, py_xor, py_and, py_matmul, py_divmod,
                                     py_inplace_add, py_inplace_sub, py_inplace_mul, py_inplace_div,
                                     py_inplace_floordiv, py_inplace_mod, py_inplace_pow, py_inplace_lshift,
                                     py_inplace_rshift, py_inplace_or, py_inplace_xor, py_inplace_and,
                                     py_inplace_matmul,
                                     py_abs, py_ascii, py_repr, py_hash, py_len,
                                     py_call,
                                     py_getattr, py_setattr, py_getattr_string, py_setattr_string,
                                     py_get_iter, py_iter_next,
                                     py_negative, py_positive, py_invert,
                                     index_check, callable_check,
                                     py_type_lookup_special,
                                     )
from statipy.core.environment import Environment

import statipy.errors as errors


def wrap(func):
    def wrapper(env: Environment, args: list[AbstractObject], kwargs: dict[str, AbstractObject]):
        return func(env, *args, **kwargs)
    return wrapper


def builtin_all(env: Environment, iterable: AbstractObject) -> AbstractObject:
    it = py_get_iter(env, iterable)
    iternext = it.get_type().next

    item = iternext(env, it)  # __bool__ を評価せねば...

    return Bool().create_instance()


def builtin_any(env: Environment, iterable: AbstractObject) -> AbstractObject:
    it = py_get_iter(env, iterable)
    iternext = it.get_type().next

    item = iternext(env, it)  # __bool__ を評価せねば...

    return Bool().create_instance()


def builtin_bin(env: Environment, x: AbstractObject) -> AbstractObject:
    if not index_check(x):
        raise errors.TypingError
    x.get_type().index(env, x)
    return Str().create_instance()


def builtin_callable(env: Environment, obj: AbstractObject) -> AbstractObject:
    callable_check(obj)
    return Bool().create_instance()


def builtin_chr(env: Environment, arg: AbstractObject) -> AbstractObject:
    if not index_check(arg):
        raise errors.TypingError
    arg.get_type().index(env, arg)
    return Str().create_instance()


def builtin_exit(env: Environment) -> AbstractObject:
    pass


def builtin_hex(env: Environment, x: AbstractObject) -> AbstractObject:
    if not index_check(x):
        raise errors.TypingError
    x.get_type().index(env, x)
    return Str().create_instance()


def builtin_input(env: Environment) -> AbstractObject:
    return Str().create_instance()


def builtin_max(env: Environment, *args: AbstractObject) -> AbstractObject:
    if len(args) == 0:
        raise errors.TypingError
    elif len(args) == 1:
        res = args[0].get_obj().special_attr["elt"].get_obj()
        return res
    else:
        res = args[0].get_obj()
        for arg in args[1:]:
            res.get_obj().unification(arg.get_obj())
        return res.get_obj()


def builtin_min(env: Environment, *args: AbstractObject) -> AbstractObject:
    if len(args) == 0:
        raise errors.TypingError
    elif len(args) == 1:
        res = args[0].get_obj().special_attr["elt"].get_obj()
        return res
    else:
        res = args[0].get_obj()
        for arg in args[1:]:
            res.get_obj().unification(arg.get_obj())
        return res.get_obj()


def builtin_oct(env: Environment, x: AbstractObject) -> AbstractObject:
    if not index_check(x):
        raise errors.TypingError
    x.get_type().index(env, x)
    return Str().create_instance()


def builtin_ord(env: Environment, c: AbstractObject) -> AbstractObject:
    if c.get_type().is_subtype(Str()) or c.get_type().is_subtype(Bytes()) and c.get_type().is_subtype(ByteArray()):
        return Int().create_instance()
    else:
        raise errors.TypingError


def builtin_print(env: Environment, *args: AbstractObject) -> AbstractObject:
    pass  # ToDo


def builtin_quit(env: Environment) -> AbstractObject:
    pass


def builtin_round(env: Environment, x: AbstractObject, n: AbstractObject) -> AbstractObject:
    round_func = py_type_lookup_special(env, x, "__round__")
    if round_func is None:
        raise errors.TypingError

    res = py_call(env, round_func.get_obj(), [x, n], {})
    return res


def builtin_sorted(env: Environment, self: AbstractObject) -> AbstractObject:
    py_get_iter(env, self)
    # 比較の評価しなきゃ
    return self


def builtin_sum(env: Environment, iterable: AbstractObject, start: AbstractObject = None) -> AbstractObject:
    if start is None:
        start = Int().create_instance()

    it = py_get_iter(env, iterable)
    iternext = it.get_type().next

    start = py_inplace_add(env, start, iternext)
    return start


abs_ = BuiltinFunction().create_instance(wrap(py_abs))
all_ = BuiltinFunction().create_instance(wrap(builtin_all))
any_ = BuiltinFunction().create_instance(wrap(builtin_any))
ascii_ = BuiltinFunction().create_instance(wrap(py_ascii))
bin_ = BuiltinFunction().create_instance(wrap(builtin_bin))
bool_ = Bool()
bytearray_ = ByteArray()
bytes_ = Bytes()
callable_ = BuiltinFunction().create_instance(wrap(builtin_callable))
chr_ = BuiltinFunction().create_instance(wrap(builtin_chr))
complex_ = Complex()
dict_ = Dict()
divmod_ = BuiltinFunction().create_instance(wrap(py_divmod))
enumerate_ = Enumerate()
exit_ = BuiltinFunction().create_instance(wrap(builtin_exit))
filter_ = Filter()
float_ = Float()
getattr_ = BuiltinFunction().create_instance(wrap(py_getattr))
hash_ = BuiltinFunction().create_instance(wrap(py_hash))
hex_ = BuiltinFunction().create_instance(wrap(builtin_hex))
input_ = BuiltinFunction().create_instance(wrap(builtin_input))
int_ = Int()
iter_ = BuiltinFunction().create_instance(wrap(py_get_iter))
len_ = BuiltinFunction().create_instance(wrap(py_len))
list_ = List()
map_ = Map()
max_ = BuiltinFunction().create_instance(wrap(builtin_max))
memoryview_ = MemoryView()
min_ = BuiltinFunction().create_instance(wrap(builtin_min))
next_ = BuiltinFunction().create_instance(wrap(py_iter_next))
object_ = Object()
oct_ = BuiltinFunction().create_instance(wrap(builtin_oct))
ord_ = BuiltinFunction().create_instance(wrap(builtin_ord))
pow_ = BuiltinFunction().create_instance(wrap(py_pow))
print_ = BuiltinFunction().create_instance(wrap(builtin_print))
quit_ = BuiltinFunction().create_instance(wrap(builtin_quit))
range_ = Range()
repr_ = BuiltinFunction().create_instance(wrap(py_repr))
reversed_ = Reversed()
round_ = BuiltinFunction().create_instance(wrap(builtin_round))
set_ = Set()
setattr_ = BuiltinFunction().create_instance(wrap(py_setattr))
slice_ = Slice()
sorted_ = BuiltinFunction().create_instance(wrap(builtin_sorted))
str_ = Str()
sum_ = BuiltinFunction().create_instance(wrap(builtin_sum))
tuple_ = Tuple()
type_ = Type()
zip_ = Zip()
