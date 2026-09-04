// Generated Garns surface for sales.open_orders (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "sales.open_orders";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."id_76d3517dac" AS "$k0", s0."id_76d3517dac" AS "identity", j1."co_1e32478f5c" AS "customer", s0."co_26bff25d88" AS "total" FROM "ta_8d09f00415" AS s0 LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7" WHERE (s0."co_7cbde43f56" = 'open') ORDER BY s0."co_66617ed9a4" DESC, s0."id_76d3517dac" ASC LIMIT 20"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["identity", "customer", "total"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
