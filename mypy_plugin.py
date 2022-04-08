from mypy.plugin import Plugin
from mypy.typeanal import AnalyzeTypeContext, TypeAnalyzerPluginInterface


list_name = "statipy.runtime.annotations.LenList"
set_name = "statipy.runtime.annotations.LenSet"
dict_name = "statipy.runtime.annotations.LenDict"
str_name = "statipy.runtime.annotations.LenStr"


def list_hook(ctx: AnalyzeTypeContext):
    elt, length = ctx.type.args
    elt = ctx.api.analyze_type(elt)
    return ctx.api.named_type("builtins.list", [elt])


def set_hook(ctx: AnalyzeTypeContext):
    elt, length = ctx.type.args[0]
    elt = ctx.api.analyze_type(elt)
    return ctx.api.named_type("builtins.set", [elt])


def dict_hook(ctx: AnalyzeTypeContext):
    key, value, length = ctx.type.args
    key = ctx.api.analyze_type(key)
    value = ctx.api.analyze_type(value)
    return ctx.api.named_type("builtins.set", [key, value])


def str_hook(ctx: AnalyzeTypeContext):
    return ctx.api.named_type("builtins.str")


class StatipyPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str):
        if fullname == list_name:
            return list_hook
        elif fullname == set_name:
            return set_hook
        elif fullname == dict_name:
            return dict_hook
        elif fullname == str_name:
            return str_hook


def plugin(version: str):
    return StatipyPlugin
