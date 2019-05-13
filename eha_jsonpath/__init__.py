from jsonpath_ng.ext.parser import ExtentedJsonPathParser

from . import ext_functions as fn


# You must use this parser instead of the normal or ext one.
class JsonPathParser(ExtentedJsonPathParser):
    "Aether extension of jsonpath_ng extensions..."
    # register all exposed functions in this method
    def p_jsonpath_named_operator(self, p):
        "jsonpath : NAMED_OPERATOR"
        if p[1].startswith("splitlist("):
            p[0] = fn.SplitList(p[1])
        elif p[1].startswith("cast("):
            p[0] = fn.Cast(p[1])
        elif p[1].startswith("match("):
            p[0] = fn.Match(p[1])
        elif p[1].startswith("notmatch("):
            p[0] = fn.NotMatch(p[1])
        elif p[1].startswith("datetime("):
            p[0] = fn.ParseDatetime(p[1])
        elif p[1].startswith("hash("):
            p[0] = fn.Hash(p[1])
        elif p[1].startswith("valuereplace("):
            p[0] = fn.ValueReplace(p[1])
        elif p[1].startswith("template("):
            p[0] = fn.Template(p[1])
        else:
            super(JsonPathParser, self).p_jsonpath_named_operator(p)


def parse(path, debug=False):
    return JsonPathParser(debug=debug).parse(path)
