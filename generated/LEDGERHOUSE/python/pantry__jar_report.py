# Generated Garns surface for pantry.jar_report (query); the SQL is the lowered plan, unchanged.
READ = 'pantry.jar_report'
NOUN = 'query'
SQL = 'SELECT s0."cond" AS "$k0", s0."cond" AS "state", SUM(s0."mass_g") AS "total_grams", ROUND(AVG(s0."mass_g"), 1) AS "mean_grams" FROM "jar" AS s0 WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) AND (s0."mass_g" >= :floor) GROUP BY s0."cond" HAVING (SUM(s0."mass_g") > :floor) ORDER BY SUM(s0."mass_g") DESC, s0."cond" ASC'
PARAMS = ('floor',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('state', 'total_grams', 'mean_grams')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
