from typing import TypeVar, Type
from types import GenericAlias


C = TypeVar("C")
T = TypeVar("T")
U = TypeVar("U")


class LenAlias(GenericAlias):
    pass


class LenListAlias(LenAlias):
    def __init__(self):
        super(LenAlias, self).__init__(list, ())

    def __getitem__(self, params: tuple[Type[T], int]):
        return list[T]


class LenSetAlias(LenAlias):
    def __init__(self):
        super(LenAlias, self).__init__(set, ())

    def __getitem__(self, params: tuple[Type[T], int]):
        return set[T]


class LenDictAlias(LenAlias):
    def __init__(self):
        super(LenAlias, self).__init__(dict, ())

    def __getitem__(self, params: tuple[Type[T], Type[U], int]):
        return dict[T, U]


class LenStrAlias(LenAlias):
    def __init__(self):
        super(LenAlias, self).__init__(set, ())

    def __getitem__(self, params: int):
        return str


LenList = LenListAlias()
# tuple is originally assumed to be fixed length, so it is not necessary
LenSet = LenSetAlias()
LenDict = LenDictAlias()
LenStr = LenStrAlias()
