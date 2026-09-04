// Generated Garns surface for events.events_for_user (query); the SQL is the lowered plan, unchanged.
pub const READ: &str = "events.events_for_user";
pub const NOUN: &str = "query";
pub const SQL: &str = r#"SELECT s0."rid_events_auditevent" AS "$k0", s0."f_auditevent_event_type" AS "event_type", s0."f_auditevent_event_date" AS "event_date", s0."f_auditevent_ip_address" AS "ip_address" FROM "tbl_events_auditevent" AS s0 WHERE (s0."ref_auditevent_user" = :who) ORDER BY s0."f_auditevent_event_date" ASC, s0."rid_events_auditevent" ASC"#;
pub const PARAMS: &[&str] = &["who"];
pub const COLUMNS: &[&str] = &["event_type", "event_date", "ip_address"];
pub const SCOPED: bool = false;
pub const USES_CLOCK: bool = false;
