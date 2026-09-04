"""Resolve and bind: qualified identities, scope paths, exhaustive visitors.

Every world in the corpus is discovered from its storage binding on disk and
selected by its qualified world name, which is the only selection the public
boundary admits.
"""

from __future__ import annotations

import unittest

from tests.support import BUILD, GarnsTestCase, discovered_worlds, program_of, world_ir

from garns import ir as I
from garns.footprint import FootprintDeriver
from garns.lower_sqlite import _Lowerer, _ShowLowerer
from garns.refuse import Refusal
from garns.storage import bind_world
from garns.visit import EXPR_NODES, OPERAND_NODES, SHOW_NODES, check_exhaustive

PRACTICE = ("PRACTICE", "corpus/worlds/practice")
LEDGERHOUSE = ("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")
REPORTING = ("REPORTING", "corpus/conformance/worlds/reporting")


class TestWorldsResolveAndBind(GarnsTestCase):
    def test_the_corpus_offers_the_worlds_the_suite_expects_to_cover(self) -> None:
        names = {name for name, _ in discovered_worlds()}
        self.assertLessEqual({"PRACTICE", "EVERBILITY", "VAULTWARDEN", "APPFLOWY", "APPFLOWY_VEC",
                              "REPORTING", "SALES", "LEDGERHOUSE"}, names)
        self.assertEqual(5, sum(1 for _, rel in discovered_worlds() if "evolution" in rel))

    def test_every_discovered_world_resolves_and_binds(self) -> None:
        for name, rel in discovered_worlds():
            with self.subTest(world=name, source=rel):
                world = world_ir(name, rel)
                self.assertEqual(name, world.world.name)
                self.assertEqual(name, world.storage.world)
                self.assertTrue(world.relations, "a bound world maps at least one relation")
                for carrier in world.relations:
                    mapping = world.storage.relation(carrier.qid)
                    self.assertEqual(carrier.qid, mapping.carrier)
                    self.assertTrue(mapping.table and mapping.identity)

    def test_a_bound_world_maps_exactly_its_own_storable_carriers(self) -> None:
        for name, rel in discovered_worlds():
            with self.subTest(world=name, source=rel):
                world = world_ir(name, rel)
                self.assertEqual({c.qid for c in world.relations}, set(world.storage.relations))
                for carrier in world.relations:
                    self.assertIn(carrier.module, world.world.modules)

    def test_a_standalone_unenforced_link_resolves_as_a_typed_link(self) -> None:
        world = world_ir(*REPORTING)
        link = world.carrier("reporting.Invoice").link_named("customer")
        self.assertIsNotNone(link)
        self.assertEqual("unenforced", link.enforcement)
        self.assertEqual("invoices", link.inverse)


class TestQualifiedIdentities(GarnsTestCase):
    """No bare names survive resolution."""

    def programs(self):
        seen = set()
        for _, rel in discovered_worlds():
            if rel in seen:
                continue
            seen.add(rel)
            yield rel, program_of(rel)

    def test_carriers_reads_and_intents_are_qualified_by_their_module(self) -> None:
        for rel, program in self.programs():
            with self.subTest(source=rel):
                modules = {m.name for m in program.modules}
                for carrier in program.carriers:
                    self.assertEqual(f"{carrier.module}.{carrier.name}", carrier.qid)
                    self.assertIn(carrier.module, modules)
                for read in program.reads:
                    self.assertEqual(f"{read.module}.{read.name}", read.qid)
                    self.assertIn(read.subject, {c.qid for c in program.carriers})
                for intent in program.intents:
                    self.assertIn(".", intent.qid)
                    self.assertIn(intent.qid.rsplit(".", 1)[0], modules)

    def test_carrier_members_links_and_uses_name_qualified_identities(self) -> None:
        for rel, program in self.programs():
            with self.subTest(source=rel):
                qids = {c.qid for c in program.carriers}
                intents = {i.qid for i in program.intents}
                for carrier in program.carriers:
                    for use in carrier.uses:
                        self.assertIn(use.intent, intents, f"{carrier.qid} uses an unqualified intent")
                        self.assertEqual(use.qid, f"{carrier.qid}.{use.intent.rsplit('.', 1)[-1]}")
                    for link in carrier.links:
                        self.assertIn(link.target, qids, f"{carrier.qid}.{link.name} targets a bare name")
                    for member in carrier.members:
                        self.assertIn(member, qids)
                    if carrier.family is not None:
                        self.assertIn(carrier.family, qids)

    def test_storage_bindings_are_keyed_by_qualified_identities(self) -> None:
        for name, rel in discovered_worlds():
            with self.subTest(world=name, source=rel):
                world = world_ir(name, rel)
                for qid, mapping in world.storage.relations.items():
                    self.assertIn(".", qid)
                    for key in list(mapping.columns) + list(mapping.links):
                        self.assertGreaterEqual(key.count("."), 2, f"{key} is not a qualified field key")


