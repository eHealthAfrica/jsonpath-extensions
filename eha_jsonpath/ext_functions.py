from datetime import datetime
from hashlib import md5
import json
import re
from jsonpath_ng.jsonpath import (
    This,
    DatumInContext
)


class DefintionInvalid(Exception):
    pass


def _cast_int(obj):
    # fixes issues when trying to cast a float str -> int
    # int('1.09') throws ValueError
    try:
        return int(obj)
    except ValueError:
        return int(float(obj))


TYPE_COERCIONS = {
    'int': lambda x: _cast_int(x),
    'boolean': lambda x: bool(x),
    'string': lambda x: str(x),
    'float': lambda x: float(x),
    'json': lambda x: json.loads(x),
    'none': lambda x: x,
    'null': lambda x: None
}


def cast(obj, _type):
    fn = TYPE_COERCIONS.get(_type, TYPE_COERCIONS['none'])
    try:
        value = fn(obj)
        return value
    except Exception:
        return obj


class BaseFn(This):

    METHOD_SIG = re.compile(r'')

    def get_args(self, method):
        m = self.METHOD_SIG.match(method)
        if m is None:
            raise DefintionInvalid(f'{method} is invalid for {self.METHOD_SIG}')
        return [i for i in m.groups()]

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.method == other.method)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.method)

    def __str__(self):
        return '`%s`' % self.method


class SplitList(BaseFn):
    '''
        usage: `splitlist({delimiter}, {castType})`
        ! White space after commas is required!
    '''
    METHOD_SIG = re.compile(r'splitlist\((.),\s+(.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.term = args[0]
        self.cast = args[1]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value.split(self.term)
        return [DatumInContext.wrap(cast(i, self.cast)) for i in value]


class Cast(BaseFn):
    '''
        usage: `cast({castType})`
    '''
    METHOD_SIG = re.compile(r'cast\((.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.cast = args[0]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value
        return [DatumInContext.wrap(cast(value, self.cast))]


class Match(BaseFn):
    '''
        usage: `match({match_term}, {null_value})`
        ! White space after commas is required!
        result is : True, False or None
    '''
    METHOD_SIG = re.compile(r'match\((.+),\s+(.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.term = args[0]
        self.null = args[1]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value
        if str(value) == self.null:
            value = None
        else:
            value = (str(value) == self.term)
        return [DatumInContext.wrap(value)]


class NotMatch(BaseFn):
    '''
        usage: `notmatch({match_term}, {null_value})`
        ! White space after commas is required!
        result is : True, False or None
    '''
    METHOD_SIG = re.compile(r'notmatch\((.+),\s+(.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.term = args[0]
        self.null = args[1]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value
        if str(value) == str(self.null):
            value = None
        else:
            value = (str(value) != self.term)
        return [DatumInContext.wrap(value)]


class ParseDatetime(BaseFn):
    '''
        usage: `datetime({strptime_str}, {return_slice})`
        ! White space after commas is required!
        result is : iso_datetime[return_slice]
    '''
    METHOD_SIG = re.compile(r'datetime\((.+),\s+(.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.time_str = args[0]
        self.slice_arg = args[1]
        self.method = method

    @classmethod
    def args_to_slice(cls, slice_arg, obj):
        defaults = [0, None, None]
        parts = []
        for x, i in enumerate(slice_arg.split(':')):
            try:
                parts.append(int(i))
            except ValueError:
                parts.append(defaults[x])
        return obj[slice(*parts)]

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        try:
            try:
                value = datetime.strptime(datum.value, self.time_str)
            except ValueError as ver:
                raise DefintionInvalid(
                    f'Bad time_format {self.time_str} -> {ver}')
            value = ParseDatetime.args_to_slice(
                self.slice_arg, value.isoformat())
        except Exception:
            return []
        return [DatumInContext.wrap(value)]


class Hash(BaseFn):
    '''
        usage: `hash({salt})`
    '''
    METHOD_SIG = re.compile(r'hash\((.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.salt = args[0]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = self._hash(self.salt, datum.value)
        return [DatumInContext.wrap(value)]

    def _hash(self, salt, obj):
        sorted_msg = json.dumps(obj, sort_keys=True)
        encoded_msg = (salt + sorted_msg).encode('utf-8')
        hash = str(md5(encoded_msg).hexdigest())[:32]  # 128bit hash
        return hash


class Template(BaseFn):
    '''
        usage: `template({template_format{}})`
        result is : value substited into template
    '''
    METHOD_SIG = re.compile(r'template\(([^,;]+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.template_format = args[0]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value
        value = self.template_format.format(json.dumps(datum.value))
        return [DatumInContext.wrap(value)]


class ValueReplace(BaseFn):
    '''
        usage: `valuereplace({match_value}, {replacement_value})`
        ! White space after commas is required!
        result is : {replacement_value} if (match_value == value) else None
    '''
    METHOD_SIG = re.compile(r'valuereplace\((.+),\s+(.+)\)')

    def __init__(self, method=None):
        args = self.get_args(method)
        self.match_value = args[0]
        self.replacement = args[1]
        self.method = method

    def find(self, datum):
        datum = DatumInContext.wrap(datum)
        value = datum.value
        if str(value) != self.match_value:
            return []
        else:
            return [DatumInContext.wrap(self.replacement)]
