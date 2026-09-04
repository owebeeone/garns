// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;
#[path = "pantry__heavy_shelves.rs"]
mod pantry__heavy_shelves;
#[path = "pantry__jar_report.rs"]
mod pantry__jar_report;
#[path = "pantry__jars_by_state.rs"]
mod pantry__jars_by_state;
#[path = "pantry__jars_on_heavy_shelves.rs"]
mod pantry__jars_on_heavy_shelves;
#[path = "pantry__open_jars.rs"]
mod pantry__open_jars;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {
        "pantry.heavy_shelves" => (pantry__heavy_shelves::SQL, pantry__heavy_shelves::PARAMS),
        "pantry.jar_report" => (pantry__jar_report::SQL, pantry__jar_report::PARAMS),
        "pantry.jars_by_state" => (pantry__jars_by_state::SQL, pantry__jars_by_state::PARAMS),
        "pantry.jars_on_heavy_shelves" => (pantry__jars_on_heavy_shelves::SQL, pantry__jars_on_heavy_shelves::PARAMS),
        "pantry.open_jars" => (pantry__open_jars::SQL, pantry__open_jars::PARAMS),
        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
