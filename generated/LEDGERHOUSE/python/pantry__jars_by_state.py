# Generated Garns surface for pantry.jars_by_state (question); the SQL is the lowered plan, unchanged.
READ = 'pantry.jars_by_state'
NOUN = 'question'
SQL = 'SELECT s0."cond" AS "$k0", s0."cond" AS "state", COUNT(*) AS "count" FROM "jar" AS s0 WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) GROUP BY s0."cond" ORDER BY s0."cond" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('state', 'count')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
