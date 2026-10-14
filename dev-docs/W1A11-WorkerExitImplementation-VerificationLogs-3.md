# Worker exit implementation manager verification logs 3

Date: 2026-10-05. Captured by the manager after the correction-2 builder declared STOP-WRITES.
These are command outputs, not reviewer verdicts or implementation acceptance.

## Python 3.11 (3.11.14) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
...........................................................................................................................................................................................
----------------------------------------------------------------------
Ran 187 tests in 0.254s

OK
```

## Python 3.11 (3.11.14) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
..................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 290 tests in 1.612s

OK
```

## Python 3.11 (3.11.14) product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B tools/check_product.py`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.12 (3.12.12) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
...........................................................................................................................................................................................
----------------------------------------------------------------------
Ran 187 tests in 0.246s

OK
```

## Python 3.12 (3.12.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
..................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 290 tests in 1.664s

OK
```

## Python 3.12 (3.12.12) product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B tools/check_product.py`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.13 (3.13.12) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
...........................................................................................................................................................................................
----------------------------------------------------------------------
Ran 187 tests in 0.274s

OK
```

## Python 3.13 (3.13.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 114. No warning filter.

```text
................................................................................................................................................................................................./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cc220>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725bb50>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725a2f0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725b010>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725b5b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cd7b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cc6d0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:542: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725a2f0>
  def intent_item(self, item: Tree) -> A.IntentItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cc9a0>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725a2f0>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cc6d0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072cda80>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10725b970>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
..........................<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4040>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a75b0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4310>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a75b0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a44f0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4040>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a5c60>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a5c60>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a5c60>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:155: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a5c60>
  @staticmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a5c60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a63e0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4040>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a75b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:494: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a63e0>
  def carrier_item(self, item: Tree) -> A.CarrierItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a63e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a63e0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a67a0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a4a90>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a75b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................................../opt/homebrew/Cellar/python@3.13/3.13.12_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/json/encoder.py:263: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a6d40>
  return _iterencode(o, 0)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/opt/homebrew/Cellar/python@3.13/3.13.12_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/json/encoder.py:263: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1072a47c0>
  return _iterencode(o, 0)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......
----------------------------------------------------------------------
Ran 290 tests in 1.605s

OK
```

## Python 3.13 (3.13.12) product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B tools/check_product.py`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.14 (3.14.3) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
...........................................................................................................................................................................................
----------------------------------------------------------------------
Ran 187 tests in 0.283s

OK
```

## Python 3.14 (3.14.3) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 140. No warning filter.

```text
................................................................................................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f113f0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f11e40>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f125c0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f12b60>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f13100>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109f13b50>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c285e0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2a5c0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2a980>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2ae30>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2b010>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2b2e0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29b70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29210>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28d60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28c70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28a90>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c287c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c285e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28400>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28220>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28040>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2bc40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2be20>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a0040>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a0220>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a04f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a06d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a08b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a09a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a0c70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a0e50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1030>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1210>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a15d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a17b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1990>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1b70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a3a1d50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28130>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28310>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c284f0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c285e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c289a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c288b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c28d60>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29210>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29300>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c29a80>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2a200>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2a890>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2aa70>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2a980>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2af20>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2ae30>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2b2e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109c2b5b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b985e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b984f0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b987c0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b989a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b98c70>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b98f40>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b98d60>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b995d0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b99030>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b99120>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b99990>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......................................
----------------------------------------------------------------------
Ran 290 tests in 1.616s

OK
```

## Python 3.14 (3.14.3) product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B tools/check_product.py`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```
