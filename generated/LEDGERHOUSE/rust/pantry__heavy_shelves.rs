// Generated Garns surface for pantry.heavy_shelves (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "pantry.heavy_shelves";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."shelf_no" AS "$k0", s0."label_txt" AS "shelf_label" FROM "shelf" AS s0 WHERE s0."kept_by" = :_scope AND EXISTS (SELECT 1 FROM "jar" AS j1 WHERE j1."on_shelf" = s0."shelf_no" AND (j1."mass_g" > 500)) ORDER BY s0."shelf_no" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["shelf_label"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
