// Generated Garns surface for heldout.org_pms_user_maps (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "heldout.org_pms_user_maps";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_pms_pmsusermap" AS "$k0", s0."f_pmsusermap_created_at" AS "created_at", s0."f_pmsusermap_updated_at" AS "updated_at", s0."f_pmsusermap_pms_user_id" AS "pms_user_id" FROM "tbl_pms_pmsusermap" AS s0 WHERE ((s0."ref_pmsusermap_org" = :org) AND (s0."ref_pmsusermap_adapter" = :adapter)) ORDER BY s0."rid_pms_pmsusermap" ASC"#;
pub const PARAMS: &[&str] = &["adapter", "org"];
pub const COLUMNS: &[&str] = &["created_at", "updated_at", "pms_user_id"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
