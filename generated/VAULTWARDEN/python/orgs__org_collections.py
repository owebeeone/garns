# Generated Garns surface for orgs.org_collections (query); the SQL is the lowered plan, unchanged.
READ = 'orgs.org_collections'
NOUN = 'query'
SQL = 'SELECT s0."rid_orgs_collection" AS "$k0", s0."f_collection_collection_name" AS "collection_name", s0."f_collection_external_id" AS "external_id" FROM "tbl_orgs_collection" AS s0 WHERE (s0."ref_collection_org" = :org) ORDER BY s0."rid_orgs_collection" ASC'
PARAMS = ('org',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('collection_name', 'external_id')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
