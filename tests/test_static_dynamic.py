"""Static query and dynamic question over the SALES world.

Every expectation is computed from the rows this module seeds, so no SQL text
and no recorded answer is supplied to the implementation.
"""

from __future__ import annotations

import unittest

from tests.support import SALES_CUSTOMER_NAMES, SALES_ORDERS, GarnsTestCase, seed_sales, world_ir

from garns.footprint import derive_footprint
from garns.generate import generate
from garns.live import LiveEngine, canonical_rows
from garns.refuse import Refusal

SALES = ("SALES", "corpus/conformance/worlds/sales")
QUESTION = "sales.open_orders"
QUERY = "sales_static.open_orders_once"
RICHER = "sales_static.revenue_open_by_customer"
DISTINCT = "sales_static.distinct_open_customers"


def open_orders_expected() -> list[dict[str, object]]:
    """The seed's open orders, newest first, exactly as the source declares."""
    rows = [
        {"identity": n + 1, "customer": SALES_CUSTOMER_NAMES[customer], "total": total, "created_at": created}
        for n, (customer, status, total, created) in enumerate(SALES_ORDERS)
        if status == "open"
    ]
    rows.sort(key=lambda row: row["created_at"], reverse=True)
    return [{"identity": r["identity"], "customer": r["customer"], "total": r["total"]} for r in rows]


def revenue_expected(floor: float) -> list[dict[str, object]]:
    totals: dict[str, list[float]] = {}
    for customer, status, total, _created in SALES_ORDERS:
        if status == "open" and total >= floor:
            totals.setdefault(SALES_CUSTOMER_NAMES[customer], []).append(total)
    rows = [
        {"customer": name, "revenue": sum(values), "orders": len(values), "average_order": round(sum(values) / len(values), 2)}
        for name, values in totals.items()
        if sum(values) > floor
    ]
    rows.sort(key=lambda row: (-row["revenue"], len(row["customer"])))
    return rows


class SalesTestCase(GarnsTestCase):
    def setUp(self) -> None:
        self.world = world_ir(*SALES)
        self.store, self.engine, self.live = self.shipped(self.world, clock=50)
        self.ids = seed_sales(self.engine)


class TestParity(SalesTestCase):
    def test_query_one_shot_rows_equal_the_questions_initial_live_rows(self) -> None:
        one_shot = self.engine.execute(QUERY).rows
        instance = self.live.subscribe(QUESTION)
        self.assertEqual(canonical_rows(one_shot), canonical_rows(instance.rows()))

    def test_both_forms_agree_with_the_rows_the_test_seeded(self) -> None:
        expected = open_orders_expected()
        self.assertEqual(expected, self.engine.execute(QUERY).rows)
        self.assertEqual(expected, self.live.subscribe(QUESTION).rows())

    def test_both_nouns_lower_through_one_plan_type_with_the_same_shape(self) -> None:
        query_plan = self.engine.plan(QUERY)
        question_plan = self.engine.plan(QUESTION)
        self.assertIs(type(query_plan), type(question_plan))
        self.assertEqual(query_plan.columns, question_plan.columns)
        self.assertEqual(query_plan.key_columns, question_plan.key_columns)


class TestRicherStaticQuery(SalesTestCase):
    def test_group_having_arithmetic_and_call_execute(self) -> None:
        self.assertEqual(revenue_expected(10), self.engine.execute(RICHER, {"floor": 10}).rows)

    def test_the_having_clause_actually_filters(self) -> None:
        floor = 160
        rows = self.engine.execute(RICHER, {"floor": floor}).rows
        self.assertEqual(revenue_expected(floor), rows)
        self.assertNotEqual(revenue_expected(10), rows, "a different floor must produce a different report")

    def test_distinct_static_query_executes(self) -> None:
        expected = sorted({SALES_CUSTOMER_NAMES[c] for c, status, _t, _a in SALES_ORDERS if status == "open"})
        self.assertEqual([{"customer": name} for name in expected], self.engine.execute(DISTINCT).rows)


class TestSeparation(SalesTestCase):
    def test_subscribing_a_query_refuses_before_any_registration(self) -> None:
        live = LiveEngine(self.engine)
        with self.assertRaises(Refusal) as caught:
            live.subscribe(QUERY)
        self.assertEqual("QUERY_NOT_LIVE", caught.exception.code)
        self.assertEqual(0, len(live.registry))
        self.assertEqual({}, live.index)

    def test_deriving_a_footprint_for_a_query_refuses(self) -> None:
        with self.assertRaises(Refusal) as caught:
            derive_footprint(self.world, self.world.program.read(QUERY))
        self.assertEqual("QUERY_NOT_LIVE", caught.exception.code)

    def test_a_question_derives_a_footprint_and_registers_routing_keys(self) -> None:
        instance = self.live.subscribe(QUESTION)
        self.assertTrue(self.live.index)
        atoms = {(a.carrier, a.field) for a in instance.footprint.atoms}
        self.assertLessEqual(
            {("sales.Order", "*"), ("sales.Order", "sales.Order.status"), ("sales.Order", "sales.Order.total"),
             ("sales.Order", "sales.Order.customer"), ("sales.Order", "sales.Order.created_at"),
             ("sales.Customer", "sales.Customer.name")},
            atoms,
        )


class TestGeneratedProducts(GarnsTestCase):
    def setUp(self) -> None:
        self.world = world_ir(*SALES)
        self.files = generate(self.world, self.tempdir() / "SALES")

    def queries(self) -> list[str]:
        return sorted(r.qid for r in self.world.reads if not r.is_question)

    def test_every_query_generates_exactly_one_sql_artifact_and_nothing_live(self) -> None:
        for qid in self.queries():
            with self.subTest(read=qid):
                self.assertIn(f"queries/{qid}.sql", self.files)
                live_products = [name for name in self.files if name.startswith("questions/") and qid in name]
                self.assertEqual([], live_products)

    def test_no_question_artifact_belongs_to_a_static_module(self) -> None:
        static_modules = {qid.split(".", 1)[0] for qid in self.queries()}
        self.assertTrue(static_modules)
        for name in sorted(f for f in self.files if f.startswith("questions/")):
            with self.subTest(artifact=name):
                self.assertNotIn(name[len("questions/") :].split(".", 1)[0], static_modules)

    def test_each_question_generates_its_footprint_binding_and_routing(self) -> None:
        questions = [r.qid for r in self.world.reads if r.is_question]
        self.assertTrue(questions)
        for qid in questions:
            for suffix in ("sql", "footprint.json", "binding.json", "routing.json"):
                with self.subTest(read=qid, product=suffix):
                    self.assertIn(f"questions/{qid}.{suffix}", self.files)


if __name__ == "__main__":
    unittest.main()
