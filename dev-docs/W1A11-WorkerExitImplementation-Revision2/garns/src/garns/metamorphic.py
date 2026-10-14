"""Metamorphic renaming through the resolver's reference map.

``transform`` rewrites every identifier occurrence that the resolver bound to
a semantic identity (modules, intents, aliases, newtypes, closed-set types,
carriers, members, links, inverse names, reads, verbs, tombstones,
capabilities, writer sources, worlds, deployments) with a fresh name, and
re-keys the storage binding with fresh physical names. Compiler code is not
touched; the transformed world must resolve to the same normalized semantics.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from . import ast as A
from . import ir as I
from .storage import binding_document

RENAMED_ROLES = {
    "module", "intent", "intent-alias", "intent-previous", "newtype", "closedtype", "carrier", "member", "link", "inverse",
    "read", "alias", "bulk", "restricted", "compound", "tombstone", "capability", "writer", "world", "deployment",
}
KEYWORDS = set("""module import as intent alias renamed_from values pattern length dimension newtype of optional list_of trait resource event association family member use key filter order stamp on_mint on_change default repair link end restrict cascade detach unenforced scopes inverse lifecycle mutable retirable archived_by carry ordered_within history kept breaking tighten invariant scope_via query question given where show identity count rank page limit with_total live bounded including_archived unscoped by one group first distinct having last ascending descending bulk over set absent restricted accepts compound step each bind world modules durability writers generated requires exempt scope capabilities writer_source quarantine_retention deployment engine at ship mode snapshot pool env path memory extends tombstone data retype forward backward restore move_home into widen validate quarantine drop ship_clock engine_clock some every not and or contains in is present absent within when max min sum average minimum maximum call true false""".split())


@dataclass
class Transformed:
    sources: dict[str, str]  # file path -> transformed text
    mapping: dict[str, str]  # identity -> fresh local name
    forward: dict[str, str]  # fresh local name -> original spelling (for normalization)
    binding: dict


def fresh_names(program: I.Program, seed: str) -> dict[str, str]:
    """Deterministic fresh local name per renamed identity."""
    identities = sorted({r.identity for r in program.references if r.role in RENAMED_ROLES})
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for identity in identities:
        h = hashlib.sha256(f"{seed}|{identity}".encode()).hexdigest()
        name = "zq" + h[:7]
        while name in used or name in KEYWORDS:
            h = hashlib.sha256(h.encode()).hexdigest()
            name = "zq" + h[:7]
        used.add(name)
        mapping[identity] = name
    return mapping


def rename_sources(files: list[A.SourceFile], program: I.Program, mapping: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """Rewrite identifier occurrences by reference position; returns (texts, fresh->original spellings)."""
    by_file: dict[str, list[I.Reference]] = {}
    for r in program.references:
        if r.role in RENAMED_ROLES and r.identity in mapping:
            by_file.setdefault(r.file, []).append(r)
    texts: dict[str, str] = {}
    forward: dict[str, str] = {}
    for sf in files:
        lines = sf.text.split("\n")
        refs = sorted(by_file.get(sf.path, []), key=lambda r: (r.line, -r.column))
        seen: set[tuple[int, int]] = set()
        for r in refs:
            if (r.line, r.column) in seen:
                continue
            seen.add((r.line, r.column))
            line = lines[r.line - 1]
            start = r.column - 1
            if line[start : start + len(r.text)] != r.text:
                raise AssertionError(f"reference map mismatch at {sf.path}:{r.line}:{r.column}: expected {r.text!r}")
            new = mapping[r.identity]
            forward[new] = r.text  # fresh -> original spelling (unique per fresh name)
            lines[r.line - 1] = line[:start] + new + line[start + len(r.text) :]
        texts[sf.path] = "\n".join(lines)
    return texts, forward


def physical_scheme(seed: str):
    def names(kind: str, key: str) -> str:
        h = hashlib.sha256(f"{seed}|{kind}|{key}".encode()).hexdigest()[:9]
        return f"px_{h}"

    return names


def transform(files: list[A.SourceFile], program: I.Program, world_name: str, seed: str, program_after) -> Transformed:
    """Rename sources and produce a fresh binding for the renamed world.

    ``program_after`` is a callback resolving the transformed sources so that
    the binding is built from the renamed program (the compiler stays untouched).
    """
    mapping = fresh_names(program, seed)
    texts, forward = rename_sources(files, program, mapping)
    renamed_program = program_after(texts)
    new_world = mapping.get(world_name, world_name)
    binding = binding_document(renamed_program, new_world, physical_scheme(seed))
    return Transformed(texts, mapping, forward, binding)


def normalize(text: str, forward: dict[str, str]) -> str:
    """Map fresh local names back to the original names inside any text."""
    return re.sub(r"\bzq[0-9a-f]{7}\b", lambda m: forward.get(m.group(0), m.group(0)), text)


def _resort(obj):
    """Sort declaration lists by qualified identity so that renaming cannot reorder them."""
    if isinstance(obj, dict):
        return {k: _resort(v) for k, v in obj.items()}
    if isinstance(obj, list):
        items = [_resort(x) for x in obj]
        if items and all(isinstance(x, dict) and ("qid" in x or "name" in x) and "$" in x for x in items):
            kinds = {x["$"] for x in items}
            if kinds <= {"Intent", "Newtype", "Carrier", "Read", "Alias", "Bulk", "Restricted", "Compound", "Tombstone", "World", "Deployment", "Module", "TightenDecl", "RetypeDecl", "RestoreDecl", "MoveHome"}:
                items.sort(key=lambda x: json.dumps(x.get("qid", x.get("name")), sort_keys=True))
        return items
    return obj


def normalized_program_json(program: I.Program, forward: dict[str, str] | None = None) -> str:
    text = I.canonical_json(program)
    if forward:
        text = normalize(text, forward)
    return json.dumps(_resort(json.loads(text)), sort_keys=True, indent=1)


def rename_qualified(program: I.Program, mapping: dict[str, str], key: str) -> str:
    """Map a qualified identity of ``program`` (module, carrier, read, use or link key,
    or world#capability) to its fresh spelling, resolving each segment against the
    original program so that shared local spellings never collide."""
    if "#capability:" in key:
        return mapping.get(key, key.split(":", 1)[1])
    parts = key.split(".")
    if len(parts) == 1:
        return mapping.get(key, key)
    module = parts[0]
    out = [mapping.get(module, module)]
    if len(parts) == 2:
        return ".".join(out + [mapping.get(key, parts[1])])
    carrier_qid = f"{parts[0]}.{parts[1]}"
    out.append(mapping.get(carrier_qid, parts[1]))
    carrier = program.carrier(carrier_qid)
    local = parts[2]
    use = carrier.use_named(local)
    if use is not None:
        return ".".join(out + [mapping.get(use.intent, local)])
    link = carrier.link_named(local)
    if link is not None:
        declared = link.qid if link.origin == "own" else f"{link.origin}.{link.name}"
        return ".".join(out + [mapping.get(declared, local)])
    return ".".join(out + [mapping.get(key, local)])
