"""
typed_node のコードを自動生成するよ(バージョンが変わったときとか _fields を変えたいときとかのため)
コードの整形はやらないので使う時は IDE とかでやってね
"""


import ast


code = ""
expr_classes = []
stmt_classes = []

for cls in dir(ast):
    obj = getattr(ast, cls)
    if isinstance(obj, type) and issubclass(obj, ast.expr) and obj is not ast.expr:
        expr_classes += [obj]


for cls in dir(ast):
    obj = getattr(ast, cls)
    if isinstance(obj, type) and issubclass(obj, ast.stmt) and obj is not ast.stmt:
        stmt_classes += [obj]


code += "from statipy.core.abstract_object import AbstractObject\nfrom typing import Optional\n\n" \
        "import ast\n\n\n"

code += """class TypedAST(ast.AST):
    passs\n\n\n"""
code += """class Typedexpr(ast.expr, TypedAST):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.abstract_obj: Optional[AbstractObject] = None\n\n\n"""
code += """class Typedstmt(ast.stmt, TypedAST):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)\n\n\n"""

addnl_fields = ("abstract_obj", )

for obj in expr_classes:
    args_s = ", ".join(obj._fields)

    if not obj._fields:
        classdef_code = f"class Typed{obj.__name__}(ast.{obj.__name__}, Typedexpr):\n    pass"

    else:
        classdef_code = f"""class Typed{obj.__name__}(ast.{obj.__name__}, Typedexpr):
    def __init__(self, {args_s}):"""

        for field in obj._fields:
            annotation = "Typedexpr"
            if field[-1] == "s":
                annotation = "list[Typedexpr]"
            classdef_code += f"\n        self.{field}: {annotation} = {field}"

    code += classdef_code + "\n\n\n"


for obj in stmt_classes:
    args_s = ", ".join(obj._fields)

    if not obj._fields:
        classdef_code = f"class Typed{obj.__name__}(ast.{obj.__name__}, Typedstmt):\n    pass"

    else:
        classdef_code = f"""class Typed{obj.__name__}(ast.{obj.__name__}, Typedstmt):
    def __init__(self, {args_s}):"""

        for field in obj._fields:
            annotation = "Typedstmt"
            if field[-1] == "s":
                annotation = "list[Typedstmt]"
            classdef_code += f"\n        self.{field}: {annotation} = {field}"

    code += classdef_code + "\n\n\n"


code += """def from_node(node: ast.AST) -> TypedAST:
    cls_name = node.__class__.__name__
    typed_cls = globals()[f'Typed{cls_name}']

    kwargs = {kw: getattr(node, kw) for kw in node.__class__._fields}

    typed_node = typed_cls(**kwargs)
    return typed_node
"""


print(code)
