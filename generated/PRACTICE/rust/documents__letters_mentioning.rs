// Generated Garns surface for documents.letters_mentioning (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "documents.letters_mentioning";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_documents_document" AS "$k0", s0."f_document_title" AS "title", s0."f_letter_body" AS "body" FROM "tbl_documents_document" AS s0 WHERE s0."member_of_documents_document" = 'Letter' AND s0."f_document_archived_at" IS NULL AND s0."ref_document_owner" = :_scope AND (instr(s0."f_letter_body", :q) > 0) ORDER BY s0."rid_documents_document" ASC"#;
pub const PARAMS: &[&str] = &["q"];
pub const COLUMNS: &[&str] = &["title", "body"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
