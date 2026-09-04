CREATE TABLE "tbl_auth_authrequest" (
  "rid_auth_authrequest" INTEGER PRIMARY KEY,
  "f_authrequest_created_at" INTEGER NOT NULL,
  "f_authrequest_updated_at" INTEGER,
  "f_authrequest_request_device_identifier" TEXT NOT NULL,
  "f_authrequest_device_type" INTEGER NOT NULL,
  "f_authrequest_request_ip" TEXT NOT NULL,
  "f_authrequest_response_device_id" TEXT,
  "f_authrequest_access_code" BLOB NOT NULL,
  "f_authrequest_auth_public_key" BLOB NOT NULL,
  "f_authrequest_enc_key" BLOB,
  "f_authrequest_master_password_hash" BLOB,
  "f_authrequest_approved" INTEGER,
  "f_authrequest_response_date" INTEGER,
  "f_authrequest_authentication_date" INTEGER,
  "ref_authrequest_owner" INTEGER NOT NULL,
  "ref_authrequest_org" INTEGER,
  FOREIGN KEY ("ref_authrequest_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT,
  FOREIGN KEY ("ref_authrequest_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE SET NULL
);

CREATE TABLE "tbl_auth_device" (
  "rid_auth_device" INTEGER PRIMARY KEY,
  "f_device_created_at" INTEGER NOT NULL,
  "f_device_updated_at" INTEGER,
  "f_device_device_name" TEXT NOT NULL,
  "f_device_atype" INTEGER NOT NULL,
  "f_device_push_token" TEXT,
  "f_device_refresh_token" BLOB NOT NULL,
  "f_device_twofactor_remember" BLOB,
  "f_device_push_uuid" TEXT,
  "ref_device_owner" INTEGER NOT NULL,
  FOREIGN KEY ("ref_device_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_auth_emergencyaccess" (
  "rid_auth_emergencyaccess" INTEGER PRIMARY KEY,
  "f_emergencyaccess_created_at" INTEGER NOT NULL,
  "f_emergencyaccess_updated_at" INTEGER,
  "f_emergencyaccess_email" TEXT,
  "f_emergencyaccess_key_encrypted" BLOB,
  "f_emergencyaccess_atype" INTEGER NOT NULL,
  "f_emergencyaccess_membership_status" INTEGER NOT NULL,
  "f_emergencyaccess_wait_time_days" INTEGER NOT NULL,
  "f_emergencyaccess_recovery_initiated_at" INTEGER,
  "f_emergencyaccess_last_notification_at" INTEGER,
  "ref_emergencyaccess_grantor_user" INTEGER,
  "ref_emergencyaccess_grantee_user" INTEGER,
  FOREIGN KEY ("ref_emergencyaccess_grantor_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL,
  FOREIGN KEY ("ref_emergencyaccess_grantee_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL
);

CREATE TABLE "tbl_auth_invitation" (
  "rid_auth_invitation" INTEGER PRIMARY KEY,
  "f_invitation_email" TEXT NOT NULL,
  UNIQUE ("f_invitation_email")
);

CREATE TABLE "tbl_auth_ssoauth" (
  "rid_auth_ssoauth" INTEGER PRIMARY KEY,
  "f_ssoauth_created_at" INTEGER NOT NULL,
  "f_ssoauth_updated_at" INTEGER,
  "f_ssoauth_sso_state" TEXT NOT NULL,
  "f_ssoauth_client_challenge" BLOB NOT NULL,
  "f_ssoauth_sso_nonce" TEXT NOT NULL,
  "f_ssoauth_redirect_uri" TEXT NOT NULL,
  "f_ssoauth_code_response" BLOB,
  "f_ssoauth_auth_response" BLOB,
  "f_ssoauth_binding_hash" BLOB,
  "f_ssoauth_code_response_error" TEXT,
  UNIQUE ("f_ssoauth_sso_state")
);

CREATE TABLE "tbl_auth_ssouser" (
  "rid_auth_ssouser" INTEGER PRIMARY KEY,
  "f_ssouser_created_at" INTEGER NOT NULL,
  "f_ssouser_updated_at" INTEGER,
  "f_ssouser_sso_identifier" TEXT NOT NULL,
  "ref_ssouser_owner" INTEGER NOT NULL,
  UNIQUE ("f_ssouser_sso_identifier"),
  FOREIGN KEY ("ref_ssouser_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_auth_twofactor" (
  "rid_auth_twofactor" INTEGER PRIMARY KEY,
  "f_twofactor_atype" INTEGER NOT NULL,
  "f_twofactor_twofactor_enabled" INTEGER NOT NULL,
  "f_twofactor_twofactor_data" BLOB NOT NULL,
  "f_twofactor_last_used" INTEGER NOT NULL DEFAULT 0,
  "ref_twofactor_owner" INTEGER NOT NULL,
  FOREIGN KEY ("ref_twofactor_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_auth_twofactorduo" (
  "rid_auth_twofactorduo" INTEGER PRIMARY KEY,
  "f_twofactorduo_duo_state" TEXT NOT NULL,
  "f_twofactorduo_email" TEXT NOT NULL,
  "f_twofactorduo_duo_nonce" TEXT NOT NULL,
  "f_twofactorduo_duo_exp" INTEGER NOT NULL,
  UNIQUE ("f_twofactorduo_duo_state")
);

CREATE TABLE "tbl_auth_twofactorincomplete" (
  "rid_auth_twofactorincomplete" INTEGER PRIMARY KEY,
  "f_twofactorincomplete_device_uuid" TEXT NOT NULL,
  "f_twofactorincomplete_device_name" TEXT NOT NULL,
  "f_twofactorincomplete_login_time" INTEGER NOT NULL,
  "f_twofactorincomplete_ip_address" TEXT NOT NULL,
  "f_twofactorincomplete_device_type" INTEGER NOT NULL DEFAULT 14,
  "ref_twofactorincomplete_owner" INTEGER NOT NULL,
  UNIQUE ("f_twofactorincomplete_device_uuid"),
  FOREIGN KEY ("ref_twofactorincomplete_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_events_auditevent" (
  "rid_events_auditevent" INTEGER PRIMARY KEY,
  "f_auditevent_event_type" INTEGER NOT NULL,
  "f_auditevent_device_type" INTEGER,
  "f_auditevent_ip_address" TEXT,
  "f_auditevent_event_date" INTEGER NOT NULL,
  "f_auditevent_provider_uuid" TEXT,
  "f_auditevent_provider_user_uuid" TEXT,
  "f_auditevent_provider_org_uuid" TEXT,
  "ref_auditevent_user" INTEGER,
  "ref_auditevent_org" INTEGER,
  "ref_auditevent_cipher" INTEGER,
  "ref_auditevent_collection" INTEGER,
  "ref_auditevent_group" INTEGER,
  "ref_auditevent_membership" INTEGER,
  "ref_auditevent_actor" INTEGER,
  "ref_auditevent_policy" INTEGER,
  FOREIGN KEY ("ref_auditevent_user") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_collection") REFERENCES "tbl_orgs_collection"("rid_orgs_collection") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_group") REFERENCES "tbl_orgs_group"("rid_orgs_group") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_membership") REFERENCES "tbl_orgs_usersorganizations"("rid_orgs_usersorganizations") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_actor") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL,
  FOREIGN KEY ("ref_auditevent_policy") REFERENCES "tbl_orgs_orgpolicy"("rid_orgs_orgpolicy") ON DELETE SET NULL
);

CREATE TABLE "tbl_orgs_cipherscollections" (
  "rid_orgs_cipherscollections" INTEGER PRIMARY KEY,
  "ref_cipherscollections_cipher" INTEGER NOT NULL,
  "ref_cipherscollections_collection" INTEGER NOT NULL,
  FOREIGN KEY ("ref_cipherscollections_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE CASCADE,
  FOREIGN KEY ("ref_cipherscollections_collection") REFERENCES "tbl_orgs_collection"("rid_orgs_collection") ON DELETE CASCADE
);

CREATE TABLE "tbl_orgs_collection" (
  "rid_orgs_collection" INTEGER PRIMARY KEY,
  "f_collection_collection_name" BLOB NOT NULL,
  "f_collection_external_id" TEXT,
  "ref_collection_org" INTEGER NOT NULL,
  FOREIGN KEY ("ref_collection_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE RESTRICT
);

CREATE TABLE "tbl_orgs_collectionsgroups" (
  "rid_orgs_collectionsgroups" INTEGER PRIMARY KEY,
  "f_collectionsgroups_read_only" INTEGER NOT NULL,
  "f_collectionsgroups_hide_passwords" INTEGER NOT NULL,
  "f_collectionsgroups_manage" INTEGER NOT NULL DEFAULT 0,
  "ref_collectionsgroups_collection" INTEGER NOT NULL,
  "ref_collectionsgroups_group" INTEGER NOT NULL,
  FOREIGN KEY ("ref_collectionsgroups_collection") REFERENCES "tbl_orgs_collection"("rid_orgs_collection") ON DELETE CASCADE,
  FOREIGN KEY ("ref_collectionsgroups_group") REFERENCES "tbl_orgs_group"("rid_orgs_group") ON DELETE CASCADE
);

CREATE TABLE "tbl_orgs_group" (
  "rid_orgs_group" INTEGER PRIMARY KEY,
  "f_group_group_name" TEXT NOT NULL,
  "f_group_access_all" INTEGER NOT NULL,
  "f_group_external_id" TEXT,
  "f_group_created_at" INTEGER NOT NULL,
  "f_group_revision_date" INTEGER NOT NULL,
  "ref_group_org" INTEGER NOT NULL,
  FOREIGN KEY ("ref_group_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE RESTRICT
);

CREATE TABLE "tbl_orgs_groupsusers" (
  "rid_orgs_groupsusers" INTEGER PRIMARY KEY,
  "ref_groupsusers_group" INTEGER NOT NULL,
  "ref_groupsusers_membership" INTEGER NOT NULL,
  FOREIGN KEY ("ref_groupsusers_group") REFERENCES "tbl_orgs_group"("rid_orgs_group") ON DELETE CASCADE,
  FOREIGN KEY ("ref_groupsusers_membership") REFERENCES "tbl_orgs_usersorganizations"("rid_orgs_usersorganizations") ON DELETE CASCADE
);

CREATE TABLE "tbl_orgs_orgpolicy" (
  "rid_orgs_orgpolicy" INTEGER PRIMARY KEY,
  "f_orgpolicy_atype" INTEGER NOT NULL,
  "f_orgpolicy_policy_enabled" INTEGER NOT NULL,
  "f_orgpolicy_policy_data" BLOB NOT NULL,
  "ref_orgpolicy_org" INTEGER NOT NULL,
  FOREIGN KEY ("ref_orgpolicy_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE RESTRICT
);

CREATE TABLE "tbl_orgs_organizationapikey" (
  "rid_orgs_organizationapikey" INTEGER PRIMARY KEY,
  "f_organizationapikey_atype" INTEGER NOT NULL,
  "f_organizationapikey_org_api_key" BLOB NOT NULL,
  "f_organizationapikey_revision_date" INTEGER NOT NULL,
  "ref_organizationapikey_org" INTEGER NOT NULL,
  FOREIGN KEY ("ref_organizationapikey_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE RESTRICT
);

CREATE TABLE "tbl_orgs_userscollections" (
  "rid_orgs_userscollections" INTEGER PRIMARY KEY,
  "f_userscollections_read_only" INTEGER NOT NULL DEFAULT 0,
  "f_userscollections_hide_passwords" INTEGER NOT NULL DEFAULT 0,
  "f_userscollections_manage" INTEGER NOT NULL DEFAULT 0,
  "ref_userscollections_member" INTEGER NOT NULL,
  "ref_userscollections_collection" INTEGER NOT NULL,
  FOREIGN KEY ("ref_userscollections_member") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_userscollections_collection") REFERENCES "tbl_orgs_collection"("rid_orgs_collection") ON DELETE CASCADE
);

CREATE TABLE "tbl_orgs_usersorganizations" (
  "rid_orgs_usersorganizations" INTEGER PRIMARY KEY,
  "f_usersorganizations_access_all" INTEGER NOT NULL,
  "f_usersorganizations_membership_key" BLOB NOT NULL,
  "f_usersorganizations_membership_status" INTEGER NOT NULL,
  "f_usersorganizations_membership_type" INTEGER NOT NULL,
  "f_usersorganizations_reset_password_key" BLOB,
  "f_usersorganizations_external_id" TEXT,
  "f_usersorganizations_invited_by_email" TEXT,
  "ref_usersorganizations_member" INTEGER NOT NULL,
  "ref_usersorganizations_org" INTEGER NOT NULL,
  FOREIGN KEY ("ref_usersorganizations_member") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_usersorganizations_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE CASCADE
);

CREATE TABLE "tbl_people_organization" (
  "rid_people_organization" INTEGER PRIMARY KEY,
  "f_organization_display_name" TEXT NOT NULL,
  "f_organization_billing_email" TEXT NOT NULL,
  "f_organization_org_private_key" BLOB,
  "f_organization_org_public_key" BLOB
);

CREATE TABLE "tbl_people_user" (
  "rid_people_user" INTEGER PRIMARY KEY,
  "f_user_created_at" INTEGER NOT NULL,
  "f_user_updated_at" INTEGER,
  "f_user_email" TEXT NOT NULL,
  "f_user_display_name" TEXT NOT NULL,
  "f_user_password_hash" BLOB NOT NULL,
  "f_user_password_salt" BLOB NOT NULL,
  "f_user_password_iterations" INTEGER NOT NULL,
  "f_user_password_hint" TEXT,
  "f_user_akey" BLOB NOT NULL,
  "f_user_private_key" BLOB,
  "f_user_public_key" BLOB,
  "f_user_totp_secret" BLOB,
  "f_user_totp_recover" TEXT,
  "f_user_security_stamp" TEXT NOT NULL,
  "f_user_equivalent_domains" BLOB NOT NULL,
  "f_user_excluded_globals" BLOB NOT NULL,
  "f_user_client_kdf_type" INTEGER NOT NULL DEFAULT 0,
  "f_user_client_kdf_iter" INTEGER NOT NULL DEFAULT 100000,
  "f_user_client_kdf_memory" INTEGER,
  "f_user_client_kdf_parallelism" INTEGER,
  "f_user_verified_at" INTEGER,
  "f_user_last_verifying_at" INTEGER,
  "f_user_login_verify_count" INTEGER NOT NULL DEFAULT 0,
  "f_user_email_new" TEXT,
  "f_user_email_new_token" TEXT,
  "f_user_enabled" INTEGER NOT NULL DEFAULT 1,
  "f_user_stamp_exception" BLOB,
  "f_user_api_key" BLOB,
  "f_user_avatar_color" TEXT,
  "f_user_external_id" TEXT,
  UNIQUE ("f_user_email")
);

CREATE TABLE "tbl_vault_archive" (
  "rid_vault_archive" INTEGER PRIMARY KEY,
  "f_archive_archived_at" INTEGER NOT NULL,
  "ref_archive_owner" INTEGER NOT NULL,
  "ref_archive_cipher" INTEGER NOT NULL,
  FOREIGN KEY ("ref_archive_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_archive_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE CASCADE
);

CREATE TABLE "tbl_vault_attachment" (
  "rid_vault_attachment" INTEGER PRIMARY KEY,
  "f_attachment_file_name" BLOB NOT NULL,
  "f_attachment_file_size" INTEGER NOT NULL,
  "f_attachment_attachment_key" BLOB,
  "ref_attachment_cipher" INTEGER NOT NULL,
  FOREIGN KEY ("ref_attachment_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE CASCADE
);

CREATE TABLE "tbl_vault_cipher" (
  "rid_vault_cipher" INTEGER PRIMARY KEY,
  "f_cipher_created_at" INTEGER NOT NULL,
  "f_cipher_updated_at" INTEGER,
  "f_cipher_atype" INTEGER NOT NULL,
  "f_cipher_cipher_name" BLOB NOT NULL,
  "f_cipher_notes" BLOB,
  "f_cipher_fields" BLOB,
  "f_cipher_cipher_data" BLOB NOT NULL,
  "f_cipher_password_history" BLOB,
  "f_cipher_deleted_at" INTEGER,
  "f_cipher_reprompt" INTEGER,
  "f_cipher_cipher_key" BLOB,
  "ref_cipher_owner" INTEGER,
  "ref_cipher_org" INTEGER,
  FOREIGN KEY ("ref_cipher_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL,
  FOREIGN KEY ("ref_cipher_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE SET NULL
);

CREATE TABLE "tbl_vault_favorite" (
  "rid_vault_favorite" INTEGER PRIMARY KEY,
  "ref_favorite_owner" INTEGER NOT NULL,
  "ref_favorite_cipher" INTEGER NOT NULL,
  FOREIGN KEY ("ref_favorite_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE CASCADE,
  FOREIGN KEY ("ref_favorite_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE CASCADE
);

CREATE TABLE "tbl_vault_folder" (
  "rid_vault_folder" INTEGER PRIMARY KEY,
  "f_folder_created_at" INTEGER NOT NULL,
  "f_folder_updated_at" INTEGER,
  "f_folder_folder_name" BLOB NOT NULL,
  "ref_folder_owner" INTEGER NOT NULL,
  FOREIGN KEY ("ref_folder_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE RESTRICT
);

CREATE TABLE "tbl_vault_foldersciphers" (
  "rid_vault_foldersciphers" INTEGER PRIMARY KEY,
  "ref_foldersciphers_cipher" INTEGER NOT NULL,
  "ref_foldersciphers_folder" INTEGER NOT NULL,
  FOREIGN KEY ("ref_foldersciphers_cipher") REFERENCES "tbl_vault_cipher"("rid_vault_cipher") ON DELETE CASCADE,
  FOREIGN KEY ("ref_foldersciphers_folder") REFERENCES "tbl_vault_folder"("rid_vault_folder") ON DELETE CASCADE
);

CREATE TABLE "tbl_vault_send" (
  "rid_vault_send" INTEGER PRIMARY KEY,
  "f_send_created_at" INTEGER NOT NULL,
  "f_send_updated_at" INTEGER,
  "f_send_send_name" BLOB NOT NULL,
  "f_send_send_notes" BLOB,
  "f_send_atype" INTEGER NOT NULL,
  "f_send_send_data" BLOB NOT NULL,
  "f_send_send_key" BLOB NOT NULL,
  "f_send_send_password_hash" BLOB,
  "f_send_send_password_salt" BLOB,
  "f_send_send_password_iter" INTEGER,
  "f_send_max_access_count" INTEGER,
  "f_send_access_count" INTEGER NOT NULL DEFAULT 0,
  "f_send_expiration_date" INTEGER,
  "f_send_deletion_date" INTEGER NOT NULL,
  "f_send_disabled" INTEGER NOT NULL DEFAULT 0,
  "f_send_hide_email" INTEGER,
  "ref_send_owner" INTEGER,
  "ref_send_org" INTEGER,
  FOREIGN KEY ("ref_send_owner") REFERENCES "tbl_people_user"("rid_people_user") ON DELETE SET NULL,
  FOREIGN KEY ("ref_send_org") REFERENCES "tbl_people_organization"("rid_people_organization") ON DELETE SET NULL
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
