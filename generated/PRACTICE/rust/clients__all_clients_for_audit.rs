// Generated Garns surface for clients.all_clients_for_audit (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "clients.all_clients_for_audit";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name", s0."f_client_archived_at" AS "archived_at", j1."f_user_email" AS "owner.email" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" ORDER BY s0."f_client_preferred_name" ASC, s0."rid_clients_client" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["preferred_name", "archived_at", "owner.email"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
