# Worker exit implementation manager verification logs 2

Date: 2026-10-05. Captured by the manager after the correction-1 builder declared STOP-WRITES.
These are command outputs, not reviewer verdicts or implementation acceptance.

## Python 3.11 (3.11.14) focused

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests/contracts -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
.............................................................................................................................................................................
----------------------------------------------------------------------
Ran 173 tests in 0.216s

OK
```

## Python 3.11 (3.11.14) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
....................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 276 tests in 1.574s

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
.............................................................................................................................................................................
----------------------------------------------------------------------
Ran 173 tests in 0.216s

OK
```

## Python 3.12 (3.12.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 0. No warning filter.

```text
....................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 276 tests in 1.622s

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
.............................................................................................................................................................................
----------------------------------------------------------------------
Ran 173 tests in 0.237s

OK
```

## Python 3.13 (3.13.12) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 116. No warning filter.

```text
.................................................................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109960040>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996f4c0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996db70>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996ea70>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996fa60>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109961120>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1099614e0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
......../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:542: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996db70>
  def intent_item(self, item: Tree) -> A.IntentItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109960310>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996db70>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
../Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:175: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1099614e0>
  return A.PathNode(tuple(self.name(t) for t in self.toks(tree) if t.type == "NAME"), self.L(tree))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:175: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1099609a0>
  return A.PathNode(tuple(self.name(t) for t in self.toks(tree) if t.type == "NAME"), self.L(tree))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:175: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10996c7c0>
  return A.PathNode(tuple(self.name(t) for t in self.toks(tree) if t.type == "NAME"), self.L(tree))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
..........................<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993eb60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ca90>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:142: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  return [c for c in tree.children if isinstance(c, Token)]
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c400>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ca90>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c130>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e2f0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e2f0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993eb60>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:59: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  def __init__(self, data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta]=None) -> None:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:157: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993eb60>
  return any(isinstance(c, Token) and c.type == ttype for c in tree.children)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:162: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993eb60>
  if isinstance(c, Token) and c.type == ttype:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:155: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993eb60>
  @staticmethod
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e890>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d4e0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e5c0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ca90>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:387: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c130>
  m = mre.match(text.text, pos, text.end)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c130>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Volumes/projects/limbo/garns-wz/garns/src/garns/parse.py:494: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d4e0>
  def carrier_item(self, item: Tree) -> A.CarrierItem:
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d4e0>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/lexer.py:215: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c400>
  inst = super(Token, cls).__new__(cls, value)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d4e0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993e890>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993c400>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:50: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  res_meta.start_pos = getattr(first_meta, 'container_start_pos', first_meta.start_pos)
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:152: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  filtered = children[i].children
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:64: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d7b0>
  @property
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:2: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993d4e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
................/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/tree.py:30: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10993ff10>
  def __init__(self):
ResourceWarning: Enable tracemalloc to get the object allocation traceback
....................................
----------------------------------------------------------------------
Ran 276 tests in 1.576s

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
.............................................................................................................................................................................
----------------------------------------------------------------------
Ran 173 tests in 0.245s

OK
```

## Python 3.14 (3.14.3) full

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .`

Exit: 0. ResourceWarning lines: 84. No warning filter.

```text
..................................................................................................................................................................................................../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10903ba60>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cc4f0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093ccc70>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cd210>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cd7b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093ce200>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cec50>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c0c70>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c1030>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c14e0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
../Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cf970>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cf5b0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb/lark/parse_tree_builder.py:57: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1093cf3d0>
  last_meta = self._pp_get_meta(reversed(children))
ResourceWarning: Enable tracemalloc to get the object allocation traceback
..........................<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f81c60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f82020>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f826b0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f825c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f82a70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f83010>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f831f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f82f20>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x108f834c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c13f0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c1300>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c1030>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c0f40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c0b80>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c0220>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c1c60>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c1e40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2020>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2110>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c23e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c25c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c27a0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2980>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2a70>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2d40>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c2f20>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c3100>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c32e0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
<string>:3: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x1095c34c0>
ResourceWarning: Enable tracemalloc to get the object allocation traceback
....................................................
----------------------------------------------------------------------
Ran 276 tests in 1.580s

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
