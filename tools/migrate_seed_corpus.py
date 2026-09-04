#!/usr/bin/env python3
"""Migrate the v9-4 non-numbered corpora into v9-5 worlds.

Every edit is a v9-5 language consequence, listed in corpus/worlds/MIGRATION.md.
Run from build/B2: ``python tools/migrate_seed_corpus.py``.
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parents[1]
SEED = HERE.parents[1] / "seed" / "v9-4" / "c3-core" / "corpus"
OUT = HERE / "corpus" / "worlds"

# (world dir, file, old, new, reason)
EDITS: list[tuple[str, str, str, str, str]] = []


def edit(world: str, file: str, old: str, new: str, reason: str) -> None:
    EDITS.append((world, file, old, new, reason))


def to_query(world: str, file: str, name: str) -> None:
    edit(world, file, f"question {name} of", f"query {name} of", "one-shot read without a live bound is a static query in v9-5")


def bound(world: str, file: str, name: str, n: int) -> None:
    EDITS.append((world, file, f"@bound:{name}", str(n), "dynamic-only algebra (some/every, count, composition) stays a question and states its live bound"))


# practice
for q in ("contacts_named_like", "contacts_with_relationship", "all_clients_for_audit"):
    to_query("practice", "clients.garns", q)
for q in ("client_documents", "letters_mentioning"):
    to_query("practice", "documents.garns", q)
edit("practice", "labels.garns", "where some labels.label_name = \"vip\"", "where some labels.label.label_name = \"vip\"",
     "paths traverse resolved link edges only: the inverse `labels` reaches ClientLabel, whose `label` link reaches Label.label_name")
bound("practice", "labels.garns", "vip_clients", 1000)
bound("practice", "labels.garns", "vip_contacts", 1000)
for q in ("client_card", "notes_in_window"):
    to_query("practice", "notes.garns", q)
bound("practice", "notes.garns", "dormant_clients", 1000)
edit("practice", "world.garns", "generated python, rust, typescript", "generated python, rust", "this build generates python and rust surfaces; an unsupported target refuses")
edit("practice", "deployments.garns", "  engine postgres\n", "  engine sqlite\n",
     "postgres is recognised but has no lowering in this build; a deployment using it refuses ENGINE_LOWERING_ABSENT at validate (R1 P2.4 repair), so PROD (and AUDIT, which extends it) run on sqlite")
# evolution
for g in ("g4", "g5"):
    edit(f"evolution/{g}", "world.garns", "generated python, rust, typescript", "generated python, rust", "this build generates python and rust surfaces; an unsupported target refuses")
    edit(f"evolution/{g}", "clients.garns", "    use email\n    link client -> Client", "    use email\n    use archived_at { optional }\n    link client -> Client",
         "archived_by names a declared optional Instant use; the seed omitted the use on Contact")
# everbility
for q in ("aget_personal_clients", "aget_client_by_clerk_user_id", "check_org_client", "adelete_client_by_id", "org_pms_user_maps",
          "adapters_by_status", "tags_for_property", "db_get_available_pms_adapters", "celery_get_org_user_db"):
    to_query("everbility", "heldout.garns", q)
# vaultwarden
edit("vaultwarden", "world.garns", "modules traits, people, vault, orgs, auth, events, heldout", "modules traits, people, vault, orgs, auth, events",
     "the seed ships no heldout module; a listed module must be declared (MODULE_UNKNOWN)")
for q in ("events_for_user", "events_for_org"):
    to_query("vaultwarden", "events.garns", q)
to_query("vaultwarden", "orgs.garns", "org_collections")
for q in ("unexpired_sends", "opaque_present"):
    to_query("vaultwarden", "vault.garns", q)
edit("vaultwarden", "auth.garns", "  intent grantor : Text \"unused; grantor is a link\"\n", "", "an intent used by no carrier refuses (INTENT_HOMELESS)")
edit("vaultwarden", "events.garns", "  intent act_user : Text \"unused; acting user is a link\"\n", "", "an intent used by no carrier refuses (INTENT_HOMELESS)")
# appflowy
edit("appflowy", "world.garns", "modules traits, workspaces, chat, uploads, collab, ai, migrate, heldout_dml", "modules traits, workspaces, chat, uploads, collab, ai, migrate",
     "the seed ships no heldout_dml module; a listed module must be declared (MODULE_UNKNOWN)")
edit("appflowy", "world.garns", "modules embeddings, heldout_vec", "modules embeddings",
     "the seed ships no heldout_vec module; a listed module must be declared (MODULE_UNKNOWN)")
edit("appflowy", "embeddings.garns", "link workspace -> Workspace { unenforced scopes inverse embeddings }", "link workspace -> Workspace { unenforced scopes }",
     "an inverse declared on a trait link composes into every carrier of the trait and is ambiguous on the target (INVERSE_DUPLICATED)")


def apply_bound(text: str, name: str, n: int) -> str:
    pattern = re.compile(rf"(question {name} of [^\n]*\{{\n)(.*?)(\n  \}})", re.S)
    m = pattern.search(text)
    if m is None:
        raise SystemExit(f"question {name} not found")
    return text[: m.start()] + m.group(1) + m.group(2) + f"\n    live bounded {n}" + m.group(3) + text[m.end():]


def main() -> None:
    # rewrite only the migrated sources and the log; storage bindings alongside them are authored inputs
    if OUT.exists():
        for stale in list(OUT.rglob("*.garns")) + [OUT / "MIGRATION.md"]:
            if stale.exists():
                stale.unlink()
    worlds = ["practice", "everbility", "vaultwarden", "appflowy", "evolution/g1", "evolution/g2", "evolution/g3", "evolution/g4", "evolution/g5"]
    for world in worlds:
        src = SEED / world
        dst = OUT / world
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.garns")):
            shutil.copy(f, dst / f.name)
    log: list[str] = ["# Seed corpus migration log", "", "Each edit is a consequence of the frozen v9-5 language; the seed is otherwise copied byte-for-byte.", ""]
    for world, file, old, new, reason in EDITS:
        path = OUT / world / file
        text = path.read_text(encoding="utf-8")
        if old.startswith("@bound:"):
            name = old.split(":", 1)[1]
            text = apply_bound(text, name, int(new))
            log.append(f"- `{world}/{file}`: question `{name}` gains `live bounded {new}` — {reason}")
        else:
            if old not in text:
                raise SystemExit(f"edit target not found in {path}: {old!r}")
            text = text.replace(old, new, 1)
            log.append(f"- `{world}/{file}`: `{old.strip()}` -> `{new.strip() or '(removed)'}` — {reason}")
        path.write_text(text, encoding="utf-8")
    (OUT / "MIGRATION.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"migrated {len(worlds)} worlds with {len(EDITS)} edits into {OUT}")


if __name__ == "__main__":
    main()
