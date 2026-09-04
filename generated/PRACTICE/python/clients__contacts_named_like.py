# Generated Garns surface for clients.contacts_named_like (query); the SQL is the lowered plan, unchanged.
READ = 'clients.contacts_named_like'
NOUN = 'query'
SQL = 'SELECT s0."rid_clients_contact" AS "$k0", s0."f_contact_preferred_name" AS "preferred_name", j2."f_client_preferred_name" AS "client.preferred_name" FROM "tbl_clients_contact" AS s0 LEFT JOIN "tbl_clients_client" AS j2 ON j2."rid_clients_client" = s0."ref_contact_client" WHERE s0."ref_contact_client" IN (SELECT p1."rid_clients_client" FROM "tbl_clients_client" AS p1 WHERE p1."ref_client_owner" = :_scope) AND (instr(j2."f_client_preferred_name", :q) > 0) ORDER BY s0."f_contact_preferred_name" ASC, s0."rid_clients_contact" ASC'
PARAMS = ('q',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('preferred_name', 'client.preferred_name')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
