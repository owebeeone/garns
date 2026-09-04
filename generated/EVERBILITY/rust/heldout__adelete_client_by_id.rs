// Generated Garns surface for heldout.adelete_client_by_id (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "heldout.adelete_client_by_id";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_first_name" AS "first_name", j1."f_organisation_org_id" AS "org.org_id" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_organisation" AS j1 ON j1."rid_people_organisation" = s0."ref_client_org" WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND s0."rid_clients_client" = :client AND (s0."f_client_archived_at" IS NULL) ORDER BY s0."rid_clients_client" ASC LIMIT 1"#;
pub const PARAMS: &[&str] = &["client"];
pub const COLUMNS: &[&str] = &["first_name", "org.org_id"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
