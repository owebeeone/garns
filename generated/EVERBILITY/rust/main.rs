// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;
#[path = "heldout__adapters_by_status.rs"]
mod heldout__adapters_by_status;
#[path = "heldout__adelete_client_by_id.rs"]
mod heldout__adelete_client_by_id;
#[path = "heldout__aget_client_by_clerk_user_id.rs"]
mod heldout__aget_client_by_clerk_user_id;
#[path = "heldout__aget_personal_clients.rs"]
mod heldout__aget_personal_clients;
#[path = "heldout__celery_get_org_user_db.rs"]
mod heldout__celery_get_org_user_db;
#[path = "heldout__check_org_client.rs"]
mod heldout__check_org_client;
#[path = "heldout__db_get_available_pms_adapters.rs"]
mod heldout__db_get_available_pms_adapters;
#[path = "heldout__org_pms_user_maps.rs"]
mod heldout__org_pms_user_maps;
#[path = "heldout__tags_for_property.rs"]
mod heldout__tags_for_property;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {
        "heldout.adapters_by_status" => (heldout__adapters_by_status::SQL, heldout__adapters_by_status::PARAMS),
        "heldout.adelete_client_by_id" => (heldout__adelete_client_by_id::SQL, heldout__adelete_client_by_id::PARAMS),
        "heldout.aget_client_by_clerk_user_id" => (heldout__aget_client_by_clerk_user_id::SQL, heldout__aget_client_by_clerk_user_id::PARAMS),
        "heldout.aget_personal_clients" => (heldout__aget_personal_clients::SQL, heldout__aget_personal_clients::PARAMS),
        "heldout.celery_get_org_user_db" => (heldout__celery_get_org_user_db::SQL, heldout__celery_get_org_user_db::PARAMS),
        "heldout.check_org_client" => (heldout__check_org_client::SQL, heldout__check_org_client::PARAMS),
        "heldout.db_get_available_pms_adapters" => (heldout__db_get_available_pms_adapters::SQL, heldout__db_get_available_pms_adapters::PARAMS),
        "heldout.org_pms_user_maps" => (heldout__org_pms_user_maps::SQL, heldout__org_pms_user_maps::PARAMS),
        "heldout.tags_for_property" => (heldout__tags_for_property::SQL, heldout__tags_for_property::PARAMS),
        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
