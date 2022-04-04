from statipy.core.abstract_object import AbstractObject, py_not_implemented
import statipy.errors as errors
from statipy.core.environment import Environment


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
        f = getattr(o.type, method_name, None)
        if f is not None:
            res = f(env, o)
            return res

        raise errors.TypeError()


def index_check(obj: AbstractObject) -> bool:
    return getattr(obj.type, "index", None) is not None  # hasattr?


def binary_op1(env: Environment, a: AbstractObject, b: AbstractObject, op: str) -> AbstractObject:
    a_func = getattr(a.type, op, None)  # ない場合の初期化の仕方これでいい？
    b_func = getattr(b.type, op, None)
    res = py_not_implemented

    if a_func is not None:
        if b_func is not None and b.type.is_subtype(a.type):
            res = b_func(env, a, b)
            b_func = None
        else:
            res = a_func(env, a, b)

    if res == py_not_implemented and b_func is not None:
        res = b_func(env, a, b)

    return res


def binary_i_op1(env: Environment, a: AbstractObject, b: AbstractObject, i_op: str, op: str) -> AbstractObject:
    i_func = getattr(a.type, i_op, None)
    res = py_not_implemented

    if i_func is not None:
        res = i_func(env, a, b)

    if res == py_not_implemented:
        res = binary_op1(env, a, b, op)

    return res


py_add = BINARY_FUNC("add")  # sq.concat?
py_sub = BINARY_FUNC("sub")
py_mul = BINARY_FUNC("mul")  # sq.repeat?
py_div = BINARY_FUNC("div")
py_floordiv = BINARY_FUNC("floordiv")
py_mod = BINARY_FUNC("mod")
py_pow = BINARY_FUNC("pow")
py_lshift = BINARY_FUNC("lshift")
py_rshift = BINARY_FUNC("rshift")
py_or = BINARY_FUNC("or")
py_xor = BINARY_FUNC("xor")
py_and = BINARY_FUNC("and")
py_matmul = BINARY_FUNC("matmul")


py_inplace_add = INPLACE_BINARY_FUNC("add")  # sq.concat?
py_inplace_sub = INPLACE_BINARY_FUNC("sub")
py_inplace_mul = INPLACE_BINARY_FUNC("mul")  # sq.repeat?
py_inplace_div = INPLACE_BINARY_FUNC("div")
py_inplace_floordiv = INPLACE_BINARY_FUNC("floordiv")
py_inplace_mod = INPLACE_BINARY_FUNC("mod")
py_inplace_pow = INPLACE_BINARY_FUNC("pow")
py_inplace_lshift = INPLACE_BINARY_FUNC("lshift")
py_inplace_rshift = INPLACE_BINARY_FUNC("rshift")
py_inplace_or = INPLACE_BINARY_FUNC("or")
py_inplace_xor = INPLACE_BINARY_FUNC("xor")
py_inplace_and = INPLACE_BINARY_FUNC("and")
py_inplace_matmul = INPLACE_BINARY_FUNC("matmul")


py_negative = UNARY_FUNC("negative")
py_positive = UNARY_FUNC("positive")
py_invert = UNARY_FUNC("invert")
