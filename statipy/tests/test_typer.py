import unittest

import ast
import statipy.core.typed_ast as t_ast
from statipy.core.environment import Environment
from statipy.core.node_preprocesser import NodePreprocessor
from statipy.core.typer import Typer
from statipy.core.abstract_object import AbstractObject, Int
import statipy.errors as errors

from textwrap import dedent


class TestEnvironment(unittest.TestCase):
    def test_basis(self):
        code = dedent("""\
        a = 0
        if a == 0:
            a = 1
            for i in range(10):
                b = i
            else:
                a = 2
        else:
            a += 1
        """)
        tree = ast.parse(code)
        preprocesser = NodePreprocessor(code)
        preprocessed_tree = preprocesser.make_ast()
        environment = Environment(preprocessed_tree)

        assert isinstance(preprocessed_tree, t_ast.TypedModule)
        assign_1 = preprocessed_tree.body[0]
        assert isinstance(assign_1, t_ast.TypedAssign)
        target_1 = assign_1.targets[0]
        assert isinstance(target_1, t_ast.TypedName)
        if_node = preprocessed_tree.body[1]
        assert isinstance(if_node, t_ast.TypedIf)
        assign_2 = if_node.body[0]
        assert isinstance(assign_2, t_ast.TypedAssign)
        target_2 = assign_2.targets[0]
        assert isinstance(target_2, t_ast.TypedName)
        if_for_node = if_node.body[1]
        assert isinstance(if_for_node, t_ast.TypedFor)
        assign_3 = if_for_node.body[0]
        assert isinstance(assign_3, t_ast.TypedAssign)
        target_3 = assign_3.targets[0]
        assert isinstance(target_3, t_ast.TypedName)
        assign_4 = if_node.orelse[0]
        assert isinstance(assign_4, t_ast.TypedAugAssign)
        target_4 = assign_4.target
        assert isinstance(target_4, t_ast.TypedName)

        int_obj = Int().create_instance()

        environment.assign_variable(assign_1,
                                    target_1.id,
                                    int_obj)

        self.assertEqual(environment.get_variable(if_node.test.left, target_1.id),
                         int_obj)

        environment.step_in(if_node, if_node.body)
        environment.assign_variable(assign_2, target_2.id, int_obj)
        self.assertEqual(environment.get_variable(if_node.test.left, target_1.id),
                         int_obj)
        self.assertEqual(len(environment.variables[target_2.id]), 1)
        self.assertEqual(environment.variables[target_2.id][0].scope.p_node, preprocessed_tree)

        environment.step_in(if_for_node, if_for_node.body)
        environment.assign_variable(assign_3, target_3.id, int_obj)
        self.assertEqual(environment.variables[target_3.id][0].scope.p_node, if_for_node)

        environment.step_out()
        self.assertEqual(environment.current_scope.p_node, if_node)

        environment.step_in(if_for_node, if_for_node.orelse)
        environment.assign_variable(assign_4, target_4.id, int_obj)
        self.assertEqual(environment.variables[target_4.id][0].scope.p_node, preprocessed_tree)

        environment.step_out()
        environment.step_out()
        self.assertEqual(environment.current_scope.p_node, preprocessed_tree)


class TestTyper(unittest.TestCase):
    def test_basis(self):
        code = dedent("""\
        a = 0
        b = "hello"
        a += a + 2
        """)
        typer = Typer(code)
        tree = typer.analyze()

    def test_basis_error(self):
        code = dedent("""\
        a = 0
        b = "hello"
        a = b
        """)
        typer = Typer(code)
        with self.assertRaises(errors.TypingError):
            tree = typer.analyze()
