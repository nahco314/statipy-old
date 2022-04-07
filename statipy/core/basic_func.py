from statipy.core.abstract_object import AbstractObject, AbstractType, \
    Str, Dict, Iterator, py_not_implemented, \
    binary_func, ternary_func, unary_func, ssizeargfunc
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


def TERNARY_FUNC(method_name: str):
    def func(env: Environment, a: AbstractObject, b: AbstractObject, c: Optional[AbstractObject]) -> AbstractObject:
        func = getattr(a.get_type(), method_name, None)
        if func is not None:
            return func(env, a, b, c)

        raise errors.TypeError()
    return func


def INPLACE_TERNARY_FUNC(method_name: str):
    def func(env: Environment, a: AbstractObject, b: AbstractObject, c: Optional[AbstractObject]) -> AbstractObject:
        func = getattr(a.get_type(), method_name, None)
        if func is not None:
            return func(env, a, b, c)

        raise errors.TypeError()
    return func


def UNARY_FUNC(method_name: str):
    def func(env: Environment, o: AbstractObject) -> AbstractObject:
        f = getattr(o.get_type(), method_name, None)
        if f is not None:
            res = f(env, o)
            return res

        raise errors.TypeError()
    return func


def index_check(obj: AbstractObject) -> bool:
    return getattr(obj.get_type(), "index", None) is not None  # hasattr?


def callable_check(obj: AbstractObject) -> bool:
    return getattr(obj.get_type(), "call", None) is not None


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
        return f_call(env, func, args, {})

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


def py_abs(env: Environment, o: AbstractObject) -> AbstractObject:
    f = getattr(o.get_type(), "abs", None)
    if f is not None:
        res = f(env, o)
        return res

    raise errors.TypeError


def py_repr(env: Environment, v: AbstractObject) -> AbstractObject:
    if v.get_type().repr is None:
        raise errors.TypingError

    res = v.get_type().repr(env, v)
    return res


def py_ascii(env: Environment, v: AbstractObject) -> AbstractObject:
    repr = py_repr(env, v)
    ascii_ = Str().create_instance()
    return ascii_


def py_hash(env: Environment, v: AbstractObject) -> AbstractObject:
    if v.get_type().hash is None:
        raise errors.TypingError

    res = v.get_type().hash(env, v)
    return res


def py_len(env: Environment, v: AbstractObject) -> AbstractObject:
    if v.get_type().len is None:
        raise errors.TypingError

    res = v.get_type().len(env, v)
    return res


def py_add(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_op1(env, a, b, "add")

    if res == py_not_implemented and a.get_type().concat is not None:
        res = a.get_type().concat(env, a, b)

    if res != py_not_implemented:
        return res

    raise errors.TypeError()


def repeat(env: Environment, repeatfunc: ssizeargfunc, seq: AbstractObject, n: AbstractObject) -> AbstractObject:
    if index_check(n):
        count = 0  # index の評価
    else:
        raise errors.TypingError

    res = repeatfunc(env, seq, count)
    return res


def py_mul(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_op1(env, a, b, "mul")

    if res == py_not_implemented:
        ma = getattr(a.get_type(), "repeat", None)
        mb = getattr(b.get_type(), "repeat", None)
        if ma is not None:
            res = repeat(env, ma, a, b)
        elif mb is not None:
            res = repeat(env, mb, b, a)

    if res != py_not_implemented:
        return res

    raise errors.TypeError()


# py_add
py_sub: binary_func = BINARY_FUNC("sub")
# py_mul
py_div: binary_func = BINARY_FUNC("div")
py_floordiv: binary_func = BINARY_FUNC("floordiv")
py_mod: binary_func = BINARY_FUNC("mod")
py_pow: ternary_func = BINARY_FUNC("pow")
py_lshift: binary_func = BINARY_FUNC("lshift")
py_rshift: binary_func = BINARY_FUNC("rshift")
py_or: binary_func = BINARY_FUNC("or")
py_xor: binary_func = BINARY_FUNC("xor")
py_and: binary_func = BINARY_FUNC("and")
py_matmul: binary_func = BINARY_FUNC("matmul")
py_divmod: binary_func = BINARY_FUNC("divmod")


def py_inplace_add(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_op1(env, a, b, "inplace_add")

    if res == py_not_implemented and a.get_type().inplace_concat is not None:
        res = a.get_type().concat(env, a, b)

    if res != py_not_implemented:
        return res

    raise errors.TypeError()


def py_inplace_mul(env: Environment, a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_op1(env, a, b, "inplace_mul")

    if res == py_not_implemented:
        ma = getattr(a.get_type(), "inplace_repeat", None)
        mb = getattr(b.get_type(), "inplace_repeat", None)
        if ma is not None:
            res = repeat(env, ma, a, b)
        elif mb is not None:
            res = repeat(env, mb, b, a)

    if res != py_not_implemented:
        return res

    raise errors.TypeError()


# py_inplace_add
py_inplace_sub: binary_func = INPLACE_BINARY_FUNC("sub")
# py_inplace_mul
py_inplace_div: binary_func = INPLACE_BINARY_FUNC("div")
py_inplace_floordiv: binary_func = INPLACE_BINARY_FUNC("floordiv")
py_inplace_mod: binary_func = INPLACE_BINARY_FUNC("mod")
py_inplace_pow: ternary_func = INPLACE_BINARY_FUNC("pow")
py_inplace_lshift: binary_func = INPLACE_BINARY_FUNC("lshift")
py_inplace_rshift: binary_func = INPLACE_BINARY_FUNC("rshift")
py_inplace_or: binary_func = INPLACE_BINARY_FUNC("or_")
py_inplace_xor: binary_func = INPLACE_BINARY_FUNC("xor")
py_inplace_and: binary_func = INPLACE_BINARY_FUNC("and_")
py_inplace_matmul: binary_func = INPLACE_BINARY_FUNC("matmul")


py_negative: unary_func = UNARY_FUNC("negative")
py_positive: unary_func = UNARY_FUNC("positive")
py_invert: unary_func = UNARY_FUNC("invert")


def find_name_in_mro(type_: AbstractType, name: str) -> AbstractObject:
    mro = type_.mro
    res = None
    n = len(mro)
    for i in range(n):
        base = mro[i]
        res = base.attr[name]
        if res is not None:
            break
    return res


def py_type_lookup(env: Environment, type_: AbstractType, name: str) -> AbstractObject:
    res = find_name_in_mro(type_, name)
    return res


def py_type_lookup_special(env: Environment, self: AbstractObject, attrid: str) -> AbstractObject:
    res = py_type_lookup(env, self.get_type(), attrid)
    if res is not None:
        f = res.get_type().get_callable()
        if f is not None:
            res = f(env, res, self, self.get_type())
    return res
