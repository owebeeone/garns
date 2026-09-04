CREATE TABLE "tbl_clients_client" (
  "rid_clients_client" INTEGER PRIMARY KEY,
  "f_client_created_at" INTEGER NOT NULL,
  "f_client_updated_at" INTEGER,
  "f_client_first_name" TEXT NOT NULL,
  "f_client_last_name" TEXT,
  "f_client_archived_at" INTEGER,
  "ref_client_owner" INTEGER NOT NULL,
  "ref_client_org" INTEGER,
  FOREIGN KEY ("ref_client_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_client_org") REFERENCES "tbl_people_organisation"("rid_people_organisation") ON DELETE RESTRICT
);

CREATE TABLE "tbl_clients_clientuser" (
  "rid_clients_clientuser" INTEGER PRIMARY KEY,
  "f_clientuser_assigned_at" INTEGER NOT NULL,
  "ref_clientuser_client" INTEGER NOT NULL,
  "ref_clientuser_user" INTEGER NOT NULL,
  FOREIGN KEY ("ref_clientuser_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE,
  FOREIGN KEY ("ref_clientuser_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_documents_docxreferencedoc" (
  "rid_documents_docxreferencedoc" INTEGER PRIMARY KEY,
  "f_docxreferencedoc_created_at" INTEGER NOT NULL,
  "f_docxreferencedoc_updated_at" INTEGER,
  "f_docxreferencedoc_doc_scope" TEXT NOT NULL,
  "f_docxreferencedoc_display_name" TEXT NOT NULL,
  "f_docxreferencedoc_original_filename" TEXT NOT NULL,
  "f_docxreferencedoc_s3_key" TEXT NOT NULL,
  "f_docxreferencedoc_file_size_bytes" INTEGER NOT NULL,
  "f_docxreferencedoc_sha256" TEXT NOT NULL,
  "ref_docxreferencedoc_owner_user" INTEGER,
  "ref_docxreferencedoc_org" INTEGER,
  "ref_docxreferencedoc_created_by" INTEGER NOT NULL,
  CHECK ("f_docxreferencedoc_doc_scope" IN ('personal', 'org')),
  UNIQUE ("f_docxreferencedoc_s3_key"),
  FOREIGN KEY ("ref_docxreferencedoc_owner_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_docxreferencedoc_org") REFERENCES "tbl_people_organisation"("rid_people_organisation") ON DELETE CASCADE,
  FOREIGN KEY ("ref_docxreferencedoc_created_by") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_merge_mergetag" (
  "rid_merge_mergetag" INTEGER PRIMARY KEY,
  "f_mergetag_created_at" INTEGER NOT NULL,
  "f_mergetag_updated_at" INTEGER,
  "f_mergetag_property_id" TEXT NOT NULL,
  "f_mergetag_property_name" TEXT NOT NULL DEFAULT '',
  "f_mergetag_can_delete" INTEGER NOT NULL DEFAULT 1,
  "ref_mergetag_owner" INTEGER NOT NULL,
  UNIQUE ("f_mergetag_property_id"),
  FOREIGN KEY ("ref_mergetag_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_merge_mergetagclient" (
  "rid_merge_mergetagclient" INTEGER PRIMARY KEY,
  "f_mergetagclient_created_at" INTEGER NOT NULL,
  "f_mergetagclient_updated_at" INTEGER,
  "f_mergetagclient_property_value" TEXT NOT NULL,
  "ref_mergetagclient_user" INTEGER NOT NULL,
  "ref_mergetagclient_client" INTEGER NOT NULL,
  "ref_mergetagclient_tag" INTEGER NOT NULL,
  FOREIGN KEY ("ref_mergetagclient_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_mergetagclient_client") REFERENCES "tbl_clients_client"("rid_clients_client") ON DELETE CASCADE,
  FOREIGN KEY ("ref_mergetagclient_tag") REFERENCES "tbl_merge_mergetag"("rid_merge_mergetag") ON DELETE CASCADE
);

CREATE TABLE "tbl_people_organisation" (
  "rid_people_organisation" INTEGER PRIMARY KEY,
  "f_organisation_created_at" INTEGER NOT NULL,
  "f_organisation_updated_at" INTEGER,
  "f_organisation_org_id" TEXT NOT NULL,
  "f_organisation_in_trial" INTEGER NOT NULL DEFAULT 0,
  "f_organisation_is_paying" INTEGER NOT NULL DEFAULT 0,
  "f_organisation_seats" INTEGER NOT NULL DEFAULT 1,
  "f_organisation_stripe_customer_id" TEXT,
  "ref_organisation_created_by" INTEGER NOT NULL,
  UNIQUE ("f_organisation_org_id", "ref_organisation_created_by"),
  FOREIGN KEY ("ref_organisation_created_by") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_people_user" (
  "rid_people_user" INTEGER PRIMARY KEY,
  "f_user_created_at" INTEGER NOT NULL,
  "f_user_updated_at" INTEGER,
  "f_user_clerk_user_id" TEXT NOT NULL,
  "f_user_email" TEXT NOT NULL,
  "f_user_in_trial" INTEGER NOT NULL DEFAULT 1,
  "f_user_is_paying" INTEGER NOT NULL DEFAULT 0,
  "f_user_stripe_customer_id" TEXT,
  "f_user_profession_updated" INTEGER NOT NULL DEFAULT 0,
  "f_user_is_onboarded" INTEGER NOT NULL DEFAULT 0,
  "ref_user_profession" INTEGER NOT NULL,
  "ref_user_language" INTEGER NOT NULL,
  "ref_user_funding_model" INTEGER NOT NULL,
  UNIQUE ("f_user_clerk_user_id"),
  FOREIGN KEY ("ref_user_profession") REFERENCES "tbl_refs_profession"("rid_refs_profession") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_user_language") REFERENCES "tbl_refs_language"("rid_refs_language") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_user_funding_model") REFERENCES "tbl_refs_fundingmodel"("rid_refs_fundingmodel") ON DELETE RESTRICT
);

CREATE TABLE "tbl_people_userpreference" (
  "rid_people_userpreference" INTEGER PRIMARY KEY,
  "f_userpreference_created_at" INTEGER NOT NULL,
  "f_userpreference_updated_at" INTEGER,
  "f_userpreference_note_template" TEXT,
  "f_userpreference_report_template" TEXT,
  "ref_userpreference_user" INTEGER NOT NULL,
  UNIQUE ("ref_userpreference_user"),
  FOREIGN KEY ("ref_userpreference_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE
);

CREATE TABLE "tbl_pms_pmsadapter" (
  "rid_pms_pmsadapter" INTEGER PRIMARY KEY,
  "f_pmsadapter_pms_id" TEXT NOT NULL,
  "f_pmsadapter_adapter_status" TEXT NOT NULL,
  "f_pmsadapter_is_development" INTEGER NOT NULL DEFAULT 0,
  "f_pmsadapter_enabled" INTEGER NOT NULL DEFAULT 1,
  CHECK ("f_pmsadapter_adapter_status" IN ('available', 'coming_soon')),
  UNIQUE ("f_pmsadapter_pms_id")
);

CREATE TABLE "tbl_pms_pmsapikey" (
  "rid_pms_pmsapikey" INTEGER PRIMARY KEY,
  "f_pmsapikey_created_at" INTEGER NOT NULL,
  "f_pmsapikey_updated_at" INTEGER,
  "f_pmsapikey_kid" TEXT NOT NULL,
  "f_pmsapikey_api_ek" TEXT NOT NULL,
  "f_pmsapikey_api_client_id" TEXT,
  "f_pmsapikey_is_org_wide" INTEGER NOT NULL DEFAULT 0,
  "ref_pmsapikey_owner" INTEGER NOT NULL,
  "ref_pmsapikey_adapter" INTEGER NOT NULL,
  "ref_pmsapikey_org" INTEGER,
  UNIQUE ("ref_pmsapikey_adapter"),
  FOREIGN KEY ("ref_pmsapikey_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_pmsapikey_adapter") REFERENCES "tbl_pms_pmsadapter"("rid_pms_pmsadapter") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_pmsapikey_org") REFERENCES "tbl_people_organisation"("rid_people_organisation") ON DELETE SET NULL
);

CREATE TABLE "tbl_pms_pmsusermap" (
  "rid_pms_pmsusermap" INTEGER PRIMARY KEY,
  "f_pmsusermap_created_at" INTEGER NOT NULL,
  "f_pmsusermap_updated_at" INTEGER,
  "f_pmsusermap_pms_user_id" TEXT NOT NULL,
  "ref_pmsusermap_user" INTEGER NOT NULL,
  "ref_pmsusermap_adapter" INTEGER NOT NULL,
  "ref_pmsusermap_org" INTEGER,
  FOREIGN KEY ("ref_pmsusermap_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_pmsusermap_adapter") REFERENCES "tbl_pms_pmsadapter"("rid_pms_pmsadapter") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_pmsusermap_org") REFERENCES "tbl_people_organisation"("rid_people_organisation") ON DELETE CASCADE
);

CREATE TABLE "tbl_refs_fundingmodel" (
  "rid_refs_fundingmodel" INTEGER PRIMARY KEY,
  "f_fundingmodel_name" TEXT NOT NULL DEFAULT '',
  "f_fundingmodel_display_name" TEXT NOT NULL DEFAULT 'EMPTY'
);

CREATE TABLE "tbl_refs_language" (
  "rid_refs_language" INTEGER PRIMARY KEY,
  "f_language_name" TEXT NOT NULL DEFAULT ''
);

CREATE TABLE "tbl_refs_profession" (
  "rid_refs_profession" INTEGER PRIMARY KEY,
  "f_profession_name" TEXT NOT NULL,
  "f_profession_display_name" TEXT NOT NULL
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
