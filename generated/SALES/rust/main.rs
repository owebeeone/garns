// Generated parity runner: executes a read's SQL and prints canonical rows.
#![allow(dead_code)]
mod sqlite;
#[path = "sales__open_orders.rs"]
mod sales__open_orders;
#[path = "sales_static__distinct_open_customers.rs"]
mod sales_static__distinct_open_customers;
#[path = "sales_static__open_orders_once.rs"]
mod sales_static__open_orders_once;
#[path = "sales_static__revenue_open_by_customer.rs"]
mod sales_static__revenue_open_by_customer;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 { eprintln!("usage: runner <db> <read> [name=kind:value ...]"); std::process::exit(2); }
    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {
        "sales.open_orders" => (sales__open_orders::SQL, sales__open_orders::PARAMS),
        "sales_static.distinct_open_customers" => (sales_static__distinct_open_customers::SQL, sales_static__distinct_open_customers::PARAMS),
        "sales_static.open_orders_once" => (sales_static__open_orders_once::SQL, sales_static__open_orders_once::PARAMS),
        "sales_static.revenue_open_by_customer" => (sales_static__revenue_open_by_customer::SQL, sales_static__revenue_open_by_customer::PARAMS),
        other => { eprintln!("unknown read {}", other); std::process::exit(3); }
    };
    let out = sqlite::run(&args[1], sql, &args[3..]);
    print!("{}", out);
}
