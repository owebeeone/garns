// Generated Garns surface for pantry.open_jars (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "pantry.open_jars";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."jar_no" AS "$k0", s0."lbl" AS "jar_label", s0."mass_g" AS "grams", j2."label_txt" AS "shelf" FROM "jar" AS s0 LEFT JOIN "shelf" AS j2 ON j2."shelf_no" = s0."on_shelf" WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) AND (s0."cond" = 'open') ORDER BY s0."mass_g" DESC, s0."jar_no" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["jar_label", "grams", "shelf"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
