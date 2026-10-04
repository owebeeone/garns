// Minimal raw SQLite FFI used by generated Rust parity runners (no crates).
// Prints one JSON array per row: [[type_code, text], ...] with SQLite's own
// text conversion so that Python and Rust encode identically.

use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_void};

#[link(name = "sqlite3")]
extern "C" {
    fn sqlite3_open(filename: *const c_char, db: *mut *mut c_void) -> c_int;
    fn sqlite3_prepare_v2(db: *mut c_void, sql: *const c_char, n: c_int, stmt: *mut *mut c_void, tail: *mut *const c_char) -> c_int;
    fn sqlite3_step(stmt: *mut c_void) -> c_int;
    fn sqlite3_column_count(stmt: *mut c_void) -> c_int;
    fn sqlite3_column_type(stmt: *mut c_void, i: c_int) -> c_int;
    fn sqlite3_column_text(stmt: *mut c_void, i: c_int) -> *const c_char;
    fn sqlite3_column_blob(stmt: *mut c_void, i: c_int) -> *const u8;
    fn sqlite3_column_bytes(stmt: *mut c_void, i: c_int) -> c_int;
    fn sqlite3_bind_parameter_index(stmt: *mut c_void, name: *const c_char) -> c_int;
    fn sqlite3_bind_int64(stmt: *mut c_void, i: c_int, v: i64) -> c_int;
    fn sqlite3_bind_double(stmt: *mut c_void, i: c_int, v: f64) -> c_int;
    fn sqlite3_bind_text(stmt: *mut c_void, i: c_int, v: *const c_char, n: c_int, f: *const c_void) -> c_int;
    fn sqlite3_bind_null(stmt: *mut c_void, i: c_int) -> c_int;
    fn sqlite3_finalize(stmt: *mut c_void) -> c_int;
    fn sqlite3_close(db: *mut c_void) -> c_int;
    fn sqlite3_errmsg(db: *mut c_void) -> *const c_char;
}

const SQLITE_TRANSIENT: *const c_void = usize::MAX as *const c_void;

fn escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for ch in s.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

/// Bind `name=kind:value` arguments: kinds i (int), f (float), s (text), n (null).
pub fn run(db_path: &str, sql: &str, binds: &[String]) -> String {
    let mut out = String::new();
    unsafe {
        let mut db: *mut c_void = std::ptr::null_mut();
        let path = CString::new(db_path).unwrap();
        if sqlite3_open(path.as_ptr(), &mut db) != 0 {
            eprintln!("open failed");
            std::process::exit(4);
        }
        let csql = CString::new(sql).unwrap();
        let mut st: *mut c_void = std::ptr::null_mut();
        if sqlite3_prepare_v2(db, csql.as_ptr(), -1, &mut st, std::ptr::null_mut()) != 0 {
            eprintln!("prepare failed: {}", CStr::from_ptr(sqlite3_errmsg(db)).to_string_lossy());
            std::process::exit(5);
        }
        for b in binds {
            let (name, rest) = b.split_once('=').expect("name=kind:value");
            let (kind, value) = rest.split_once(':').expect("kind:value");
            let cname = CString::new(format!(":{}", name)).unwrap();
            let idx = sqlite3_bind_parameter_index(st, cname.as_ptr());
            if idx == 0 { continue; }
            match kind {
                "i" => { sqlite3_bind_int64(st, idx, value.parse::<i64>().expect("int")); }
                "f" => { sqlite3_bind_double(st, idx, value.parse::<f64>().expect("float")); }
                "s" => { let cv = CString::new(value).unwrap(); sqlite3_bind_text(st, idx, cv.as_ptr(), -1, SQLITE_TRANSIENT); }
                _ => { sqlite3_bind_null(st, idx); }
            }
        }
        loop {
            let rc = sqlite3_step(st);
            if rc != 100 { if rc != 101 { eprintln!("step failed: {}", CStr::from_ptr(sqlite3_errmsg(db)).to_string_lossy()); std::process::exit(6); } break; }
            let n = sqlite3_column_count(st);
            let mut cells: Vec<String> = Vec::new();
            for i in 0..n {
                let ty = sqlite3_column_type(st, i);
                let text = if ty == 5 {
                    String::from("null")
                } else if ty == 4 {
                    let len = sqlite3_column_bytes(st, i) as usize;
                    let p = sqlite3_column_blob(st, i);
                    let bytes = std::slice::from_raw_parts(p, len);
                    escape(&bytes.iter().map(|b| format!("{:02x}", b)).collect::<String>())
                } else {
                    let p = sqlite3_column_text(st, i);
                    escape(&CStr::from_ptr(p).to_string_lossy())
                };
                cells.push(format!("[{},{}]", ty, text));
            }
            out.push('[');
            out.push_str(&cells.join(","));
            out.push_str("]\n");
        }
        sqlite3_finalize(st);
        sqlite3_close(db);
    }
    out
}
