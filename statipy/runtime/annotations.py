from typing import TypeVar, Type
from types import GenericAlias


T = TypeVar("T")


class LenAlias(GenericAlias):
    def __getitem__(self, params: tuple[Type[T], int]):
        return list[T]


LenList = LenAlias(list, ())
LenTuple = LenAlias(tuple, ())
LenSet = LenAlias(set, ())
LenDict = LenAlias(dict, ())
LenStr = LenAlias(str, ())
