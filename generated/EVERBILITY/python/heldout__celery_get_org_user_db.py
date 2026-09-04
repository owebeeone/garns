# Generated Garns surface for heldout.celery_get_org_user_db (query); the SQL is the lowered plan, unchanged.
READ = 'heldout.celery_get_org_user_db'
NOUN = 'query'
SQL = 'SELECT s0."rid_people_user" AS "$k0", s0."f_user_created_at" AS "created_at", s0."f_user_updated_at" AS "updated_at", s0."f_user_clerk_user_id" AS "clerk_user_id", s0."f_user_email" AS "email", s0."f_user_in_trial" AS "in_trial", s0."f_user_is_paying" AS "is_paying", s0."f_user_stripe_customer_id" AS "stripe_customer_id", s0."f_user_profession_updated" AS "profession_updated", s0."f_user_is_onboarded" AS "is_onboarded" FROM "tbl_people_user" AS s0 WHERE (s0."f_user_clerk_user_id" IN (SELECT value FROM json_each(:ids))) ORDER BY s0."rid_people_user" ASC'
PARAMS = ('ids',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('created_at', 'updated_at', 'clerk_user_id', 'email', 'in_trial', 'is_paying', 'stripe_customer_id', 'profession_updated', 'is_onboarded')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
