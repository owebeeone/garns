# Generated Garns surface for notes.client_card (query); the SQL is the lowered plan, unchanged.
READ = 'notes.client_card'
NOUN = 'query'
SQL = 'SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name", s0."f_client_archived_at" AS "archived_at", j1."f_user_email" AS "owner.email" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" WHERE s0."ref_client_owner" = :_scope AND s0."rid_clients_client" = :client ORDER BY s0."rid_clients_client" ASC LIMIT 1'
PARAMS = ('client',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('preferred_name', 'archived_at', 'owner.email', 'contacts', 'notes')
SCOPED = True
USES_CLOCK = False
CHILDREN = {
    'contacts': 'SELECT n2."ref_contact_client" AS "$parent", n2."rid_clients_contact" AS "$k0", n2."f_contact_preferred_name" AS "preferred_name", n2."f_contact_email" AS "email", n2."f_contact_relationship" AS "relationship" FROM "tbl_clients_contact" AS n2 WHERE n2."ref_contact_client" IN (SELECT value FROM json_each(:_parents)) ORDER BY n2."ref_contact_client" ASC, n2."f_contact_created_at" ASC, n2."f_contact_preferred_name" ASC, n2."rid_clients_contact" ASC',
    'notes': 'SELECT "$parent", "$k0", "note_body", "recorded_at" FROM (SELECT n3."ref_note_client" AS "$parent", n3."rid_notes_note" AS "$k0", n3."f_note_note_body" AS "note_body", n3."f_note_recorded_at" AS "recorded_at", ROW_NUMBER() OVER (PARTITION BY n3."ref_note_client" ORDER BY n3."f_note_recorded_at" DESC, n3."rid_notes_note" DESC) AS "$rn" FROM "tbl_notes_note" AS n3 WHERE n3."ref_note_client" IN (SELECT value FROM json_each(:_parents))) WHERE "$rn" <= 5 ORDER BY "$parent" ASC, "$rn" DESC',
}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
