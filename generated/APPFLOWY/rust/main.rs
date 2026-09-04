// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;


fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {

        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
