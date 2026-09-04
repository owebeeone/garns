# Generated Garns surface for clients.contacts_with_relationship (query); the SQL is the lowered plan, unchanged.
READ = 'clients.contacts_with_relationship'
NOUN = 'query'
SQL = 'SELECT s0."rid_clients_contact" AS "$k0", s0."f_contact_preferred_name" AS "preferred_name", s0."f_contact_relationship" AS "relationship" FROM "tbl_clients_contact" AS s0 WHERE s0."ref_contact_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND (s0."f_contact_relationship" = :kind) ORDER BY s0."rid_clients_contact" ASC'
PARAMS = ('kind',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('preferred_name', 'relationship')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
