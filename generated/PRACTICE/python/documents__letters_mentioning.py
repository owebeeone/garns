# Generated Garns surface for documents.letters_mentioning (query); the SQL is the lowered plan, unchanged.
READ = 'documents.letters_mentioning'
NOUN = 'query'
SQL = 'SELECT s0."rid_documents_document" AS "$k0", s0."f_document_title" AS "title", s0."f_letter_body" AS "body" FROM "tbl_documents_document" AS s0 WHERE s0."member_of_documents_document" = \'Letter\' AND s0."f_document_archived_at" IS NULL AND s0."ref_document_owner" = :_scope AND (instr(s0."f_letter_body", :q) > 0) ORDER BY s0."rid_documents_document" ASC'
PARAMS = ('q',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('title', 'body')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
