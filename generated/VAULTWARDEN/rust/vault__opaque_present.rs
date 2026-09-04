// Generated Garns surface for vault.opaque_present (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "vault.opaque_present";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_vault_cipher" AS "$k0", s0."f_cipher_atype" AS "atype" FROM "tbl_vault_cipher" AS s0 WHERE s0."f_cipher_deleted_at" IS NULL AND (s0."f_cipher_cipher_data" IS NOT NULL) ORDER BY s0."rid_vault_cipher" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["atype"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
