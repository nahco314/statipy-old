from statipy.core.abstract_object import AbstractObject, py_not_implemented
import statipy.errors as errors


# ここらへんの関数群はAbstractObjectのメソッドにしたほうが良い気がする
# あと、addとかmulとかの関数をまとめたほうが良い気もする
# けど、今のとこまだわからんし変更に手間かかる訳でもないのでとりあえず拡張性高そうでCPythonに合っているこの実装にしておく


def BINARY_FUNC(method_name: str):
    def func(a: AbstractObject, b: AbstractObject) -> AbstractObject:
        res = binary_op1(a, b, method_name)
        if res != py_not_implemented:
            return res

        raise errors.TypeError()
    return func


def index_check(obj: AbstractObject) -> bool:
    return getattr(obj.type, "index", None) is not None  # hasattr?


def binary_op1(a: AbstractObject, b: AbstractObject, op: str) -> AbstractObject:
    a_func = getattr(a.type, op, None)  # ない場合の初期化の仕方これでいい？
    b_func = getattr(b.type, op, None)
    res = py_not_implemented

    if a_func is not None:
        if b_func is not None and b.type.is_subtype(a.type):
            res = b_func(a, b)
            b_func = None
        else:
            res = a_func(a, b)

    if res == py_not_implemented and b_func is not None:
        res = b_func(a, b)

    return res


def binary_i_op1(a: AbstractObject, b: AbstractObject, i_op: str, op: str) -> AbstractObject:
    i_func = getattr(a.type, i_op, None)
    res = py_not_implemented

    if i_func is not None:
        res = i_func(a, b)

    if res == py_not_implemented:
        res = binary_op1(a, b, op)

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


def py_inplace_add(a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_i_op1(a, b, "inplace_add", "add")
    if res != py_not_implemented:
        return res

    # sq.concat?

    raise errors.TypeError()


def py_inplace_mul(a: AbstractObject, b: AbstractObject) -> AbstractObject:
    res = binary_i_op1(a, b, "inplace_mul", "mul")
    if res != py_not_implemented:
        return res

    # sq.concat?

    raise errors.TypeError()


def py_negative(o: AbstractObject) -> AbstractObject:
    f = getattr(o.type, "negative", None)
    if f is not None:
        res = f(o)
        return res

    raise errors.TypeError()


def py_positive(o: AbstractObject) -> AbstractObject:
    f = getattr(o.type, "positive", None)
    if f is not None:
        res = f(o)
        return res

    raise errors.TypeError()


def py_invert(o: AbstractObject) -> AbstractObject:
    f = getattr(o.type, "invert", None)
    if f is not None:
        res = f(o)
        return res

    raise errors.TypeError()
