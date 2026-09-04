# Generated Garns surface for sales_static.revenue_open_by_customer (query); the SQL is the lowered plan, unchanged.
READ = 'sales_static.revenue_open_by_customer'
NOUN = 'query'
SQL = 'SELECT j1."co_1e32478f5c" AS "$k0", j1."co_1e32478f5c" AS "customer", SUM(s0."co_26bff25d88") AS "revenue", COUNT(*) AS "orders", ROUND((CAST(SUM(s0."co_26bff25d88") AS REAL) / COUNT(*)), 2) AS "average_order" FROM "ta_8d09f00415" AS s0 LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7" WHERE ((s0."co_7cbde43f56" = \'open\') AND (s0."co_26bff25d88" >= :floor)) GROUP BY j1."co_1e32478f5c" HAVING (SUM(s0."co_26bff25d88") > :floor) ORDER BY SUM(s0."co_26bff25d88") DESC, LENGTH(j1."co_1e32478f5c") ASC, j1."co_1e32478f5c" ASC'
PARAMS = ('floor',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('customer', 'revenue', 'orders', 'average_order')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
