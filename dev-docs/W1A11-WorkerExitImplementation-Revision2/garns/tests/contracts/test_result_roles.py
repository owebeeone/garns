from __future__ import annotations

import unittest

from garns.backends.contracts.semantic import (
    NESTED_RESULT_TYPE,
    NestedResult,
    ResultField,
    ResultFieldRole,
    ResultShape,
    SemanticType,
)


TEXT = SemanticType("Text", "text")
INTEGER = SemanticType("Integer", "integer")
ORDER_ID = SemanticType("Id", "text", carrier="sales.Order")
LINE_ID = SemanticType("Id", "text", carrier="sales.Line")


class ResultRoleVectorTests(unittest.TestCase):
    def test_five_normative_vectors_are_lossless(self) -> None:
        ordinary = ResultShape((
            ResultField("sales.Order.customer", TEXT),
            ResultField("$key.identity", ORDER_ID, True, ResultFieldRole.STRUCTURAL_KEY),
        ))
        optional_or_windowed = ResultShape((
            ResultField("sales.Order.total", INTEGER),
            ResultField("$key.identity", ORDER_ID, True, ResultFieldRole.STRUCTURAL_KEY),
        ))
        grouped = ResultShape((
            ResultField("$key.group.0", TEXT, True, ResultFieldRole.STRUCTURAL_KEY),
            ResultField("sales.Order.count", INTEGER),
        ))
        distinct = ResultShape((ResultField("sales.Order.customer", TEXT, True),))
        children = ResultShape((
            ResultField("sales.Line.value", TEXT),
            ResultField("$key.parent", ORDER_ID, True, ResultFieldRole.STRUCTURAL_KEY),
            ResultField("$key.identity", LINE_ID, True, ResultFieldRole.STRUCTURAL_KEY),
        ))
        rooted_nested = ResultShape((
            ResultField("sales.Order.identity", ORDER_ID, True),
            ResultField("sales.Order.lines", NESTED_RESULT_TYPE, False, ResultFieldRole.NESTED_OWNER),
        ), (NestedResult("sales.Order.lines", children),))

        vectors = (ordinary, optional_or_windowed, grouped, distinct, rooted_nested)
        reconstructed = tuple(ResultShape(shape.fields, shape.nested) for shape in vectors)
        self.assertEqual(vectors, reconstructed)
        self.assertEqual(ResultFieldRole.VISIBLE, distinct.fields[0].role)
        self.assertTrue(distinct.fields[0].key, "visible key remains independent from its role")
        self.assertEqual(ResultFieldRole.NESTED_OWNER, rooted_nested.fields[1].role)
        self.assertEqual(NESTED_RESULT_TYPE, rooted_nested.fields[1].type)

    def test_reserved_alias_and_role_type_attacks_refuse(self) -> None:
        attacks = (
            lambda: ResultField("$key.identity", ORDER_ID),
            lambda: ResultField("sales.visible", TEXT, False, ResultFieldRole.STRUCTURAL_KEY),
            lambda: ResultField("$key.identity", ORDER_ID, False, ResultFieldRole.STRUCTURAL_KEY),
            lambda: ResultField("sales.lines", TEXT, False, ResultFieldRole.NESTED_OWNER),
            lambda: ResultField("sales.lines", NESTED_RESULT_TYPE),
            lambda: ResultField("sales.value", TEXT, False, "visible"),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                with self.assertRaises((TypeError, ValueError)):
                    attack()

    def test_duplicate_or_orphan_nested_owner_refuses(self) -> None:
        owner = ResultField("sales.Order.lines", NESTED_RESULT_TYPE, role=ResultFieldRole.NESTED_OWNER)
        child = ResultShape((ResultField("sales.Line.value", TEXT),))
        with self.assertRaises(ValueError):
            ResultShape((owner,), ())
        with self.assertRaises(ValueError):
            ResultShape((owner,), (
                NestedResult(owner.qualified_name, child),
                NestedResult(owner.qualified_name, child),
            ))
        with self.assertRaises(ValueError):
            ResultShape((ResultField("sales.Order.lines", TEXT),), (
                NestedResult("sales.Order.lines", child),
            ))

    def test_exact_enum_and_boolean_members_are_required(self) -> None:
        for malformed in ("visible", 0, 1, False, True, object()):
            with self.assertRaises((TypeError, ValueError)):
                ResultField("sales.value", TEXT, False, malformed)  # type: ignore[arg-type]
        for malformed in (0, 1, "true", None):
            with self.assertRaises(TypeError):
                ResultField("sales.value", TEXT, malformed)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
