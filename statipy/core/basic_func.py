from statipy.core.abstract_object import AbstractObject, Dict, Iterator, py_not_implemented, \
    binary_func, binary_i_func, unary_func
import statipy.errors as errors
from statipy.core.environment import Environment
from typing import TypeAlias, Callable, Optional


# ここらへんの関数群はAbstractObjectのメソッドにしたほうが良い気がする
# あと、addとかmulとかの関数をまとめたほうが良い気もする
# けど、今のとこまだわからんし変更に手間かかる訳でもないのでとりあえず拡張性高そうでCPythonに合っているこの実装にしておく


# あと、グローバルとかを参照するためにenv渡してるけどこれあってるのかな(CPythonでどう処理してるのか気になる)


def BINARY_FUNC(method_name: str):
    def func(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
        res = binary_op1(env, a, b, method_name)
        if res != py_not_implemented:
            return res

        raise errors.TypeError()
    return func


def INPLACE_BINARY_FUNC(method_name: str):
    def func(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
        res = binary_i_op1(env, a, b, "inplace_" + method_name, method_name)
        if res != py_not_implemented:
            return res

        raise errors.TypeError()
    return func


def UNARY_FUNC(method_name: str):
    def func(env: Environment, o: AbstractObject) -> AbstractObject:
        f = getattr(o.get_type(), method_name, None)
        if f is not None:
            res = f(env, o)
            return res

        raise errors.TypeError()


def index_check(obj: AbstractObject) -> bool:
    return getattr(obj.get_type(), "index", None) is not None  # hasattr?


def binary_op1(env: Environment, a: AbstractObject, b: AbstractObject, op: str) -> AbstractObject:
    a_func = getattr(a.get_type(), op, None)  # ない場合の初期化の仕方これでいい？
    b_func = getattr(b.get_type(), op, None)
    res = py_not_implemented

    if a_func is not None:
        if b_func is not None and b.get_type().is_subtype(a.get_type()):
            res = b_func(env, a, b)
            b_func = None
        else:
            res = a_func(env, a, b)

    if res == py_not_implemented and b_func is not None:
        res = b_func(env, a, b)

    return res


def binary_i_op1(env: Environment, a: AbstractObject, b: AbstractObject, i_op: str, op: str) -> AbstractObject:
    i_func = getattr(a.get_type(), i_op, None)
    res = py_not_implemented

    if i_func is not None:
        res = i_func(env, a, b)

    if res == py_not_implemented:
        res = binary_op1(env, a, b, op)

    return res


def py_call(
        env: Environment, func: AbstractObject, args: list[AbstractObject], kwargs: dict[str, AbstractObject],
        starred_arg: Optional[AbstractObject] = None, starred_kw: Optional[AbstractObject] = None
        ) -> AbstractObject:
    if starred_arg or starred_kw:
        raise errors.Mijissou
    if kwargs:
        raise errors.Mijissou

    f_call = getattr(func.get_type(), "call", None)
    if f_call is not None:
        return f_call(env, func, args)

    raise errors.TypeError


def py_getattr_string(env: Environment, v: AbstractObject, name: str) -> AbstractObject:
    tp = v.get_type()
    getattr_func = getattr(tp, "getattr", None)
    if getattr_func is not None:
        return getattr_func(env, v, name)

    if tp.tp_getattr is not None:
        result = tp.tp_getattr(env, v, name)
    else:
        raise errors.AttributeError()

    return result


def py_getattr(env: Environment, v: AbstractObject, name: AbstractObject) -> AbstractObject:
    raise errors.Mijissou


def py_setattr_string(env: Environment, v: AbstractObject, name: str, value: AbstractObject) -> None:
    tp = v.get_type()
    setattr_func = getattr(tp, "setattr", None)
    if setattr_func is not None:
        setattr_func(env, v, name, value)

    if tp.tp_setattr is not None:
        tp.tp_setattr(env, v, name, value)
    else:
        raise errors.AttributeError()

    return None


def py_setattr(env: Environment, v: AbstractObject, name: str, value: AbstractObject) -> AbstractObject:
    raise errors.Mijissou


def py_sequence_check(s: AbstractObject) -> bool:
    if s.type.is_subtype(Dict()):
        return False
    return getattr(s.type, "getitem", None) is not None


def py_seq_iter_new(env: Environment, s: AbstractObject) -> AbstractObject:
    it = Iterator().create_instance()
    it.seq = s
    return it


def py_get_iter(env: Environment, o: AbstractObject) -> AbstractObject:
    f = getattr(o.get_type(), "iter", None)
    if f is None:
        if py_sequence_check(o):
            return py_seq_iter_new(env, o)
        raise errors.TypeError
    else:
        res = f(env, o)
        return res


def py_iter_next(env: Environment, iter_: AbstractObject) -> AbstractObject:
    result = iter_.get_type().next(env, iter_)
    if result is None:
        # StopIteration?
        raise Exception
    return result


py_add: binary_func = BINARY_FUNC("add")  # sq.concat?
py_sub: binary_func = BINARY_FUNC("sub")
py_mul: binary_func = BINARY_FUNC("mul")  # sq.repeat?
py_div: binary_func = BINARY_FUNC("div")
py_floordiv: binary_func = BINARY_FUNC("floordiv")
py_mod: binary_func = BINARY_FUNC("mod")
py_pow: binary_func = BINARY_FUNC("pow")
py_lshift: binary_func = BINARY_FUNC("lshift")
py_rshift: binary_func = BINARY_FUNC("rshift")
py_or: binary_func = BINARY_FUNC("or")
py_xor: binary_func = BINARY_FUNC("xor")
py_and: binary_func = BINARY_FUNC("and")
py_matmul: binary_func = BINARY_FUNC("matmul")


py_inplace_add: binary_i_func = INPLACE_BINARY_FUNC("add")  # sq.concat?
py_inplace_sub: binary_i_func = INPLACE_BINARY_FUNC("sub")
py_inplace_mul: binary_i_func = INPLACE_BINARY_FUNC("mul")  # sq.repeat?
py_inplace_div: binary_i_func = INPLACE_BINARY_FUNC("div")
py_inplace_floordiv: binary_i_func = INPLACE_BINARY_FUNC("floordiv")
py_inplace_mod: binary_i_func = INPLACE_BINARY_FUNC("mod")
py_inplace_pow: binary_i_func = INPLACE_BINARY_FUNC("pow")
py_inplace_lshift: binary_i_func = INPLACE_BINARY_FUNC("lshift")
py_inplace_rshift: binary_i_func = INPLACE_BINARY_FUNC("rshift")
py_inplace_or: binary_i_func = INPLACE_BINARY_FUNC("or_")
py_inplace_xor: binary_i_func = INPLACE_BINARY_FUNC("xor")
py_inplace_and: binary_i_func = INPLACE_BINARY_FUNC("and_")
py_inplace_matmul: binary_i_func = INPLACE_BINARY_FUNC("matmul")


py_negative: unary_func = UNARY_FUNC("negative")
py_positive: unary_func = UNARY_FUNC("positive")
py_invert: unary_func = UNARY_FUNC("invert")
