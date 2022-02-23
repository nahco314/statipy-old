import unittest

from statipy.errors import TypingError
from statipy.core.abstract_object import AbstractObject, AbstractType, BuiltinType, Str, Int


class TestAbstractObject(unittest.TestCase):
    def test_builtin_type(self):
        int_ = Int()
        int_2 = Int()
        self.assertIs(int_, int_2)
        a = AbstractObject(int_)

    def test_unification(self):
        int_ = Int()
        str_ = Str()
        a = AbstractObject(int_)
        b = AbstractObject(int_)
        self.assertIsNot(a.get_obj(), b.get_obj())

        a.unification(b)
        self.assertIs(a.get_obj(), b.get_obj())

        with self.assertRaises(AssertionError):
            a.assert_root()

        c = AbstractObject(str_)
        with self.assertRaises(TypingError):
            a.unification(c)
        self.assertIsNot(a.get_obj(), c.get_obj())
