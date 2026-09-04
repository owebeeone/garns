// Generated Garns surface for vault.unexpired_sends (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "vault.unexpired_sends";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_vault_send" AS "$k0", s0."f_send_send_name" AS "send_name", s0."f_send_expiration_date" AS "expiration_date", s0."f_send_deletion_date" AS "deletion_date" FROM "tbl_vault_send" AS s0 WHERE ((s0."f_send_disabled" = 0) AND (s0."f_send_deletion_date" > :_clock) AND ((s0."f_send_expiration_date" IS NULL) OR (s0."f_send_expiration_date" > :_clock))) ORDER BY s0."f_send_deletion_date" ASC, s0."rid_vault_send" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["send_name", "expiration_date", "deletion_date"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = true;
