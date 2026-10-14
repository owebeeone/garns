# Python PostgreSQL design remediation 2

**Status:** focused bounded correction for re-verdict; not self-closure.
**Baseline:** f1adc67a4d9c9fbe6b1177e23f10f5eef186cb31.
**Correction count:** 2 of 2; no new architecture correction.

Consistency P2-4 is accepted. Specify json-document-v1 exact UTF-8 serializer,
short control escapes, lowercase hex for remaining controls, no optional
solidus/non-ASCII escaping, compact separators and no final LF. The same rules
apply to input and retrieval. Preserve the independent outer payload serializer.

Add control/quote/backslash/solidus/non-ASCII/non-BMP and nested vectors, each
with equivalent differently escaped inputs, canonical JSON bytes, base64 atom
and final payload bytes/digest. Lane owner recomputes them using a standard
serializer and a separately implemented scalar/list/object encoder. This is
design-vector evidence only, not native database evidence.

The same two round-2 reviewers continue with context intact. Consistency must
retrace identity T using equivalent escaped inputs; Safety must check that the
bounded correction preserves its GO and prior closures. There is no new graph
composition contract or API change in this correction. Surface remains a
separate next step, not a concurrent third reviewer.
