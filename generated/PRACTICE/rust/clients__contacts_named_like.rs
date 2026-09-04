// Generated Garns surface for clients.contacts_named_like (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "clients.contacts_named_like";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_contact" AS "$k0", s0."f_contact_preferred_name" AS "preferred_name", j2."f_client_preferred_name" AS "client.preferred_name" FROM "tbl_clients_contact" AS s0 LEFT JOIN "tbl_clients_client" AS j2 ON j2."rid_clients_client" = s0."ref_contact_client" WHERE s0."ref_contact_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND (instr(j2."f_client_preferred_name", :q) > 0) ORDER BY s0."f_contact_preferred_name" ASC, s0."rid_clients_contact" ASC"#;
pub const PARAMS: &[&str] = &["q"];
pub const COLUMNS: &[&str] = &["preferred_name", "client.preferred_name"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
