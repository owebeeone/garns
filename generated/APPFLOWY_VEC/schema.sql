CREATE TABLE "tbl_embeddings_collabembedding" (
  "rid_embeddings_collabembedding" INTEGER PRIMARY KEY,
  "f_collabembedding_object_oid" TEXT NOT NULL,
  "f_collabembedding_fragment_oid" TEXT NOT NULL,
  "f_collabembedding_content_type" INTEGER NOT NULL,
  "f_collabembedding_content" TEXT NOT NULL,
  "f_collabembedding_embedding_metadata" TEXT,
  "f_collabembedding_fragment_index" INTEGER NOT NULL DEFAULT 0,
  "f_collabembedding_embedder_type" INTEGER NOT NULL DEFAULT 0,
  "f_collabembedding_embedding" BLOB NOT NULL,
  "ref_collabembedding_workspace" INTEGER NOT NULL,
  UNIQUE ("f_collabembedding_object_oid", "f_collabembedding_fragment_oid")
);

CREATE TABLE "tbl_embeddings_pendingindex" (
  "rid_embeddings_pendingindex" INTEGER PRIMARY KEY,
  "f_pendingindex_object_oid" TEXT NOT NULL,
  "f_pendingindex_content" TEXT NOT NULL,
  "f_pendingindex_collab_type" INTEGER NOT NULL,
  "f_pendingindex_updated_at" INTEGER NOT NULL,
  "f_pendingindex_indexed_at" INTEGER,
  "ref_pendingindex_workspace" INTEGER NOT NULL,
  UNIQUE ("f_pendingindex_object_oid")
);

CREATE TABLE "tbl_embeddings_workspace" (
  "rid_embeddings_workspace" INTEGER PRIMARY KEY,
  "f_workspace_workspace_oid" TEXT NOT NULL,
  UNIQUE ("f_workspace_workspace_oid")
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
