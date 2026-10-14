# A2 — Backend boundary

**Status: PROPOSED FOR REVIEW.** Depend on A1, A4, A7, A12--A14. W2 supplies
one immutable backend-neutral relational `Plan` and `ResultShape`, derived from
qualified IR and `WorldIR`; dialect packages lower it. `Plan` contains no SQL,
driver cursor, physical-name default, parser node, or second expression IR.

`AsyncBackend -> AsyncPool -> AsyncConnection -> AsyncTransaction` owns I/O.
The common surface explicitly includes query/snapshot, schema inspection,
migration-lock acquisition/application, generation outcome, ledger replay,
governed mutation and commit publication. Both backends retain every method;
unsupported capabilities refuse before adapter invocation. Capability,
authority and binding validation precede lowering and every effect.
Stable refusals separate unsupported capability, authorization, deadline,
namespace, generation, migration-accounting and privilege failures from
transient backend faults and A7 commit knowledge.

The W1 root is opaque canonical bytes plus format/digest, while plan origin
records world, IR digest, authored-storage digest and generation. W2 owns the
node algebra. Semantic types retain every inherited `TypeRef` dimension and
nested result shapes name their qualified owner.

Alternatives rejected: portable SQL (leaks SQLite); driver-shaped plans; and
large optional protocols. Closure: W2 defines exhaustive nodes/visitors and
dependency tests; W3/W4 implement the same async protocols and translation
catalog. Names remain provisional for W3 Surface review.
