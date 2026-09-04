# Generated Garns surface for heldout.aget_client_by_clerk_user_id (query); the SQL is the lowered plan, unchanged.
READ = 'heldout.aget_client_by_clerk_user_id'
NOUN = 'query'
SQL = 'SELECT s0."rid_clients_client" AS "$k0", s0."f_client_created_at" AS "created_at", s0."f_client_updated_at" AS "updated_at", s0."f_client_first_name" AS "first_name", s0."f_client_last_name" AS "last_name", s0."f_client_archived_at" AS "archived_at" FROM "tbl_clients_client" AS s0 LEFT JOIN "tbl_people_user" AS j1 ON j1."rid_people_user" = s0."ref_client_owner" WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND ((j1."f_user_clerk_user_id" = :clerk) AND (s0."f_client_archived_at" IS NULL)) ORDER BY s0."rid_clients_client" ASC'
PARAMS = ('clerk',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('created_at', 'updated_at', 'first_name', 'last_name', 'archived_at')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
