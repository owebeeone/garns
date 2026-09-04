# Generated Garns surface for clients.all_clients_for_audit (query); the SQL is the lowered plan, unchanged.
READ = 'clients.all_clients_for_audit'
NOUN = 'query'
SQL = 'SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name", s0."f_client_archived_at" AS "archived_at", j1."f_user_email" AS "owner.email" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" ORDER BY s0."f_client_preferred_name" ASC, s0."rid_clients_client" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('preferred_name', 'archived_at', 'owner.email')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
