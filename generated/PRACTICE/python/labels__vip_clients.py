# Generated Garns surface for labels.vip_clients (question); the SQL is the lowered plan, unchanged.
READ = 'labels.vip_clients'
NOUN = 'question'
SQL = 'SELECT s0."rid_clients_client" AS "$k0", s0."f_client_preferred_name" AS "preferred_name" FROM "tbl_clients_client" AS s0 WHERE s0."f_client_archived_at" IS NULL AND s0."ref_client_owner" = :_scope AND EXISTS (SELECT 1 FROM "tbl_labels_clientlabel" AS j1 LEFT JOIN "tbl_labels_label" AS j2 ON j2."rid_labels_label" = j1."ref_clientlabel_label" WHERE j1."ref_clientlabel_client" = s0."rid_clients_client" AND (j2."f_label_label_name" = \'vip\')) ORDER BY s0."rid_clients_client" ASC'
PARAMS = ()
KEY_COLUMNS = ('$k0',)
COLUMNS = ('preferred_name',)
SCOPED = True
USES_CLOCK = False
CHILDREN = {

}


def rows(connection, params):
    cursor = connection.execute(SQL, params)
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]
