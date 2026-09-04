CREATE TABLE "ta_6e060cc01b" (
  "id_268d9db70b" INTEGER PRIMARY KEY,
  "co_7ed8c48383" TEXT NOT NULL,
  "co_1e32478f5c" TEXT NOT NULL,
  UNIQUE ("co_7ed8c48383")
);

CREATE TABLE "ta_8d09f00415" (
  "id_76d3517dac" INTEGER PRIMARY KEY,
  "co_c2bd8587a7" TEXT NOT NULL,
  "co_7cbde43f56" TEXT NOT NULL,
  "co_26bff25d88" REAL NOT NULL,
  "co_66617ed9a4" INTEGER NOT NULL,
  "li_a1a73c58a7" INTEGER NOT NULL,
  CHECK ("co_7cbde43f56" IN ('open', 'closed')),
  UNIQUE ("co_c2bd8587a7"),
  FOREIGN KEY ("li_a1a73c58a7") REFERENCES "ta_6e060cc01b"("id_268d9db70b") ON DELETE RESTRICT
);

CREATE TABLE "en_339a843a1d" (
  ordinal INTEGER PRIMARY KEY,
  ir_digest TEXT NOT NULL,
  storage_digest TEXT NOT NULL,
  shipped_at_revision INTEGER NOT NULL
);

CREATE TABLE "en_9b3975370b" (
  revision INTEGER PRIMARY KEY,
  writer TEXT NOT NULL,
  transaction_id TEXT NOT NULL
);

CREATE TABLE "en_f8bd8555fd" (
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
