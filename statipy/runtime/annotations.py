from typing import TypeVar, Type
from types import GenericAlias


T = TypeVar("T")
U = TypeVar("U")


class LenAlias(GenericAlias):
    container = None

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, cls.container, (), *args, **kwargs)


class LenListAlias(LenAlias):
    container = list

    def __getitem__(self, params: tuple[Type[T], int]):
        return list[T]


class LenSetAlias(LenAlias):
    container = set

    def __getitem__(self, params: tuple[Type[T], int]):
        return set[T]


class LenDictAlias(LenAlias):
    container = dict

    def __getitem__(self, params: tuple[Type[T], Type[U], int]):
        return dict[T, U]


class LenStrAlias(LenAlias):
    container = str

    def __getitem__(self, params: int):
        return str


LenList = LenListAlias()
# tuple is originally assumed to be fixed length, so it is not necessary
LenSet = LenSetAlias()
LenDict = LenDictAlias()
LenStr = LenStrAlias()
