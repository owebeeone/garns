// Generated Garns surface for sales_static.distinct_open_customers (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "sales_static.distinct_open_customers";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT DISTINCT j1."co_1e32478f5c" AS "customer" FROM "ta_8d09f00415" AS s0 LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7" WHERE (s0."co_7cbde43f56" = 'open') ORDER BY j1."co_1e32478f5c" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["customer"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
