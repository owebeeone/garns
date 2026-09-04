# Generated Garns surface for pantry.heavy_shelves (question); the SQL is the lowered plan, unchanged.
READ = 'pantry.heavy_shelves'
NOUN = 'question'
SQL = 'SELECT s0."shelf_no" AS "$k0", s0."label_txt" AS "shelf_label" FROM "shelf" AS s0 WHERE s0."kept_by" = :_scope AND EXISTS (SELECT 1 FROM "jar" AS j1 WHERE j1."on_shelf" = s0."shelf_no" AND (j1."mass_g" > 500)) ORDER BY s0."shelf_no" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('shelf_label',)
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
