import ast
from ast import NodeTransformer

from statipy.core.typed_ast import *
from statipy.core.node_preprocesser import NodePreprocessor
from statipy.core.abstract_object import AbstractObject, Int, Str, List, Tuple, Set, Dict, Undefined

from statipy.core.basic_func import py_add, py_mul, py_inplace_add, py_inplace_mul

from statipy.core.environment import Environment
import statipy.errors as errors

from typing import Any


class Typer(NodeTransformer):
    def __init__(self, code: str, context: Environment = None):
        self.t_ast = NodePreprocessor(code).make_ast()
        if context is None:
            context = Environment(self.t_ast)
        self.context = context

    def analysis(self) -> Typedmod:
        self.visit(self.t_ast)
        return self.t_ast
