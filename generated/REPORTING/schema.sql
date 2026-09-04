CREATE TABLE "ta_a841ea5a67" (
  "id_56e790d195" INTEGER PRIMARY KEY,
  "co_1672fa0252" TEXT NOT NULL,
  "co_01dbbfc0f1" TEXT NOT NULL,
  UNIQUE ("co_1672fa0252")
);

CREATE TABLE "ta_342006d009" (
  "id_dea8a7c8d9" INTEGER PRIMARY KEY,
  "co_95da97f99a" TEXT NOT NULL,
  "co_ba8dae4721" REAL NOT NULL,
  "co_13dd0e180e" INTEGER NOT NULL,
  "li_c21e9feb86" INTEGER NOT NULL,
  UNIQUE ("co_95da97f99a")
);

CREATE TABLE "en_5bf68daea4" (
  ordinal INTEGER PRIMARY KEY,
  ir_digest TEXT NOT NULL,
  storage_digest TEXT NOT NULL,
  shipped_at_revision INTEGER NOT NULL
);

CREATE TABLE "en_08f62a4c16" (
  revision INTEGER PRIMARY KEY,
  writer TEXT NOT NULL,
  transaction_id TEXT NOT NULL
);

CREATE TABLE "en_f59db8c5a7" (
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
