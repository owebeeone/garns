// Generated Garns surface for heldout.tags_for_property (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "heldout.tags_for_property";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_merge_mergetag" AS "$k0", s0."f_mergetag_created_at" AS "created_at", s0."f_mergetag_updated_at" AS "updated_at", s0."f_mergetag_property_id" AS "property_id", s0."f_mergetag_property_name" AS "property_name", s0."f_mergetag_can_delete" AS "can_delete" FROM "tbl_merge_mergetag" AS s0 WHERE s0."ref_mergetag_owner" = :_scope AND (s0."f_mergetag_property_id" = :property) ORDER BY s0."rid_merge_mergetag" ASC"#;
pub const PARAMS: &[&str] = &["property"];
pub const COLUMNS: &[&str] = &["created_at", "updated_at", "property_id", "property_name", "can_delete"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
