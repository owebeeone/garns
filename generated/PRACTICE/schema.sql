CREATE TABLE "tbl_clients_client" (
  "rid_clients_client" INTEGER PRIMARY KEY,
  "f_client_created_at" INTEGER NOT NULL,
  "f_client_updated_at" INTEGER,
  "f_client_preferred_name" TEXT NOT NULL,
  "f_client_archived_at" INTEGER,
  "ref_client_owner" INTEGER NOT NULL,
  FOREIGN KEY ("ref_client_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_clients_contact" (
  "rid_clients_contact" INTEGER PRIMARY KEY,
  "f_contact_created_at" INTEGER NOT NULL,
  "f_contact_updated_at" INTEGER,
  "f_contact_preferred_name" TEXT NOT NULL,
  "f_contact_email" TEXT NOT NULL,
  "f_contact_relationship" TEXT NOT NULL,
  "ref_contact_client" INTEGER NOT NULL,
  FOREIGN KEY ("ref_contact_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE
);

CREATE TABLE "tbl_documents_document" (
  "rid_documents_document" INTEGER PRIMARY KEY,
  "f_document_created_at" INTEGER NOT NULL,
  "f_document_updated_at" INTEGER,
  "f_document_title" TEXT NOT NULL,
  "f_document_archived_at" INTEGER,
  "f_form_template_ref" TEXT,
  "f_letter_body" TEXT,
  "ref_document_owner" INTEGER NOT NULL,
  "ref_document_client" INTEGER NOT NULL,
  "member_of_documents_document" TEXT NOT NULL CHECK ("member_of_documents_document" IN ('Form', 'Letter')),
  FOREIGN KEY ("ref_document_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_document_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE
);

CREATE TABLE "tbl_labels_clientlabel" (
  "rid_labels_clientlabel" INTEGER PRIMARY KEY,
  "ref_clientlabel_client" INTEGER NOT NULL,
  "ref_clientlabel_label" INTEGER NOT NULL,
  FOREIGN KEY ("ref_clientlabel_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE,
  FOREIGN KEY ("ref_clientlabel_label") REFERENCES "tbl_labels_label"("rid_labels_label") ON DELETE RESTRICT
);

CREATE TABLE "tbl_labels_label" (
  "rid_labels_label" INTEGER PRIMARY KEY,
  "f_label_label_name" TEXT NOT NULL,
  UNIQUE ("f_label_label_name")
);

CREATE TABLE "tbl_notes_note" (
  "rid_notes_note" INTEGER PRIMARY KEY,
  "f_note_note_body" TEXT NOT NULL,
  "f_note_recorded_at" INTEGER NOT NULL,
  "ref_note_client" INTEGER NOT NULL,
  FOREIGN KEY ("ref_note_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE
);

CREATE TABLE "tbl_people_user" (
  "rid_people_user" INTEGER PRIMARY KEY,
  "f_user_created_at" INTEGER NOT NULL,
  "f_user_updated_at" INTEGER,
  "f_user_email" TEXT NOT NULL,
  UNIQUE ("f_user_email")
);

CREATE TABLE "tbl_workspaces_workspace" (
  "rid_workspaces_workspace" INTEGER PRIMARY KEY,
  "f_workspace_share" TEXT NOT NULL,
  "f_workspace_display_name" TEXT NOT NULL,
  UNIQUE ("f_workspace_share")
);

CREATE TABLE "garns_generations" (
  ordinal INTEGER PRIMARY KEY,
  ir_digest TEXT NOT NULL,
  storage_digest TEXT NOT NULL,
  shipped_at_revision INTEGER NOT NULL
);

CREATE TABLE "garns_revisions" (
  revision INTEGER PRIMARY KEY,
  writer TEXT NOT NULL,
  transaction_id TEXT NOT NULL
);

CREATE TABLE "garns_ledger" (
  revision INTEGER NOT NULL,
  ordinal INTEGER NOT NULL,
  carrier TEXT NOT NULL,
  identity INTEGER NOT NULL,
  operation TEXT NOT NULL CHECK (operation IN ('insert', 'update', 'delete')),
  changes TEXT NOT NULL,
  scope_before TEXT,
  scope_after TEXT,
  writer TEXT NOT NULL,
  transaction_id TEXT NOT NULL,
  PRIMARY KEY (revision, ordinal)
);
