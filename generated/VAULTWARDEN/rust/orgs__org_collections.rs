// Generated Garns surface for orgs.org_collections (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "orgs.org_collections";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_orgs_collection" AS "$k0", s0."f_collection_collection_name" AS "collection_name", s0."f_collection_external_id" AS "external_id" FROM "tbl_orgs_collection" AS s0 WHERE (s0."ref_collection_org" = :org) ORDER BY s0."rid_orgs_collection" ASC"#;
pub const PARAMS: &[&str] = &["org"];
pub const COLUMNS: &[&str] = &["collection_name", "external_id"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