class TestScopePaths(GarnsTestCase):
    def test_practice_scope_paths_include_a_multihop_case(self) -> None:
        world = world_ir(*PRACTICE)
        self.assertEqual(("clients.Client.owner",), world.scope_path("clients.Client"))
        self.assertEqual(("clients.Contact.client", "clients.Client.owner"), world.scope_path("clients.Contact"))
        self.assertEqual(("notes.Note.client", "clients.Client.owner"), world.scope_path("notes.Note"))

    def test_carriers_exempt_from_the_scope_trait_have_no_scope_path(self) -> None:
        world = world_ir(*PRACTICE)
        self.assertTrue(world.world.exempt, "PRACTICE declares exemptions from its scope trait")
        for exempt in world.world.exempt:
            with self.subTest(carrier=exempt):
                self.assertEqual((), world.scope_path(exempt))

    def test_ledgerhouse_scopes_a_jar_through_its_shelf(self) -> None:
        world = world_ir(*LEDGERHOUSE)
        self.assertEqual(("pantry.Shelf.keeper",), world.scope_path("pantry.Shelf"))
        self.assertEqual(("pantry.Jar.shelf", "pantry.Shelf.keeper"), world.scope_path("pantry.Jar"))

    def test_every_scope_path_step_is_a_declared_link_ending_at_the_scope_root(self) -> None:
        for name, rel in discovered_worlds():
            world = world_ir(name, rel)
            root = world.world.scope.root if world.world.scope else None
            for carrier_qid, path in world.scope_paths.items():
                if not path:  # exempt or unscoped carriers carry no path at all
                    continue
                with self.subTest(world=name, carrier=carrier_qid):
                    hop = carrier_qid
                    for step in path:
                        owner, local = step.rsplit(".", 1)
                        link = world.carrier(owner).link_named(local)
                        self.assertIsNotNone(link, f"{step} is not a declared link")
                        self.assertIn(owner, (hop, world.relation_carrier(hop).qid),
                                      f"{step} does not continue the path from {hop}")
                        hop = link.target
                    self.assertEqual(root, hop, "a scope path ends at the world's scope root")


class TestExhaustiveVisitors(GarnsTestCase):
    def test_footprint_visitor_handles_every_expression_operand_and_show(self) -> None:
        for nodes, label in ((EXPR_NODES, "expressions"), (OPERAND_NODES, "operands"), (SHOW_NODES, "shows")):
            with self.subTest(union=label):
                self.assertEqual([], check_exhaustive(FootprintDeriver, nodes))

    def test_sql_lowering_visitors_handle_every_expression_operand_and_show(self) -> None:
        self.assertEqual([], check_exhaustive(_Lowerer, EXPR_NODES))
        self.assertEqual([], check_exhaustive(_Lowerer, OPERAND_NODES))
        self.assertEqual([], check_exhaustive(_ShowLowerer, SHOW_NODES))

    def test_an_unhandled_ir_node_is_reported_by_every_visitor(self) -> None:
        class Phantom(I.And):
            pass

        self.assertEqual(["Phantom"], check_exhaustive(FootprintDeriver, (Phantom,)))
        self.assertEqual(["Phantom"], check_exhaustive(_Lowerer, (Phantom,)))
        self.assertEqual(["Phantom"], check_exhaustive(_ShowLowerer, (Phantom,)))

    def test_dispatching_an_unhandled_node_fails_loudly_at_runtime(self) -> None:
        class Phantom(I.And):
            pass

        deriver = FootprintDeriver(world_ir(*PRACTICE))
        with self.assertRaises(TypeError):
            deriver.visit(Phantom(items=()))


class TestSelectionRefuses(GarnsTestCase):
    def test_an_unknown_world_name_refuses(self) -> None:
        with self.assertRaises(Refusal) as caught:
            bind_world(program_of(PRACTICE[1]), "NOT_A_WORLD", BUILD / PRACTICE[1] / "storage-PRACTICE.json")
        self.assertEqual("WORLD_UNKNOWN", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
