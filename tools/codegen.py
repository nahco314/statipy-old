"""
typed_node のコードを自動生成するよ(バージョンが変わったときとか _fields を変えたいときとかのため)
コードの整形はやらないので使う時は IDE とかでやってね
"""


import ast


code = ""
expr_types = []

for cls in dir(ast):
    obj = getattr(ast, cls)
    if isinstance(obj, type) and issubclass(obj, ast.expr):
        expr_types += [obj]


# exprを最初に持ってくる
expr_types.sort(key=lambda x: 0 if x == ast.expr else 1)


code += "from statipy.core.abstract_object import AbstractObject\n\nimport ast\nfrom ast import "
code += f"({', '.join(map(lambda x: x.__name__, expr_types))})\n\n\n"

addnl_fields = ("abstract_obj", )

for obj in expr_types:
    if obj == ast.expr:
        code += """class Typedexpr(expr):
    def __init__(self, *args, abstract_obj: AbstractObject, **kwargs):
        super().__init__(*args, **kwargs)
        self.abstract_obj = abstract_obj\n\n\n"""
    else:
        classdef_code = f"class Typed{obj.__name__}({obj.__name__}, Typedexpr):\n    _fields = (\n"

        for i in obj._fields + addnl_fields:
            classdef_code += f"        {repr(i)},\n"

        classdef_code += "    )"

        code += classdef_code + "\n\n\n"


code += """def from_node(node: expr, abstract_obj: AbstractObject) -> Typedexpr:
    cls_name = node.__class__.__name__
    typed_cls = globals()[f'Typed{cls_name}']
    
    kwargs = {"abstract_obj": abstract_obj}
    for kw in node.__class__._fields:
        kwargs[kw] = getattr(node, kw)
    
    typed_node = typed_cls(**kwargs)
    return typed_node
"""


print(code)
