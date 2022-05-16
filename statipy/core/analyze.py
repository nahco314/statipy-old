from statipy.core.typer import Typer, TyperBase
import statipy.core.typed_ast as t_ast
from statipy.core.environment import Environment

from typing import Type

import ast


def analyze(code: str, typer_cls: Type[TyperBase] = Typer) -> t_ast.Typedmod:
    """
    Analyze the code and return a result in AST.
    """
    typer = typer_cls(code)
    result = typer.analyze()
    return result


def analyze_env(code: str, typer_cls: Type[TyperBase] = Typer) -> tuple[t_ast.Typedmod, Environment]:
    """
    Analyze the code and return AST and Environment with variable information.
    """
    typer = typer_cls(code)
    result = typer.analyze()
    return result, typer.env
