CREATE TABLE "tbl_ai_localaimodel" (
  "rid_ai_localaimodel" INTEGER PRIMARY KEY,
  "f_localaimodel_model_name" TEXT NOT NULL,
  "f_localaimodel_model_type" INTEGER NOT NULL,
  UNIQUE ("f_localaimodel_model_name")
);

CREATE TABLE "tbl_chat_chat" (
  "rid_chat_chat" INTEGER PRIMARY KEY,
  "f_chat_chat_oid" TEXT NOT NULL,
  "f_chat_created_at" INTEGER NOT NULL,
  "f_chat_chat_metadata" TEXT NOT NULL DEFAULT '',
  "f_chat_rag_ids" TEXT,
  "f_chat_is_sync" INTEGER NOT NULL DEFAULT 1,
  "f_chat_summary" TEXT NOT NULL DEFAULT '',
  UNIQUE ("f_chat_chat_oid")
);

CREATE TABLE "tbl_chat_chatlocalsetting" (
  "rid_chat_chatlocalsetting" INTEGER PRIMARY KEY,
  "f_chatlocalsetting_local_model_path" TEXT NOT NULL,
  "f_chatlocalsetting_local_model_name" TEXT NOT NULL DEFAULT '',
  "ref_chatlocalsetting_chat" INTEGER NOT NULL,
  UNIQUE ("ref_chatlocalsetting_chat")
);

CREATE TABLE "tbl_chat_chatmessage" (
  "rid_chat_chatmessage" INTEGER PRIMARY KEY,
  "f_chatmessage_message_oid" INTEGER NOT NULL,
  "f_chatmessage_content" TEXT NOT NULL,
  "f_chatmessage_created_at" INTEGER NOT NULL,
  "f_chatmessage_author_type" INTEGER NOT NULL,
  "f_chatmessage_author_id" TEXT NOT NULL,
  "f_chatmessage_reply_message_id" INTEGER,
  "f_chatmessage_message_metadata" TEXT,
  "f_chatmessage_is_sync" INTEGER NOT NULL DEFAULT 1,
  "ref_chatmessage_chat" INTEGER NOT NULL,
  UNIQUE ("f_chatmessage_message_oid")
);

CREATE TABLE "tbl_collab_collabmetadata" (
  "rid_collab_collabmetadata" INTEGER PRIMARY KEY,
  "f_collabmetadata_object_oid" TEXT NOT NULL,
  "f_collabmetadata_updated_at" INTEGER NOT NULL,
  "f_collabmetadata_prev_sync_state_vector" BLOB NOT NULL,
  "f_collabmetadata_collab_type" INTEGER NOT NULL,
  UNIQUE ("f_collabmetadata_object_oid")
);

CREATE TABLE "tbl_collab_collabsnapshot" (
  "rid_collab_collabsnapshot" INTEGER PRIMARY KEY,
  "f_collabsnapshot_object_oid" TEXT NOT NULL,
  "f_collabsnapshot_title" TEXT NOT NULL DEFAULT '',
  "f_collabsnapshot_snapshot_desc" TEXT NOT NULL DEFAULT '',
  "f_collabsnapshot_collab_type_text" TEXT NOT NULL DEFAULT '',
  "f_collabsnapshot_snapshot_at" INTEGER NOT NULL DEFAULT 0,
  "f_collabsnapshot_snapshot_data" BLOB NOT NULL
);

CREATE TABLE "tbl_collab_indexcollabrecord" (
  "rid_collab_indexcollabrecord" INTEGER PRIMARY KEY,
  "f_indexcollabrecord_object_oid" TEXT NOT NULL,
  "f_indexcollabrecord_content_hash" TEXT NOT NULL,
  "ref_indexcollabrecord_workspace" INTEGER NOT NULL,
  UNIQUE ("f_indexcollabrecord_object_oid")
);

CREATE TABLE "tbl_migrate_userdatamigrationrecord" (
  "rid_migrate_userdatamigrationrecord" INTEGER PRIMARY KEY,
  "f_userdatamigrationrecord_migration_name" TEXT NOT NULL,
  "f_userdatamigrationrecord_executed_at" INTEGER NOT NULL,
  UNIQUE ("f_userdatamigrationrecord_migration_name")
);

CREATE TABLE "tbl_traits_user" (
  "rid_traits_user" INTEGER PRIMARY KEY,
  "f_user_user_oid" TEXT NOT NULL,
  "f_user_display_name" TEXT NOT NULL DEFAULT '',
  "f_user_icon_url" TEXT NOT NULL DEFAULT '',
  "f_user_token" TEXT NOT NULL DEFAULT '',
  "f_user_email" TEXT NOT NULL DEFAULT '',
  "f_user_auth_type" INTEGER NOT NULL DEFAULT 0,
  "f_user_updated_at" INTEGER NOT NULL DEFAULT 0,
  UNIQUE ("f_user_user_oid")
);

