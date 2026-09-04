"""Python and Rust surfaces embedding the lowered SQL unchanged."""

from __future__ import annotations

from .lower_sqlite import Plan


def python_surface(plan: Plan) -> str:
    params = ", ".join(repr(p) for p in plan.params)
    children = "\n".join(f"    {c.column!r}: {c.sql!r}," for c in plan.children)
    return (
        f"# Generated Garns surface for {plan.read} ({plan.noun}); the SQL is the lowered plan, unchanged.\n"
        f"READ = {plan.read!r}\n"
        f"NOUN = {plan.noun!r}\n"
        f"SQL = {plan.sql!r}\n"
        f"PARAMS = ({params}{',' if len(plan.params) == 1 else ''})\n"
        f"KEY_COLUMNS = {tuple(plan.key_columns)!r}\n"
        f"COLUMNS = {tuple(plan.columns)!r}\n"
        f"SCOPED = {plan.scoped!r}\n"
        f"USES_CLOCK = {plan.uses_clock!r}\n"
        f"CHILDREN = {{\n{children}\n}}\n"
        "\n\n"
        "def rows(connection, params):\n"
        "    cursor = connection.execute(SQL, params)\n"
        "    names = [d[0] for d in cursor.description]\n"
        "    return [dict(zip(names, row)) for row in cursor.fetchall()]\n"
    )


def rust_surface(plan: Plan, ident: str) -> str:
    params = ", ".join(f'"{p}"' for p in plan.params)
    columns = ", ".join(f'"{c}"' for c in plan.columns)
    return (
        f"// Generated Garns surface for {plan.read} ({plan.noun}); the SQL is the lowered plan, unchanged.\n"
        f"pub const READ: &str = \"{plan.read}\";\n"
        f"pub const NOUN: &str = \"{plan.noun}\";\n"
        f"pub const SQL: &str = r#\"{plan.sql}\"#;\n"
        f"pub const PARAMS: &[&str] = &[{params}];\n"
        f"pub const COLUMNS: &[&str] = &[{columns}];\n"
        f"pub const SCOPED: bool = {'true' if plan.scoped else 'false'};\n"
        f"pub const USES_CLOCK: bool = {'true' if plan.uses_clock else 'false'};\n"
    )


def rust_main(idents: list[tuple[str, str]]) -> str:
    """A binary that runs any generated read of the world through raw SQLite FFI."""
    mods = "\n".join(f"#[path = \"{ident}.rs\"]\nmod {ident};" for _, ident in idents)
    arms = "\n".join(f'        "{qid}" => ({ident}::SQL, {ident}::PARAMS),' for qid, ident in idents)
    return (
        "// Generated parity runner: executes a read's SQL and prints canonical rows.\n"
        "#![allow(dead_code)]\n"
        "mod sqlite;\n"
        f"{mods}\n\n"
        "fn main() {\n"
        "    let args: Vec<String> = std::env::args().collect();\n"
        "    if args.len() < 3 { eprintln!(\"usage: runner <db> <read> [name=kind:value ...]\"); std::process::exit(2); }\n"
        "    let (sql, _params): (&str, &[&str]) = match args[2].as_str() {\n"
        f"{arms}\n"
        "        other => { eprintln!(\"unknown read {}\", other); std::process::exit(3); }\n"
        "    };\n"
        "    let out = sqlite::run(&args[1], sql, &args[3..]);\n"
        "    print!(\"{}\", out);\n"
        "}\n"
    )
