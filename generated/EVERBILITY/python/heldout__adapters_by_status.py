# Generated Garns surface for heldout.adapters_by_status (query); the SQL is the lowered plan, unchanged.
READ = 'heldout.adapters_by_status'
NOUN = 'query'
SQL = 'SELECT s0."rid_pms_pmsadapter" AS "$k0", s0."f_pmsadapter_pms_id" AS "pms_id", s0."f_pmsadapter_adapter_status" AS "adapter_status", s0."f_pmsadapter_is_development" AS "is_development", s0."f_pmsadapter_enabled" AS "enabled" FROM "tbl_pms_pmsadapter" AS s0 WHERE (s0."f_pmsadapter_adapter_status" = :status) ORDER BY s0."rid_pms_pmsadapter" ASC'
PARAMS = ('status',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('pms_id', 'adapter_status', 'is_development', 'enabled')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
