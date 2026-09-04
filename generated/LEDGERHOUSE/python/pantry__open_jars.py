# Generated Garns surface for pantry.open_jars (question); the SQL is the lowered plan, unchanged.
READ = 'pantry.open_jars'
NOUN = 'question'
SQL = 'SELECT s0."jar_no" AS "$k0", s0."lbl" AS "jar_label", s0."mass_g" AS "grams", j2."label_txt" AS "shelf" FROM "jar" AS s0 LEFT JOIN "shelf" AS j2 ON j2."shelf_no" = s0."on_shelf" WHERE s0."on_shelf" IN (SELECT p1."shelf_no" FROM "shelf" AS p1 WHERE p1."kept_by" = :_scope) AND (s0."cond" = \'open\') ORDER BY s0."mass_g" DESC, s0."jar_no" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('jar_label', 'grams', 'shelf')
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
