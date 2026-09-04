# Generated Garns surface for events.events_for_org (query); the SQL is the lowered plan, unchanged.
READ = 'events.events_for_org'
NOUN = 'query'
SQL = 'SELECT s0."rid_events_auditevent" AS "$k0", s0."f_auditevent_event_type" AS "event_type", s0."f_auditevent_event_date" AS "event_date" FROM "tbl_events_auditevent" AS s0 WHERE (s0."ref_auditevent_org" = :org) ORDER BY s0."f_auditevent_event_date" ASC, s0."rid_events_auditevent" ASC'
PARAMS = ('org',)
KEY_COLUMNS = ('$k0',)
COLUMNS = ('event_type', 'event_date')
SCOPED = False
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
