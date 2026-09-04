// Generated Garns surface for clients.contacts_with_relationship (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "clients.contacts_with_relationship";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_contact" AS "$k0", s0."f_contact_preferred_name" AS "preferred_name", s0."f_contact_relationship" AS "relationship" FROM "tbl_clients_contact" AS s0 WHERE s0."ref_contact_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND (s0."f_contact_relationship" = :kind) ORDER BY s0."rid_clients_contact" ASC"#;
pub const PARAMS: &[&str] = &["kind"];
pub const COLUMNS: &[&str] = &["preferred_name", "relationship"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
