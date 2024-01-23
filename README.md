# sigmatch: check function signatures

[![Downloads](https://static.pepy.tech/badge/sigmatch/month)](https://pepy.tech/project/sigmatch)
[![Downloads](https://static.pepy.tech/badge/sigmatch)](https://pepy.tech/project/sigmatch)
[![codecov](https://codecov.io/gh/pomponchik/sigmatch/graph/badge.svg?token=WLyJpBfzpf)](https://codecov.io/gh/pomponchik/sigmatch)
[![Lines of code](https://sloc.xyz/github/pomponchik/sigmatch/?category=code)](https://github.com/boyter/scc/)
[![Hits-of-Code](https://hitsofcode.com/github/pomponchik/sigmatch?branch=main)](https://hitsofcode.com/github/pomponchik/sigmatch/view?branch=main)
[![Test-Package](https://github.com/pomponchik/sigmatch/actions/workflows/tests_and_coverage.yml/badge.svg)](https://github.com/pomponchik/sigmatch/actions/workflows/tests_and_coverage.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/sigmatch.svg)](https://pypi.python.org/pypi/sigmatch)
[![PyPI version](https://badge.fury.io/py/sigmatch.svg)](https://badge.fury.io/py/sigmatch)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


This small library allows you to quickly check whether any called object matches the signature you expect. This may be useful to you, for example, if you write libraries that work with callbacks.

Install it:

```bash
pip install sigmatch
```

To check the signatures of the callable objects, you need to create a `SignatureMatcher` object, which will "bake" a description of the parameters you expect. You can pass the following arguments to the constructor of the `SignatureMatcher` class (they are all strings):

- '.' - corresponds to an ordinary positional argument without a default value.
- 'some_argument_name' - corresponds to an argument with a default value. The content of the string is the name of the argument.
- '*' - corresponds to packing multiple positional arguments without default values (*args).
- '**' - corresponds to packing several named arguments with default values (**kwargs).

When you have prepared a `SignatureMatcher` object, you can apply it to function objects and get a response (`True`/`False`) whether their signatures match the expected ones. As an example, see what a function and a `SignatureMatcher` object for it mights look like:

```python
from sigmatch import SignatureMatcher

def function(a, b, c=5, *d, **e):
    ...

matcher = SignatureMatcher('.', '.', 'c', '*', '**')
print(matcher.match(function))  # True
```
