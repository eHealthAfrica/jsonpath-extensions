import pytest

from eha_jsonpath import parse
from eha_jsonpath.ext_functions import BaseFn

src = {
    'space': '1 2 3 4',
    'pipe': '1|2|3|4',
    'comma': '1,2,3,4',
    'float': '1.04',
    'bad_float': '1.04s',
    'int': '1.09',
    'str': 1.0,
    'str2': 'a',
    'boolean0': '0',
    'boolean1': 0,
    'boolean2': 1,
    'boolean3': True,
    'dt1': '2019-01-01',
    'dt2': '1.4.2020 11:13',
    'bad_json': '"{!}',
    'hashable1': [1, 2, 3, 4],
    'hashable2': [1, 3, 2, 4],
    'hashable3': {"a": 1, "b": 2},
    'hashable4': {"b": 2, "a": 1},
    'hashable5': ['a', 'b', 'c', 'd'],
    'null': None
}

easy_dictionary = {
    'a': 1,
    'b': 'B',
    'c': {'an', 'object'},
    'd': ['a', 'list']
}

hard_dictionary = {
    'a': '()',  # regex tricker!
    'b': 'null',
    'c': '',
    'd': None
}


@pytest.mark.parametrize("cmd,expect,raises", [
    ('$.space.`len`',
        [7],
        False),  # upstream function
    ('$.space.`space`',
        [],
        True),  # bad name
    ('$.null.`splitlist( , string)`',
        [],
        False),  # bad args
    ('$.space.`splitlist(,)`',
        [],
        True),  # bad args
    ('$.space.`splitlist( , int)`',
        [1, 2, 3, 4],
        False),
    ('$.pipe.`splitlist(|, boolean)`',
        [True, True, True, True],
        False),
    ('$.comma.`splitlist(,, float)`',
        [1.0, 2.0, 3.0, 4.0],
        False),
    ('$.bad_float.`cast(float)`',
        ['1.04s'],
        False),
    ('$.float.`cast(float)`',
        [1.04],
        False),
    ('$.int.`cast(int)`',
        [1],
        False),
    ('$.str.`cast(string)`',
        ['1.0'],
        False),
    ('$.boolean0.`cast(boolean)`',
        [True],
        False),
    ('$.boolean1.`cast(boolean)`',
        [False],
        False),
    ('$.boolean0.`cast(json)`',
        [0],
        False),
    ('$.bad_json.`cast(json)`',
        ['"{!}'],
        False),
    ('$.boolean0.`notmatch(other, 0)`',
        [None],
        False),
    ('$.boolean0.`match(1, null)`',
        [False],
        False),
    ('$.boolean0.`match(0, null)`',
        [True],
        False),
    ('$.boolean0.`notmatch(1, null)`',
        [True],
        False),
    ('$.boolean0.`notmatch(0, null)`',
        [False],
        False),
    ('$.boolean1.`match(2, 0)`',
        [None],
        False),
    ('$.boolean2.`match(1, 0)`',
        [True],
        False),
    ('$.dt1.`datetime(%Y-%m-%d, 0:4)`',
        ['2019'],
        False),
    ('$.dt1.`datetime(%Y-%m-%d, 0:4:2)`',
        ['21'],
        False),
    ('$.dt1.`datetime(%Y-%m-%d, ::)`',
        ['2019-01-01T00:00:00'],
        False),
    ('$.dt1.`datetime(%Y-%m-%d, :)`',
        ['2019-01-01T00:00:00'],
        False),
    ('$.dt1.`datetime(%Y-%g-%d, ::)`',
        [None],  # bad timeformat
        False),
    ('$.dt2.`datetime(%d.%m.%Y %H:%M, 0::)`',
        ['2020-04-01T11:13:00'],
        False),
    ('$.bad_float.`valuereplace(1.04s, clean_value)`',
        ['clean_value'],
        False),
    ('$.bad_float.`valuereplace(1.04_missing, clean_value)`',
        ['1.04s'],
        False),
    ('$.hashable1.`valuereplace(1, clean_value)`',
        ['clean_value', 2, 3, 4],
        False),
    ('$.hashable5.`valuereplace(a, clean_value)`',
        ['clean_value', 'b', 'c', 'd'],
        False),
    ('$.boolean3.`valuereplace(True, clean_value)`',
        ['clean_value'],
        False),
    ('$.boolean3.`valuereplace(True, 1)`',
        ['1'],
        False),  # gives you the value as a string, not an int in this case
    ('$.hashable1.`template(this is my value {})`',
        ['this is my value {}'.format(i) for i in src['hashable1']],
        False),
    ('$.null.`template(this is my value {})`',
        ['this is my value null'],
        False),
    ('$.boolean3.`template(this is my value {})`',
        ['this is my value true'],
        False),
    (f'$.hashable5.`dictionaryreplace({str(easy_dictionary)})`',
        [easy_dictionary[i] for i in src.get('hashable5')],
        False),
    (f'$.hashable5.`dictionaryreplace({str(hard_dictionary)})`',
        [hard_dictionary[i] for i in src.get('hashable5')],
        False),
    (f'$.hashable5.`dictionaryreplace({str({})}BAD)`',
        [],
        True),
    (f'$.str2.`dictionaryreplace({str(easy_dictionary)})`',
        [easy_dictionary[src.get('str2')]],
        False),
])
def test_extensions(cmd, expect, raises):
    if raises:
        with pytest.raises(Exception):
            m = parse(cmd).find(src)
    else:
        m = parse(cmd).find(src)
        res = [i.value for i in m]
        assert (expect == res), f'{expect} != {res}'


def test_comparators():
    a = BaseFn()
    b = BaseFn()
    a.method, b.method = 'm', 'm'
    assert(a == b)
    assert(str(a) == str(b))
    assert(str(a.__repr__()) == str(b.__repr__()))


@pytest.mark.parametrize("cmd1,cmd2", [
    ('$.hashable1.`hash(a)`', '$.hashable2.`hash(a)`'),
    ('$.hashable3.`hash(a)`', '$.hashable4.`hash(a)`'),
])
def test_hashs_equality(cmd1, cmd2):
    parse(cmd1).find(src)[0] == parse(cmd2).find(src)[0]


@pytest.mark.parametrize("cmd1,cmd2", [
    ('$.hashable1.`hash(a)`', '$.hashable2.`hash(b)`'),
    ('$.hashable3.`hash(a)`', '$.hashable4.`hash(b)`'),
])
def test_hashs_inequality(cmd1, cmd2):
    parse(cmd1).find(src)[0] != parse(cmd2).find(src)[0]
