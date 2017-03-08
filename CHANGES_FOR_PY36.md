odespy/__init__.py
    enable absolute imports , print function
    use explicit relative imports
    try statement around line that deletes variables from locals

odespy/solvers.py
    enable absolute imports , print function
    replace all print statements with print function
    Replaced many "ValueError, msg" to "ValueError(msg)"
    Mixed spaces and tabs: lines 933-937, 962-967, 1508
    TypeError, msg to TypeError(msg): 1162
    ImportError, msg to ImportError(msg): 2014, 2944
    except Exception as e: 2993
    "not_valid is not defined error" at 2909
        apparently in Python 3 list comprehensions like this in class 
        body can't access variables defined in class body. This works in py2.7.
        Replaced list comprehension with for loop.
    in function _format_parameters_table: line 480, convert parameter_names 
        into list. dict.keys() in PY3 returns dict_list object not list.

odespy/RungeKutta.py
    enable absolute imports , print function
    replace all print statements with print function
    Replaced many "ValueError, msg" to "ValueError(msg)"

odespy/rkc.py
    enable absolute imports , print function
    Replaced a few "ValueError, msg" to "ValueError(msg)"

odespy/rkc.py
    enable absolute imports , print function
    replace all print statements with print function

odespy/odepack.py
    enable absolute imports , print function
    Replaced a few "ValueError, msg" to "ValueError(msg)"
    replace all print statements with print function
    mixed tabs and space: 1203, 1232, 1235, 1343, 1456, 1574
    explicit relative import of _odepack.

odespy/radau5.py
    enable absolute imports , print function
    print function
    tab/space: 283

odespy/problems.py
    enable absolute imports , print function
    print function

odespy/tests/test_basic.py
    enable absolute imports , print function
    may places (example line 89, 90): the lambda syntax is invalid in PY3.6
