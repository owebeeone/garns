// Generated Garns surface for heldout.check_org_client (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "heldout.check_org_client";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_created_at" AS "created_at", s0."f_client_updated_at" AS "updated_at", s0."f_client_first_name" AS "first_name", s0."f_client_last_name" AS "last_name", s0."f_client_archived_at" AS "archived_at" FROM "tbl_clients_client" AS s0 WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND (s0."ref_client_org" = :org) ORDER BY s0."rid_clients_client" ASC"#;
pub const PARAMS: &[&str] = &["org"];
pub const COLUMNS: &[&str] = &["created_at", "updated_at", "first_name", "last_name", "archived_at"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
