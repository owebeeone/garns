// Generated Garns surface for sales_static.revenue_open_by_customer (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "sales_static.revenue_open_by_customer";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT j1."co_1e32478f5c" AS "$k0", j1."co_1e32478f5c" AS "customer", SUM(s0."co_26bff25d88") AS "revenue", COUNT(*) AS "orders", ROUND((CAST(SUM(s0."co_26bff25d88") AS REAL) / COUNT(*)), 2) AS "average_order" FROM "ta_8d09f00415" AS s0 LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7" WHERE ((s0."co_7cbde43f56" = 'open') AND (s0."co_26bff25d88" >= :floor)) GROUP BY j1."co_1e32478f5c" HAVING (SUM(s0."co_26bff25d88") > :floor) ORDER BY SUM(s0."co_26bff25d88") DESC, LENGTH(j1."co_1e32478f5c") ASC, j1."co_1e32478f5c" ASC"#;
pub const PARAMS: &[&str] = &["floor"];
pub const COLUMNS: &[&str] = &["customer", "revenue", "orders", "average_order"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
