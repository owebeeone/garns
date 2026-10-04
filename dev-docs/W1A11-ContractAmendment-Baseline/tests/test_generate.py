"""Deterministic generation and delete/regenerate byte identity.

Generation is run into fresh temporary directories only; the committed
``generated/`` tree is read for comparison and never written.
"""

from __future__ import annotations

import json
import shutil
import unittest

from tests.support import BUILD, GENERATED, GarnsTestCase, discovered_worlds, world_ir

from garns.generate import generate, tree_digest
from garns.parse import garns_files, parse_paths
from garns.resolve import resolve_files
from garns.storage import bind_world

# The evolution generations share one world name and are migrated rather than
# generated; the committed tree holds one directory per distinct world.
COMMITTED_WORLDS = [(name, rel) for name, rel in discovered_worlds() if "evolution" not in rel]


class TestDeterminism(GarnsTestCase):
    def test_two_generations_into_fresh_directories_are_byte_identical(self) -> None:
        tmp = self.tempdir()
        for name, rel in COMMITTED_WORLDS:
            with self.subTest(world=name):
                world = world_ir(name, rel)
                generate(world, tmp / f"{name}-a")
                generate(world, tmp / f"{name}-b")
                self.assertEqual(tree_digest(tmp / f"{name}-a"), tree_digest(tmp / f"{name}-b"))

    def test_regeneration_over_an_existing_directory_replaces_it_exactly(self) -> None:
        tmp = self.tempdir()
        world = world_ir(*COMMITTED_WORLDS[0])
        generate(world, tmp / "out")
        (tmp / "out" / "stale.txt").write_text("left over", encoding="utf-8")
        digest_with_junk = tree_digest(tmp / "out")
        generate(world, tmp / "out")
        self.assertNotEqual(digest_with_junk, tree_digest(tmp / "out"))
        self.assertFalse((tmp / "out" / "stale.txt").exists())

    def test_every_generated_file_is_listed_with_its_digest_in_the_manifest(self) -> None:
        tmp = self.tempdir()
        world = world_ir(*COMMITTED_WORLDS[0])
        files = generate(world, tmp / "out")
        manifest = json.loads((tmp / "out" / "manifest.json").read_text(encoding="utf-8"))
        on_disk = {p.relative_to(tmp / "out").as_posix() for p in (tmp / "out").rglob("*") if p.is_file()}
        self.assertEqual(on_disk, set(files))
        self.assertEqual(set(manifest["files"]), on_disk - {"manifest.json"})


class TestCommittedTree(GarnsTestCase):
    def test_the_committed_tree_holds_one_directory_per_world(self) -> None:
        committed = {p.name for p in GENERATED.iterdir() if p.is_dir()}
        self.assertEqual({name for name, _ in COMMITTED_WORLDS}, committed)

    def test_delete_and_regenerate_reproduces_the_committed_tree_byte_for_byte(self) -> None:
        tmp = self.tempdir()
        differing = []
        for name, rel in COMMITTED_WORLDS:
            generate(world_ir(name, rel), tmp / name)
            if tree_digest(GENERATED / name) != tree_digest(tmp / name):
                differing.append(name)
        self.assertEqual([], differing)

    def test_regeneration_from_a_relocated_copy_of_the_corpus_is_byte_identical(self) -> None:
        """A reviewer checks the tree out somewhere else; the bytes must not move."""
        tmp = self.tempdir()
        differing: list[str] = []
        for name, rel in COMMITTED_WORLDS:
            source = tmp / "corpus-copy" / name
            shutil.copytree(BUILD / rel, source)
            program = resolve_files(parse_paths(garns_files(source)))
            world = bind_world(program, name, source / f"storage-{name}.json")
            out = tmp / f"relocated-{name}"
            generate(world, out)
            committed = GENERATED / name
            if tree_digest(committed) == tree_digest(out):
                continue
            for produced in sorted(x for x in out.rglob("*") if x.is_file()):
                rel_name = produced.relative_to(out).as_posix()
                twin = committed / rel_name
                if not twin.exists() or twin.read_bytes() != produced.read_bytes():
                    differing.append(f"{name}/{rel_name}")
        self.assertEqual(
            [], differing,
            "regenerating from a copy of the corpus at another path changes these artifacts; the "
            "generated IR carries the storage binding path it was built from",
        )


if __name__ == "__main__":
    unittest.main()
