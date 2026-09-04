# Portable contracts

These are the boundaries downstream implementations consume. They are owned by
`garns`; neither the Python package nor these contracts depend on a downstream
runtime, Glade, or Taut.

The initial cut preserves the contract identifiers proven by v9-5:

| Contract | Identifier | Status |
|---|---|---|
| Storage binding | `garns-v9-5/storage-binding/1` | Versioned JSON input |
| Generated manifest | `garns-v9-5/generated-manifest/1` | Versioned JSON output |
| Generated index | `garns-v9-5/generated-index/1` | Versioned JSON output |
| Typed IR | Embedded in `ir.json` | Shape is proven but not yet independently schema-versioned |
| Diagnostic envelope | `(code, stage, file, line, column, detail)` | Stable Python surface; machine schema pending |
| Result encoding | rows, hidden keys, optional total | Semantics documented; machine schema pending |

`contract-ids.json` is the machine-readable registry. New consumers must reject
unknown identifiers rather than infer compatibility. Stabilising schemas for
the IR, diagnostic envelope, and result encoding is the first cross-language
design task; do not reverse-engineer Python dataclasses in another runtime.
