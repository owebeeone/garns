// Generated Garns surface for labels.vip_contacts (question); the SQL is the lowered plan, unchanged.
pub const READ: &str = "labels.vip_contacts";
pub const NOUN: &str = "question";
pub const SQL: &str = r#"SELECT s0."rid_clients_contact" AS "$k0", s0."f_contact_preferred_name" AS "preferred_name", s0."f_contact_email" AS "email" FROM "tbl_clients_contact" AS s0 WHERE s0."ref_contact_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND (s0."ref_contact_client" IN (SELECT c2."rid_clients_client" FROM "tbl_clients_client" AS c2 WHERE c2."f_client_archived_at" IS NULL AND c2."ref_client_owner" = :_scope AND EXISTS (SELECT 1 FROM "tbl_labels_clientlabel" AS j3 LEFT JOIN "tbl_labels_label" AS j4 ON j4."rid_labels_label" = j3."ref_clientlabel_label" WHERE j3."ref_clientlabel_client" = c2."rid_clients_client" AND (j4."f_label_label_name" = 'vip')))) ORDER BY s0."rid_clients_contact" ASC"#;
pub const PARAMS: &[&str] = &[];
pub const COLUMNS: &[&str] = &["preferred_name", "email"];
pub const SCOPED: bool = true;
pub const USES_CLOCK: bool = false;
