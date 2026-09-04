# Generated Garns surface for sales_static.distinct_open_customers (query); the SQL is the lowered plan, unchanged.
READ = 'sales_static.distinct_open_customers'
NOUN = 'query'
SQL = 'SELECT DISTINCT j1."co_1e32478f5c" AS "customer" FROM "ta_8d09f00415" AS s0 LEFT JOIN "ta_6e060cc01b" AS j1 ON j1."id_268d9db70b" = s0."li_a1a73c58a7" WHERE (s0."co_7cbde43f56" = \'open\') ORDER BY j1."co_1e32478f5c" ASC'
PARAMS = ()
KEY_COLUMNS = ('customer',)
COLUMNS = ('customer',)
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
