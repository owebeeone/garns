// Generated Garns surface for heldout.adapters_by_status (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "heldout.adapters_by_status";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_pms_pmsadapter" AS "$k0", s0."f_pmsadapter_pms_id" AS "pms_id", s0."f_pmsadapter_adapter_status" AS "adapter_status", s0."f_pmsadapter_is_development" AS "is_development", s0."f_pmsadapter_enabled" AS "enabled" FROM "tbl_pms_pmsadapter" AS s0 WHERE (s0."f_pmsadapter_adapter_status" = :status) ORDER BY s0."rid_pms_pmsadapter" ASC"#;
pub const PARAMS: &[&str] = &["status"];
pub const COLUMNS: &[&str] = &["pms_id", "adapter_status", "is_development", "enabled"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
