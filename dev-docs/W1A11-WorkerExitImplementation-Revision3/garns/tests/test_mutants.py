"""Mutant execution: real stages, and detection that does not read the manifest.

``observe_all`` runs every mutant through the production pipeline (and, for
scenarios, through real store states). The expectation manifest is opened only
to assert against those observations, and the invariance test proves it: the
whole corpus is copied with renamed files, stripped comments and a corrupted
manifest, and every outcome is unchanged.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import unittest

from tests.support import CORPUS, GarnsTestCase

from garns.mutants import observe_all

MUTANTS = CORPUS / "mutants"


def expectations() -> dict[str, tuple[str, str]]:
    document = json.loads((MUTANTS / "expected.json").read_text(encoding="utf-8"))
    return {case["mutant"]: (case["stage"], case["code"]) for case in document["cases"]}


class MutantTestCase(GarnsTestCase):
    observed: dict = {}

    @classmethod
    def setUpClass(cls) -> None:
        if not MutantTestCase.observed:
            MutantTestCase.observed = observe_all(MUTANTS)
        cls.results = MutantTestCase.observed


class TestObservedMatchesManifest(MutantTestCase):
    def test_the_manifest_and_the_corpus_describe_the_same_mutants(self) -> None:
        self.assertEqual(sorted(expectations()), sorted(self.results))

    def test_every_mutant_reproduces_its_recorded_stage_and_code(self) -> None:
        expected = expectations()
        mismatches = {name: (obs.stage, obs.code, *expected[name])
                      for name, obs in self.results.items() if (obs.stage, obs.code) != expected[name]}
        self.assertEqual({}, mismatches)

    def test_mutants_execute_decode_validate_ship_load_and_runtime_stages(self) -> None:
        stages = {obs.stage for obs in self.results.values()}
        self.assertLessEqual({"decode", "validate", "ship", "load", "runtime"}, stages)

    def test_refused_mutants_carry_a_source_position(self) -> None:
        for name, obs in sorted(self.results.items()):
            if obs.stage == "accepted":
                continue
            with self.subTest(mutant=name):
                self.assertGreaterEqual(obs.line, 1)
                self.assertGreaterEqual(obs.column, 1)


class TestDetectionIsContentOnly(MutantTestCase):
    """Rename the files, strip the comments, corrupt the manifest: nothing changes."""

    def shadow(self):
        root = self.tempdir() / "shadow"
        shutil.copytree(MUTANTS, root)
        for index, path in enumerate(sorted(root.glob("*.garns"))):
            path.write_text(re.sub(r"#[^\n]*", "", path.read_text(encoding="utf-8")), encoding="utf-8")
            path.rename(root / f"m{index:03d}.garns")
        for directory in sorted((root / "scenarios").iterdir()):
            digest = hashlib.sha256(directory.name.encode()).hexdigest()[:8]
            directory.rename(root / "scenarios" / f"s{digest}")
        (root / "expected.json").write_text('{"corrupted": true}', encoding="utf-8")
        return root

    @staticmethod
    def content_key(root, name: str) -> str:
        """A digest of the bytes a mutant is made of, independent of its own name."""
        target = root / name
        if target.is_file():
            return hashlib.sha256(re.sub(r"#[^\n]*", "", target.read_text(encoding="utf-8")).encode()).hexdigest()
        digest = hashlib.sha256()
        for path in sorted(x for x in target.rglob("*") if x.is_file()):
            digest.update(path.relative_to(target).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\n")
        return digest.hexdigest()

    def outcome_by_content(self, root, names) -> dict[str, tuple[str, str]]:
        """Key each observation by the content that produced it, not its name."""
        return {self.content_key(root, name): (obs.stage, obs.code) for name, obs in names.items()}

    def test_outcomes_are_unchanged_after_renaming_stripping_and_corrupting(self) -> None:
        root = self.shadow()
        shadowed = observe_all(root)
        self.assertEqual(len(self.results), len(shadowed))
        original = self.outcome_by_content(MUTANTS, self.results)
        renamed = self.outcome_by_content(root, shadowed)
        self.assertEqual(len(self.results), len(original), "mutant contents must be distinct")
        self.assertEqual(original, renamed)

    def test_the_corrupted_manifest_really_was_unusable(self) -> None:
        root = self.shadow()
        document = json.loads((root / "expected.json").read_text(encoding="utf-8"))
        self.assertNotIn("cases", document)
        self.assertEqual([], sorted(root.glob("*-1.garns")), "no original mutant file name survives")


if __name__ == "__main__":
    unittest.main()
