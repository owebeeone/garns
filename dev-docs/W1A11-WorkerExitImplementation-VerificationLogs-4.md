# Worker exit implementation manager verification logs 4

Date: 2026-10-05. Captured by the manager after the correction-3 builder declared STOP-WRITES.
These are command outputs, not reviewer verdicts or implementation acceptance.

## Python 3.11 (3.11.14) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
..............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 190 tests in 0.263s

OK
```

## Python 3.11 (3.11.14) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
.....................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 293 tests in 1.667s

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
..............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 190 tests in 0.256s

OK
```

## Python 3.12 (3.12.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
.....................................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 293 tests in 1.704s

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
..............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 190 tests in 0.282s

OK
```

## Python 3.13 (3.13.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 116. No warning filter.

```text
..................................................................................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59c6d0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59e6b0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59e7a0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59f5b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59c220>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59fb50>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59d7b0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:542: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59e7a0>
  def intent_item(self, item: Tree) -> A.IntentItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59c130>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59c6d0>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59d7b0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59d5d0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b59c6d0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
..........................<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57cb80>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57d8a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c5e0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c5e0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57cb80>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c8b0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57d8a0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57d8a0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c8b0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57d8a0>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:155: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  @staticmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b53d300>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c8b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57d8a0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c5e0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:494: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c5e0>
  def carrier_item(self, item: Tree) -> A.CarrierItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c8b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c8b0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b53d300>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c040>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57de40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................................../opt/homebrew/Cellar/python@3.13/3.13.12_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/json/encoder.py:263: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57cb80>
  return _iterencode(o, 0)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/opt/homebrew/Cellar/python@3.13/3.13.12_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/json/encoder.py:263: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b57c220>
  return _iterencode(o, 0)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......
----------------------------------------------------------------------
Ran 293 tests in 1.636s

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
..............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 190 tests in 0.295s

OK
```

## Python 3.14 (3.14.3) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 140. No warning filter.

```text
...................................................................................................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d8a0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20e2f0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20ea70>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20f010>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20f5b0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a074040>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a074a90>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a076a70>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a076e30>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a0772e0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a0774c0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a077790>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71d50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71990>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b714e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b717b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71210>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b70e50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b708b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b706d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b709a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b70400>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a670130>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a670310>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6704f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6706d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6709a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a670b80>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a670d60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a670e50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a671120>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a671300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6714e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6716c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a6717b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a671a80>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a671c60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a671e40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a672020>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a672200>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b708b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b70e50>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71300>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b713f0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b717b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b714e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71b70>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b71d50>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b723e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b715d0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b725c0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109b72020>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20c9a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20ca90>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20cb80>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20c5e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d030>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20cf40>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d3f0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d5d0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d7b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20db70>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20dc60>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20de40>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20e5c0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20e200>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20d990>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20e110>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a20e7a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......................................
----------------------------------------------------------------------
Ran 293 tests in 1.720s

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
