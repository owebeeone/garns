// Generated Garns surface for clients.client_assignments (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "clients.client_assignments";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name", j1."f_user_email" AS "owner.email" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND ((:q IS NULL OR (instr(s0."f_client_preferred_name", :q) > 0)) AND (:creators IS NULL OR (j1."f_user_email" IN (SELECT value FROM json_each(:creators))))) ORDER BY s0."f_client_preferred_name" ASC, s0."rid_clients_client" ASC LIMIT :limit OFFSET (:page - 1) * :limit"#;
pub const PARAMS: &[&str] = &["creators", "limit", "page", "q"];
pub const COLUMNS: &[&str] = &["preferred_name", "owner.email"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
