CREATE TABLE "jar" (
  "jar_no" INTEGER PRIMARY KEY,
  "lbl" TEXT NOT NULL,
  "mass_g" INTEGER NOT NULL,
  "cond" TEXT NOT NULL,
  "on_shelf" INTEGER NOT NULL,
  CHECK ("cond" IN ('sealed', 'open', 'empty')),
  UNIQUE ("lbl"),
  FOREIGN KEY ("on_shelf") REFERENCES "shelf"("shelf_no") ON DELETE CASCADE
);

CREATE TABLE "shelf" (
  "shelf_no" INTEGER PRIMARY KEY,
  "label_txt" TEXT NOT NULL,
  "kept_by" INTEGER NOT NULL,
  UNIQUE ("label_txt"),
  FOREIGN KEY ("kept_by") REFERENCES "house"("house_no") ON DELETE RESTRICT
);

CREATE TABLE "house" (
  "house_no" INTEGER PRIMARY KEY,
  "code_txt" TEXT NOT NULL,
  "since" INTEGER,
  UNIQUE ("code_txt")
);

CREATE TABLE "lh_epochs" (
  ordinal INTEGER PRIMARY KEY,
  ir_digest TEXT NOT NULL,
  storage_digest TEXT NOT NULL,
  shipped_at_revision INTEGER NOT NULL
);

CREATE TABLE "lh_ticks" (
  revision INTEGER PRIMARY KEY,
  writer TEXT NOT NULL,
  transaction_id TEXT NOT NULL
);

CREATE TABLE "lh_journal" (
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

CREATE TABLE "jar_trail" (
  "trail_seq" INTEGER PRIMARY KEY AUTOINCREMENT,
  "verb" TEXT NOT NULL,
  "tick" INTEGER,
  "jar_ref" INTEGER NOT NULL,
  "lbl_v" TEXT,
  "mass_v" INTEGER,
  "cond_v" TEXT,
  "on_shelf_v" INTEGER
);

CREATE TRIGGER "jar_trail__insert" AFTER INSERT ON "jar"
BEGIN
  INSERT INTO "jar_trail" ("verb", "jar_ref", "lbl_v", "mass_v", "cond_v", "on_shelf_v") VALUES ('insert', NEW."jar_no", NEW."lbl", NEW."mass_g", NEW."cond", NEW."on_shelf");
END;

CREATE TRIGGER "jar_trail__update" AFTER UPDATE ON "jar"
BEGIN
  INSERT INTO "jar_trail" ("verb", "jar_ref", "lbl_v", "mass_v", "cond_v", "on_shelf_v") VALUES ('before', OLD."jar_no", OLD."lbl", OLD."mass_g", OLD."cond", OLD."on_shelf");
  INSERT INTO "jar_trail" ("verb", "jar_ref", "lbl_v", "mass_v", "cond_v", "on_shelf_v") VALUES ('update', NEW."jar_no", NEW."lbl", NEW."mass_g", NEW."cond", NEW."on_shelf");
END;

CREATE TRIGGER "jar_trail__delete" AFTER DELETE ON "jar"
BEGIN
  INSERT INTO "jar_trail" ("verb", "jar_ref", "lbl_v", "mass_v", "cond_v", "on_shelf_v") VALUES ('delete', OLD."jar_no", OLD."lbl", OLD."mass_g", OLD."cond", OLD."on_shelf");
END;

CREATE TABLE "shelf_trail" (
  "trail_seq" INTEGER PRIMARY KEY AUTOINCREMENT,
  "verb" TEXT NOT NULL,
  "tick" INTEGER,
  "shelf_ref" INTEGER NOT NULL,
  "label_v" TEXT,
  "kept_by_v" INTEGER
);

CREATE TRIGGER "shelf_trail__insert" AFTER INSERT ON "shelf"
BEGIN
  INSERT INTO "shelf_trail" ("verb", "shelf_ref", "label_v", "kept_by_v") VALUES ('insert', NEW."shelf_no", NEW."label_txt", NEW."kept_by");
END;

CREATE TRIGGER "shelf_trail__update" AFTER UPDATE ON "shelf"
BEGIN
  INSERT INTO "shelf_trail" ("verb", "shelf_ref", "label_v", "kept_by_v") VALUES ('before', OLD."shelf_no", OLD."label_txt", OLD."kept_by");
  INSERT INTO "shelf_trail" ("verb", "shelf_ref", "label_v", "kept_by_v") VALUES ('update', NEW."shelf_no", NEW."label_txt", NEW."kept_by");
END;

CREATE TRIGGER "shelf_trail__delete" AFTER DELETE ON "shelf"
BEGIN
  INSERT INTO "shelf_trail" ("verb", "shelf_ref", "label_v", "kept_by_v") VALUES ('delete', OLD."shelf_no", OLD."label_txt", OLD."kept_by");
END;

CREATE TABLE "house_trail" (
  "trail_seq" INTEGER PRIMARY KEY AUTOINCREMENT,
  "verb" TEXT NOT NULL,
  "tick" INTEGER,
  "house_ref" INTEGER NOT NULL,
  "code_txt_v" TEXT,
  "since_v" INTEGER
);

CREATE TRIGGER "house_trail__insert" AFTER INSERT ON "house"
BEGIN
  INSERT INTO "house_trail" ("verb", "house_ref", "code_txt_v", "since_v") VALUES ('insert', NEW."house_no", NEW."code_txt", NEW."since");
END;

CREATE TRIGGER "house_trail__update" AFTER UPDATE ON "house"
BEGIN
  INSERT INTO "house_trail" ("verb", "house_ref", "code_txt_v", "since_v") VALUES ('before', OLD."house_no", OLD."code_txt", OLD."since");
  INSERT INTO "house_trail" ("verb", "house_ref", "code_txt_v", "since_v") VALUES ('update', NEW."house_no", NEW."code_txt", NEW."since");
END;

CREATE TRIGGER "house_trail__delete" AFTER DELETE ON "house"
BEGIN
  INSERT INTO "house_trail" ("verb", "house_ref", "code_txt_v", "since_v") VALUES ('delete', OLD."house_no", OLD."code_txt", OLD."since");
END;