CREATE TABLE "tbl_uploads_uploadfile" (
  "rid_uploads_uploadfile" INTEGER PRIMARY KEY,
  "f_uploadfile_file_oid" TEXT NOT NULL,
  "f_uploadfile_parent_dir" TEXT NOT NULL,
  "f_uploadfile_local_file_path" TEXT NOT NULL,
  "f_uploadfile_content_type" TEXT NOT NULL,
  "f_uploadfile_chunk_size" INTEGER NOT NULL,
  "f_uploadfile_num_chunk" INTEGER NOT NULL,
  "f_uploadfile_upload_oid" TEXT NOT NULL DEFAULT '',
  "f_uploadfile_created_at" INTEGER NOT NULL,
  "f_uploadfile_is_finish" INTEGER NOT NULL DEFAULT 0,
  "ref_uploadfile_workspace" INTEGER NOT NULL,
  UNIQUE ("f_uploadfile_file_oid", "f_uploadfile_parent_dir", "ref_uploadfile_workspace")
);

CREATE TABLE "tbl_uploads_uploadpart" (
  "rid_uploads_uploadpart" INTEGER PRIMARY KEY,
  "f_uploadpart_e_tag" TEXT NOT NULL,
  "f_uploadpart_part_num" INTEGER NOT NULL,
  "ref_uploadpart_upload" INTEGER NOT NULL,
  UNIQUE ("f_uploadpart_e_tag")
);

CREATE TABLE "tbl_workspaces_shareduser" (
  "rid_workspaces_shareduser" INTEGER PRIMARY KEY,
  "f_shareduser_view_oid" TEXT NOT NULL,
  "f_shareduser_email" TEXT NOT NULL,
  "f_shareduser_display_name" TEXT NOT NULL,
  "f_shareduser_avatar_url" TEXT NOT NULL DEFAULT '',
  "f_shareduser_role" INTEGER NOT NULL,
  "f_shareduser_access_level" INTEGER NOT NULL,
  "f_shareduser_sort_order" INTEGER NOT NULL DEFAULT 0,
  "ref_shareduser_workspace" INTEGER NOT NULL,
  UNIQUE ("f_shareduser_view_oid", "f_shareduser_email", "ref_shareduser_workspace")
);

CREATE TABLE "tbl_workspaces_sharedview" (
  "rid_workspaces_sharedview" INTEGER PRIMARY KEY,
  "f_sharedview_uid" INTEGER NOT NULL,
  "f_sharedview_view_oid" TEXT NOT NULL,
  "f_sharedview_permission_id" INTEGER NOT NULL,
  "f_sharedview_created_at" INTEGER,
  "ref_sharedview_workspace" INTEGER NOT NULL,
  UNIQUE ("f_sharedview_uid", "f_sharedview_view_oid", "ref_sharedview_workspace")
);

CREATE TABLE "tbl_workspaces_userworkspace" (
  "rid_workspaces_userworkspace" INTEGER PRIMARY KEY,
  "f_userworkspace_workspace_oid" TEXT NOT NULL,
  "f_userworkspace_display_name" TEXT NOT NULL,
  "f_userworkspace_uid" INTEGER NOT NULL,
  "f_userworkspace_created_at" INTEGER NOT NULL DEFAULT 0,
  "f_userworkspace_database_storage_id" TEXT NOT NULL,
  "f_userworkspace_icon" TEXT NOT NULL DEFAULT '',
  "f_userworkspace_member_count" INTEGER NOT NULL DEFAULT 1,
  "f_userworkspace_role" INTEGER,
  "f_userworkspace_workspace_type" INTEGER NOT NULL DEFAULT 1,
  UNIQUE ("f_userworkspace_workspace_oid")
);

CREATE TABLE "tbl_workspaces_workspacemember" (
  "rid_workspaces_workspacemember" INTEGER PRIMARY KEY,
  "f_workspacemember_email" TEXT NOT NULL,
  "f_workspacemember_role" INTEGER NOT NULL,
  "f_workspacemember_display_name" TEXT NOT NULL,
  "f_workspacemember_avatar_url" TEXT,
  "f_workspacemember_uid" INTEGER NOT NULL,
  "f_workspacemember_updated_at" INTEGER NOT NULL,
  "f_workspacemember_joined_at" INTEGER,
  "ref_workspacemember_workspace" INTEGER NOT NULL,
  UNIQUE ("f_workspacemember_email", "ref_workspacemember_workspace")
);

CREATE TABLE "tbl_workspaces_workspacesetting" (
  "rid_workspaces_workspacesetting" INTEGER PRIMARY KEY,
  "f_workspacesetting_disable_search_indexing" INTEGER NOT NULL DEFAULT 0,
  "f_workspacesetting_ai_model" TEXT NOT NULL DEFAULT '',
  "ref_workspacesetting_workspace" INTEGER NOT NULL,
  UNIQUE ("ref_workspacesetting_workspace")
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
