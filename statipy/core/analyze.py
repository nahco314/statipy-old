from statipy.core.typer import Typer
import statipy.core.typed_ast as t_ast
from statipy.core.environment import Environment

import ast


def analyze(code: str) -> t_ast.Typedmod:
    """
    Analyze the code and return a result in AST.
    """
    typer = Typer(code)
    result = typer.analyze()
    return result


def analyze_env(code: str) -> tuple[t_ast.Typedmod, Environment]:
    """
    Analyze the code and return AST and Environment with variable information.
    """
    typer = Typer(code)
    result = typer.analyze()
    return result, typer.env
