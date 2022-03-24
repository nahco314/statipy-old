import unittest

import ast
import statipy.core.typed_ast as t_ast
from statipy.core.node_preprocesser import NodePreprocessor

from textwrap import dedent


class TestNodePreprocessor(unittest.TestCase):
    def test_node_transform(self):
        code = dedent("""\
        1 + 1
        """)
        node = ast.parse(code)

        preprocessor = NodePreprocessor(code)
        a_code = preprocessor.visit(node)

        binop_node = a_code.body[0].value

        self.assertIsInstance(binop_node, t_ast.TypedBinOp)

        op_node = binop_node.op

        self.assertEqual((1, 2, 1, 3), op_node.get_pos())

    def test_transform_stmt(self):
        code = dedent("""\
        def foo(a, b, lst, *args, **kwargs):
            for i in range(a):
                if i == b:
                    print(i, b, *lst, sep=", ")
                    break
                    
            return a + b
        
        
        class Foo(A, metaclass=B):
            AIUEO = 123
        
            def __init__(self, a, b):
                self.a = a
                self.b = b
            
            def test(self):
                return self.a + self.b
        """)
        node = ast.parse(code)

        preprocessor = NodePreprocessor(code)
        a_code = preprocessor.visit(node)


    def test_unary_op(self):
        code = dedent("""\
        -+ -1
        not-True
        """)
        node = ast.parse(code)

        preprocessor = NodePreprocessor(code)
        a_code = preprocessor.visit(node)

        unary_node_1 = a_code.body[0].value
        unary_node_2 = a_code.body[1].value

        self.assertIsInstance(unary_node_1, t_ast.TypedUnaryOp)
        self.assertIsInstance(unary_node_1.operand, t_ast.TypedUnaryOp)
        self.assertIsInstance(unary_node_1.operand.operand, t_ast.TypedUnaryOp)
        self.assertIsInstance(unary_node_2, t_ast.TypedUnaryOp)
        self.assertIsInstance(unary_node_2.operand, t_ast.TypedUnaryOp)

        op_node_1_1 = unary_node_1.op
        op_node_1_2 = unary_node_1.operand.op
        op_node_1_3 = unary_node_1.operand.operand.op
        op_node_2_1 = unary_node_2.op
        op_node_2_2 = unary_node_2.operand.op

        self.assertEqual((1, 0, 1, 1), op_node_1_1.get_pos())
        self.assertEqual((1, 1, 1, 2), op_node_1_2.get_pos())
        self.assertEqual((1, 3, 1, 4), op_node_1_3.get_pos())
        self.assertEqual((2, 0, 2, 3), op_node_2_1.get_pos())
        self.assertEqual((2, 3, 2, 4), op_node_2_2.get_pos())

    def test_boolop(self):
        code = dedent("""\
        a and b and ver and 123 and True and\\
        234 and 345 \\
            and    \\
        False
        """)
        node = ast.parse(code)

        preprocessor = NodePreprocessor(code)
        a_code = preprocessor.visit(node)

        boolop_node = a_code.body[0].value

        self.assertIsInstance(boolop_node, t_ast.TypedBoolOp)

        ops = boolop_node.ops

        actual_indexes = [
            (1, 2, 1, 5),
            (1, 8, 1, 11),
            (1, 16, 1, 19),
            (1, 24, 1, 27),
            (1, 33, 1, 36),
            (2, 4, 2, 7),
            (3, 4, 3, 7),
        ]

        for i, op in enumerate(ops):
            self.assertEqual(actual_indexes[i], op.get_pos())

    def test_compare(self):
        code = dedent("""\
        a==b != c > d<e\\
        <= f \\
          >=\\
        g
        """)
        node = ast.parse(code)

        preprocessor = NodePreprocessor(code)
        a_code = preprocessor.visit(node)

        compare_node = a_code.body[0].value

        self.assertIsInstance(compare_node, t_ast.TypedCompare)

        ops = compare_node.ops

        actual_indexes = [
            (1, 1, 1, 3),
            (1, 5, 1, 7),
            (1, 10, 1, 11),
            (1, 13, 1, 14),
            (2, 0, 2, 2),
            (3, 2, 3, 4),
        ]

        for i, op in enumerate(ops):
            self.assertEqual(actual_indexes[i], op.get_pos())
