// Generated Garns surface for notes.dormant_clients (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "notes.dormant_clients";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name" FROM "tbl_clients_client" AS s0 WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND ((SELECT COUNT(*) FROM "tbl_notes_note" AS j1 WHERE j1."ref_note_client" = s0."rid_clients_client" AND (j1."f_note_recorded_at" >= :after)) = 0) ORDER BY s0."rid_clients_client" ASC"#;
pub const PARAMS: &[&str] = &["after"];
pub const COLUMNS: &[&str] = &["preferred_name"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
