# Generated Garns surface for reporting.revenue_by_customer (query); the SQL is the lowered plan, unchanged.
READ = 'reporting.revenue_by_customer'
NOUN = 'query'
SQL = 'SELECT j1."co_01dbbfc0f1" AS "$k0", j1."co_01dbbfc0f1" AS "customer", SUM(s0."co_ba8dae4721") AS "revenue", ROUND((CAST(SUM(s0."co_ba8dae4721") AS REAL) / COUNT(*)), 2) AS "average_invoice" FROM "ta_342006d009" AS s0 LEFT JOIN "ta_a841ea5a67" AS j1 ON j1."id_56e790d195" = s0."li_c21e9feb86" WHERE (s0."co_ba8dae4721" >= :floor) GROUP BY j1."co_01dbbfc0f1" HAVING (SUM(s0."co_ba8dae4721") > :floor) ORDER BY SUM(s0."co_ba8dae4721") DESC, j1."co_01dbbfc0f1" ASC'
PARAMS = ('floor',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('customer', 'revenue', 'average_invoice')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
