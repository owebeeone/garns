# Generated Garns surface for heldout.org_pms_user_maps (query); the SQL is the lowered plan, unchanged.
READ = 'heldout.org_pms_user_maps'
NOUN = 'query'
SQL = 'SELECT s0."rid_pms_pmsusermap" AS "$k0", s0."f_pmsusermap_created_at" AS "created_at", s0."f_pmsusermap_updated_at" AS "updated_at", s0."f_pmsusermap_pms_user_id" AS "pms_user_id" FROM "tbl_pms_pmsusermap" AS s0 WHERE ((s0."ref_pmsusermap_org" = :org) AND (s0."ref_pmsusermap_adapter" = :adapter)) ORDER BY s0."rid_pms_pmsusermap" ASC'
PARAMS = ('adapter', 'org')
KEY_COLUMNS = ('$k0',)
COLUMNS = ('created_at', 'updated_at', 'pms_user_id')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
