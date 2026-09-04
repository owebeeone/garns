// Generated Garns surface for notes.client_card (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "notes.client_card";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name", s0."f_client_archived_at" AS "archived_at", j1."f_user_email" AS "owner.email" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" WHERE s0."ref_client_owner" = :_scope AND s0."rid_clients_client" = :client ORDER BY s0."rid_clients_client" ASC LIMIT 1"#;
pub const PARAMS: &[&str] = &["client"];
pub const COLUMNS: &[&str] = &["preferred_name", "archived_at", "owner.email", "contacts", "notes"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
