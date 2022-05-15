import unittest

from statipy import LenList


class TestRuntime(unittest.TestCase):
    def test_len_annotations(self):
        a: LenList[int, 3] = [1, 2, 3]
        a.append("a")  # type warning
        # in PyCharm2022.1.3, this code does not print a warning,
        #  but the type of a seems to be correctly inferred (list[int])
