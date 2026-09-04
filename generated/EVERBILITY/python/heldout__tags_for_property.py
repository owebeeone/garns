# Generated Garns surface for heldout.tags_for_property (query); the SQL is the lowered plan, unchanged.
READ = 'heldout.tags_for_property'
NOUN = 'query'
SQL = 'SELECT s0."rid_merge_mergetag" AS "$k0", s0."f_mergetag_created_at" AS "created_at", s0."f_mergetag_updated_at" AS "updated_at", s0."f_mergetag_property_id" AS "property_id", s0."f_mergetag_property_name" AS "property_name", s0."f_mergetag_can_delete" AS "can_delete" FROM "tbl_merge_mergetag" AS s0 WHERE s0."ref_mergetag_owner" = :_scope AND (s0."f_mergetag_property_id" = :property) ORDER BY s0."rid_merge_mergetag" ASC'
PARAMS = ('property',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('created_at', 'updated_at', 'property_id', 'property_name', 'can_delete')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
