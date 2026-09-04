# Generated Garns surface for vault.unexpired_sends (query); the SQL is the lowered plan, unchanged.
READ = 'vault.unexpired_sends'
NOUN = 'query'
SQL = 'SELECT s0."rid_vault_send" AS "$k0", s0."f_send_send_name" AS "send_name", s0."f_send_expiration_date" AS "expiration_date", s0."f_send_deletion_date" AS "deletion_date" FROM "tbl_vault_send" AS s0 WHERE ((s0."f_send_disabled" = 0) AND (s0."f_send_deletion_date" > :_clock) AND ((s0."f_send_expiration_date" IS NULL) OR (s0."f_send_expiration_date" > :_clock))) ORDER BY s0."f_send_deletion_date" ASC, s0."rid_vault_send" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('send_name', 'expiration_date', 'deletion_date')
SCOPED = False
USES_CLOCK = True
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
