// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;
#[path = "clients__all_clients_for_audit.rs"]
mod clients__all_clients_for_audit;
#[path = "clients__client_assignments.rs"]
mod clients__client_assignments;
#[path = "clients__contacts_named_like.rs"]
mod clients__contacts_named_like;
#[path = "clients__contacts_with_relationship.rs"]
mod clients__contacts_with_relationship;
#[path = "documents__client_documents.rs"]
mod documents__client_documents;
#[path = "documents__letters_mentioning.rs"]
mod documents__letters_mentioning;
#[path = "labels__vip_clients.rs"]
mod labels__vip_clients;
#[path = "labels__vip_contacts.rs"]
mod labels__vip_contacts;
#[path = "notes__client_card.rs"]
mod notes__client_card;
#[path = "notes__dormant_clients.rs"]
mod notes__dormant_clients;
#[path = "notes__notes_in_window.rs"]
mod notes__notes_in_window;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {
        "clients.all_clients_for_audit" => (clients__all_clients_for_audit::SQL, clients__all_clients_for_audit::PARAMS),
        "clients.client_assignments" => (clients__client_assignments::SQL, clients__client_assignments::PARAMS),
        "clients.contacts_named_like" => (clients__contacts_named_like::SQL, clients__contacts_named_like::PARAMS),
        "clients.contacts_with_relationship" => (clients__contacts_with_relationship::SQL, clients__contacts_with_relationship::PARAMS),
        "documents.client_documents" => (documents__client_documents::SQL, documents__client_documents::PARAMS),
        "documents.letters_mentioning" => (documents__letters_mentioning::SQL, documents__letters_mentioning::PARAMS),
        "labels.vip_clients" => (labels__vip_clients::SQL, labels__vip_clients::PARAMS),
        "labels.vip_contacts" => (labels__vip_contacts::SQL, labels__vip_contacts::PARAMS),
        "notes.client_card" => (notes__client_card::SQL, notes__client_card::PARAMS),
        "notes.dormant_clients" => (notes__dormant_clients::SQL, notes__dormant_clients::PARAMS),
        "notes.notes_in_window" => (notes__notes_in_window::SQL, notes__notes_in_window::PARAMS),
        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
