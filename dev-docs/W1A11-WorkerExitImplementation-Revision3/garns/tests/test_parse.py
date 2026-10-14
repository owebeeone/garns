"""Decode stage: the frozen grammar, and refusals classified from parser state.

The refusal manifest is read only to assert against outcomes this module has
already observed by running the production pipeline. Classification inputs are
source texts written here, never file names, comments or markers.
"""

from __future__ import annotations

import json
import unittest

from tests.support import BUILD, CORPUS, PARSEABLE_ROOTS, GarnsTestCase

from garns.mutants import observe_single
from garns.parse import parse_path, parse_text, parser
from garns.refuse import Refusal

REFUSALS = CORPUS / "conformance" / "refusals"

# Minimal admitted source; each classification case below is this text with one
# element removed or replaced, so the observed code follows from that edit only.
WELL_FORMED = """module m "a small module" {
  intent code : Text "a code"

  resource Thing "a thing" {
    use code { key }
  }

  query things of Thing "every thing" {
    show code
  }
}
"""


class TestGrammar(GarnsTestCase):
    def test_parser_is_deterministic_lalr(self) -> None:
        self.assertEqual(parser().options.parser, "lalr")

    def test_well_formed_control_source_parses(self) -> None:
        source = parse_text(WELL_FORMED, "<control>")
        self.assertTrue(source.toplevels, "the control source declares at least one top-level node")


class TestCorpusParses(GarnsTestCase):
    def test_every_admitted_corpus_file_parses_with_locations(self) -> None:
        files = sorted({p for root in PARSEABLE_ROOTS for p in root.rglob("*.garns")})
        self.assertGreater(len(files), 50, "the corpus should hold many admitted sources")
        failures = []
        for path in files:
            try:
                source = parse_path(path)
            except Refusal as refusal:
                failures.append(f"{path.relative_to(BUILD)}: {refusal}")
                continue
            if not source.toplevels:
                failures.append(f"{path.relative_to(BUILD)}: parsed to no declarations")
            for top in source.toplevels:
                loc = getattr(top, "loc", None)
                if loc is None or loc.line < 1 or loc.column < 1:
                    failures.append(f"{path.relative_to(BUILD)}: {type(top).__name__} carries no location")
        self.assertEqual([], failures)

    def test_refusal_and_mutant_fixtures_are_outside_the_admitted_set(self) -> None:
        admitted = {p for root in PARSEABLE_ROOTS for p in root.rglob("*.garns")}
        designed_to_refuse = set(REFUSALS.glob("*.garns")) | set((CORPUS / "mutants").glob("*.garns"))
        self.assertEqual(set(), admitted & designed_to_refuse)


class TestFrozenRefusals(GarnsTestCase):
    """corpus/conformance/refusals: observe first, then assert against the manifest."""

    def observed(self) -> dict[str, tuple[str, str]]:
        return {p.name: (obs.stage, obs.code) for p in sorted(REFUSALS.glob("*.garns")) for obs in (observe_single(p),)}

    def expectations(self) -> dict[str, tuple[str, str]]:
        document = json.loads((REFUSALS / "expected.json").read_text(encoding="utf-8"))
        return {case["file"]: (case["stage"], case["code"]) for case in document["cases"]}

    def test_manifest_and_fixtures_describe_the_same_files(self) -> None:
        self.assertEqual(sorted(self.expectations()), sorted(self.observed()))

    def test_every_frozen_refusal_reproduces_its_recorded_stage_and_code(self) -> None:
        observed, expected = self.observed(), self.expectations()
        self.assertGreaterEqual(len(observed), 6)
        for name in sorted(observed):
            with self.subTest(fixture=name):
                self.assertEqual(expected[name], observed[name])

    def test_frozen_refusals_carry_a_source_position(self) -> None:
        for path in sorted(REFUSALS.glob("*.garns")):
            with self.subTest(fixture=path.name):
                obs = observe_single(path)
                self.assertGreaterEqual(obs.line, 1)
                self.assertGreaterEqual(obs.column, 1)
                self.assertLessEqual(obs.line, len(path.read_text(encoding="utf-8").splitlines()) + 1)


class TestDecodeClassification(GarnsTestCase):
    """Codes follow from the parser state, not from the text's shape or name."""

    def refuse(self, text: str, label: str) -> Refusal:
        with self.assertRaises(Refusal) as caught:
            parse_text(text, label)
        refusal = caught.exception
        self.assertEqual("decode", refusal.stage)
        return refusal

    def test_a_python_looking_file_is_not_a_garns_source(self) -> None:
        path = self.tempdir() / "looks_like_python.py"
        path.write_text("import os\n\n\ndef main():\n    return os.getcwd()\n", encoding="utf-8")
        with self.assertRaises(Refusal) as caught:
            parse_path(path)
        self.assertEqual(("decode", "SOURCE_NOT_GARNS"), (caught.exception.stage, caught.exception.code))

    def test_other_foreign_texts_reach_the_same_top_level_classification(self) -> None:
        for label, text in (("json", '{"a": 1}\n'), ("sql", "SELECT * FROM t;\n"), ("prose", "hello world\n")):
            with self.subTest(text=label):
                self.assertEqual("SOURCE_NOT_GARNS", self.refuse(text, f"<{label}>").code)

    def test_a_resource_without_its_meaning_string_refuses_as_means_required(self) -> None:
        without = WELL_FORMED.replace('resource Thing "a thing"', "resource Thing")
        refusal = self.refuse(without, "<no-meaning>")
        self.assertEqual("MEANS_REQUIRED", refusal.code)
        # the only difference from an admitted source is the missing string
        self.assertTrue(parse_text(WELL_FORMED, "<control>").toplevels)
        self.assertEqual(4, refusal.line, "the refusal points at the declaration that states no meaning")

    def test_a_truncated_source_refuses_as_truncated(self) -> None:
        truncated = WELL_FORMED[: WELL_FORMED.index("resource")]
        self.assertEqual("SOURCE_TRUNCATED", self.refuse(truncated, "<truncated>").code)

    def test_a_host_expression_in_a_predicate_is_outside_the_closed_algebra(self) -> None:
        hosted = WELL_FORMED.replace("    show code", '    where code = os.getenv("X")\n    show code')
        self.assertEqual("EXPR_NOT_ADMITTED", self.refuse(hosted, "<host-expr>").code)

    def test_position_of_a_decode_refusal_points_inside_the_offending_line(self) -> None:
        without = WELL_FORMED.replace('resource Thing "a thing"', "resource Thing")
        refusal = self.refuse(without, "<no-meaning>")
        line = without.splitlines()[refusal.line - 1]
        self.assertLessEqual(refusal.column, len(line) + 1)
        self.assertIn("resource Thing", line)


if __name__ == "__main__":
    unittest.main()
