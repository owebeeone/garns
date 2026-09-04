// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;
#[path = "events__events_for_org.rs"]
mod events__events_for_org;
#[path = "events__events_for_user.rs"]
mod events__events_for_user;
#[path = "orgs__org_collections.rs"]
mod orgs__org_collections;
#[path = "vault__opaque_present.rs"]
mod vault__opaque_present;
#[path = "vault__unexpired_sends.rs"]
mod vault__unexpired_sends;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {
        "events.events_for_org" => (events__events_for_org::SQL, events__events_for_org::PARAMS),
        "events.events_for_user" => (events__events_for_user::SQL, events__events_for_user::PARAMS),
        "orgs.org_collections" => (orgs__org_collections::SQL, orgs__org_collections::PARAMS),
        "vault.opaque_present" => (vault__opaque_present::SQL, vault__opaque_present::PARAMS),
        "vault.unexpired_sends" => (vault__unexpired_sends::SQL, vault__unexpired_sends::PARAMS),
        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
