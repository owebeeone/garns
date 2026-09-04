# Generated Garns surface for notes.notes_in_window (query); the SQL is the lowered plan, unchanged.
READ = 'notes.notes_in_window'
NOUN = 'query'
SQL = 'SELECT s0."rid_notes_note" AS "$k0", s0."f_note_note_body" AS "note_body", s0."f_note_recorded_at" AS "recorded_at" FROM "tbl_notes_note" AS s0 WHERE s0."ref_note_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND ((s0."ref_note_client" = :client) AND (:from IS NULL OR (s0."f_note_recorded_at" >= :from)) AND (:until IS NULL OR (s0."f_note_recorded_at" < :until))) ORDER BY s0."f_note_recorded_at" ASC, s0."rid_notes_note" ASC'
PARAMS = ('client', 'from', 'until')
KEY_COLUMNS = ('$k0',)
COLUMNS = ('note_body', 'recorded_at')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
