# Generated Garns surface for vault.opaque_present (query); the SQL is the lowered plan, unchanged.
READ = 'vault.opaque_present'
NOUN = 'query'
SQL = 'SELECT s0."rid_vault_cipher" AS "$k0", s0."f_cipher_atype" AS "atype" FROM "tbl_vault_cipher" AS s0 WHERE s0."f_cipher_deleted_at" IS NULL AND (s0."f_cipher_cipher_data" IS NOT NULL) ORDER BY s0."rid_vault_cipher" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('atype',)
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
