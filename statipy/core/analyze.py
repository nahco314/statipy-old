from statipy.core.typer import Typer
import ast


def analyze(code: str):
    """
    Analyze the code and return a dict with the results.
    """
    typer = Typer(code)
    result = typer.analyze()
    return result
