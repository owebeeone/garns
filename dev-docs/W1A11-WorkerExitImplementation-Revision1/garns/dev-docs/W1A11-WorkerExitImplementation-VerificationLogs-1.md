# Worker exit implementation manager verification logs

Date: 2026-10-04. Captured by the manager after builder STOP-WRITES.
These are command outputs, not reviewer verdicts or implementation acceptance.

## Python 3.11 focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. Original output tokens: 58. No warning filter.

```text
..................................................................................................................................
----------------------------------------------------------------------
Ran 130 tests in 0.192s

OK
```

## Python 3.11 full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests -t .`

Exit: 0. Original output tokens: 84. No warning filter.

```text
.........................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 233 tests in 1.947s

OK
```

## Python 3.11 product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B tools/check_product.py`

Exit: 0. Original output tokens: 30. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.12 focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. Original output tokens: 58. No warning filter.

```text
..................................................................................................................................
----------------------------------------------------------------------
Ran 130 tests in 0.197s

OK
```

## Python 3.12 full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests -t .`

Exit: 0. Original output tokens: 84. No warning filter.

```text
.........................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 233 tests in 1.986s

OK
```

## Python 3.12 product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B tools/check_product.py`

Exit: 0. Original output tokens: 30. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.13 focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. Original output tokens: 58. No warning filter.

```text
..................................................................................................................................
----------------------------------------------------------------------
Ran 130 tests in 0.190s

OK
```

## Python 3.13 full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests -t .`

Exit: 0. Original output tokens: 3851. No warning filter.

```text
......................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097745e0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109745b70>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744a90>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747b50>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109774310>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109775120>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:542: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  def intent_item(self, item: Tree) -> A.IntentItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109774040>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109775120>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097745e0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................/opt/homebrew/Cellar/python@3.13/3.13.12_1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/re/_parser.py:260: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  def get(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747c40>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747a60>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097475b0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097471f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747f10>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097476a0>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747970>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747c40>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097471f0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097475b0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097471f0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747e20>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747c40>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097471f0>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/datascad/garns-v9-6/src/garns/parse.py:155: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109744220>
  @staticmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097475b0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747c40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747a60>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747a60>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109747880>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.............../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097475b0>
  if not hasattr(res_meta, 'line'):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:46: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1097467a0>
  if not hasattr(res_meta, 'line'):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.....................................
----------------------------------------------------------------------
Ran 233 tests in 1.862s

OK
```

## Python 3.13 product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B tools/check_product.py`

Exit: 0. Original output tokens: 30. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

## Python 3.14 focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. Original output tokens: 58. No warning filter.

```text
..................................................................................................................................
----------------------------------------------------------------------
Ran 130 tests in 0.186s

OK
```

## Python 3.14 full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .`

Exit: 0. Original output tokens: 3444. No warning filter.

```text
........................................................................................................................................................./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad6200>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad6c50>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad73d0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad7970>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad7f10>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e09a0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e13f0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e33d0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e3790>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e3c40>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b7e3e20>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb78130>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
............................<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ae4d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ade40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ae110>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5adb70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5adc60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad7b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad210>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad030>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5acd60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb78130>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb78a90>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb78c70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb78e50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb79030>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb79300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb794e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb796c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb797b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb79a80>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb79c60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb79e40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a020>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a110>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a3e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a5c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a7a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7a980>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bb7ab60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
................<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad120>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad5d0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad6c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5add50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ad8a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ae2f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ae7a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5aec50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5ae5c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5adf30>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10b5aef20>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad4d60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad53f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad54e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad5030>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad4f40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad5990>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad5d50>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad5f30>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad5e40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad6110>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad67a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad65c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad6e30>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad62f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad6b60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10bad7010>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
....................................
----------------------------------------------------------------------
Ran 233 tests in 1.872s

OK
```

## Python 3.14 product

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B tools/check_product.py`

Exit: 0. Original output tokens: 30. No warning filter.

```text
PASS product paths
PASS pinned baseline inputs
PASS cache hygiene
PASS shipped path hygiene
PASS W0 product baseline
```

