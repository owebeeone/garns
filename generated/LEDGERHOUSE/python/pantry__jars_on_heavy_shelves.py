# Generated Garns surface for pantry.jars_on_heavy_shelves (question); the SQL is the lowered plan, unchanged.
READ = 'pantry.jars_on_heavy_shelves'
NOUN = 'question'
SQL = 'SELECT s0."jar_no" AS "$k0", s0."lbl" AS "jar_label" FROM "jar" AS s0 WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) AND (s0."on_shelf" IN (SELECT c2."shelf_no" FROM "shelf" AS c2 WHERE c2."kept_by" = :_scope AND EXISTS (SELECT 1 FROM "jar" AS j3 WHERE j3."on_shelf" = c2."shelf_no" AND (j3."mass_g" > 500)))) ORDER BY s0."jar_no" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('jar_label',)
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
