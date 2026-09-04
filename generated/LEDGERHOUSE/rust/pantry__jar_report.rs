// Generated Garns surface for pantry.jar_report (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "pantry.jar_report";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."cond" AS "$k0", s0."cond" AS "state", SUM(s0."mass_g") AS "total_grams", ROUND(AVG(s0."mass_g"), 1) AS "mean_grams" FROM "jar" AS s0 WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) AND (s0."mass_g" >= :floor) GROUP BY s0."cond" HAVING (SUM(s0."mass_g") > :floor) ORDER BY SUM(s0."mass_g") DESC, s0."cond" ASC"#;
pub const PARAMS: &[&str] = &["floor"];
pub const COLUMNS: &[&str] = &["state", "total_grams", "mean_grams"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
