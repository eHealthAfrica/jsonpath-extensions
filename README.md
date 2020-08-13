# jsonpath-extensions


Provides new [Extensions to the jsonpath_ng python library](https://github.com/h2non/jsonpath-ng#extensions) to provide commonly requested functions.  The context for these functions is always the value provided from the resolution of the provided jsonpath. The functions will all handle lists or single values as inputs unless explicitly marked. If you're confused about a function's intended, behavior take a look at [the tests](https://github.com/eHealthAfrica/jsonpath-extensions/blob/master/test/test.py).

## Usage

```python
from eha_jsonpath import parse
# The following is pseudocode, don't copy it.
obj = {'my': 'object'}
path = '$.some.jsonpath.`fn(arg1, arg2)`'
matches = parse(path).find(obj)
```

## New Extensions

### Cast

Attempts to apply a cast to the result of a jsonpath expression. 
Will operate invidiually on array items in the case the path resolves to an array.

_usage:_ ```$.my.path.`cast({castType})` ```

supported castTypes and _behavior:_
```python

CASTS = {
    'int': lambda x: _cast_int(x),  # see below
    'boolean': lambda x: bool(x),
    'string': lambda x: str(x),
    'float': lambda x: float(x),
    'json': lambda x: json.loads(x),  # standard json library
    'none': lambda x: x,
    'null': lambda x: None
}


def _cast_int(obj):
    # fixes issues when trying to cast a float str -> int
    # int('1.09') throws ValueError
    try:
        return int(obj)
    except ValueError:
        return int(float(obj))
```

### Split List

Takes a string at a given jsonpath and attempts to split it into an array of given `delimiter` and casts the array items to a specific `castType`. See valid casts in Cast section.

The resolved path _must_ be a string. *Will not* operate invidiually on array items in the case the path resolves to an array.

_usage:_ ```$.my.path.`splitlist({delimiter}, {castType})` ```

    

### Match

Checks the value found at a jsonpath against a provided `match_term`. If the value is not found, returns the `null_value`. Will operate invidiually on array items in the case the path resolves to an array.
 

_usage:_ ```$.my.path.`match({match_term}, {null_value})` ```

*_White space after commas is required!_*

_behavior:_

```python
result = (value == match_term) if value != None else null_value
```    

### Not Match


Provides the inverse of Match. Checks the value found at a jsonpath against a provided `match_term`. If the value is not found, returns the `null_value`. Will operate invidiually on array items in the case the path resolves to an array.

_usage:_ ```$.my.path.`notmatch({match_term}, {null_value})` ```

*_White space after commas is required!_*

_behavior:_

```python
result = (value != match_term) if value != None else null_value
``` 
    

### Parse Datetime

Attempts to parse the iso formatted datetime from a string found at a given jsonpath. Then returns a part or the whole of the parsed datetime as specified by a python array slice.  Will operate invidiually on array items in the case the path resolves to an array. The `strptime_str` format is taken from the [python strptime behavior](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior). The array slice notation used in `return_slice` is uses the standard [slice operator](https://docs.python.org/3/library/functions.html?highlight=slice#slice), with semi-colon delimited arguments like:

```python
def args_to_slice(cls, return_slice, obj):
    defaults = [0, None, None]
    parts = []
    for x, i in enumerate(return_slice.split(':')):
        try:
            parts.append(int(i))
        except ValueError:
            parts.append(defaults[x])
    return obj[slice(*parts)]
```

_usage:_ ```$.my.path.`datetime({strptime_str}, {return_slice})` ```

*_White space after commas is required!_*


### Parse Epoch Timestamp

Attempts to parse the epoch timestamp from a value found at a given jsonpath. Then returns a part or the whole of the parsed datetime as specified by a python array slice.  Will operate invidiually on array items in the case the path resolves to an array. The input units must be indicated as one of:
    
 - `seconds`
 - `millis`
 - `micros`
    

The array slice notation used is the same as in `datetime`.

_usage:_ ```$.my.path.`epoch({units}, {return_slice})` ```

*_White space after commas is required!_*

### Hash

Returns a 128bit, hex formatted MD5 hash of the value of a resolved jsonpath added to a provided `salt`. This is useful for generating a UUID compatable value from a piece of source information along with some unique salt. This allows for a non-UUID foreign key to be reliably converted to the same UUID compatable value every time. Will operate invidiually on array items in the case the path resolves to an array.

_usage:_ ```$.my.path.`hash({salt})` ```
    

### Template

Will substitue the value found at a resolved jsonpath into a formatted string with a singe replacement place holder. Will operate invidiually on array items in the case the path resolves to an array.

_usage:_ 
Using of format resembling: ` my name is {} `

```$.my.path.`template({template_format)` ```
    

### Value Replace

Replaces resolved values matching `match_value` with `replacement_value`. Will operate invidiually on array items in the case the path resolves to an array.

_usage:_ ```$.my.path.`valuereplace({match_value}, {replacement_value})` ```

*_White space after commas is required!_*

_behavior:_ 
```python
replacement_value if (match_value == value) else value
```
    

### Dictionary Replace

Replaces resolved values matching a key in a passed dictionary with the appropriate value from the same dictionary. Will operate invidiually on array items in the case the path resolves to an array. The dictionary argument should be a stringified python dictionary.

_usage:_ ```$.my.path.`dictionaryreplace({stringified_python_dictionary})` ```
result is: path value replaces with value of matching key in dictionary

_behavior:_
```python
return passed_dict.get(value, None)

```
    