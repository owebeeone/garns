# Generated Garns surface for documents.client_documents (query); the SQL is the lowered plan, unchanged.
READ = 'documents.client_documents'
NOUN = 'query'
SQL = 'SELECT s0."rid_documents_document" AS "$k0", s0."f_document_title" AS "title", s0."member_of_documents_document" AS "kind", j1."f_client_preferred_name" AS "client.preferred_name" FROM "tbl_documents_document" AS s0 LEFT JOIN "tbl_clients_client" AS j1 ON j1."rid_clients_client" = s0."ref_document_client" WHERE s0."f_document_archived_at" IS NULL AND s0."ref_document_owner" = :_scope AND (s0."ref_document_client" = :client) ORDER BY s0."f_document_title" ASC, s0."rid_documents_document" ASC'
PARAMS = ('client',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('title', 'kind', 'client.preferred_name')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
