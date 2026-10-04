# A5 — External capture

**Status: PROPOSED FOR REVIEW.** D5 is closed **DEFERRED** by the accepted
governed-write amendment. v9-6 selects neither trigger tables nor logical
decoding, exposes no working capture endpoint, and freezes no speculative
source/claim/ack adapter. Any residual compatibility call refuses
`EXTERNAL_CAPTURE_DEFERRED` before effect.

Live/history guarantees apply only when every bound-data mutation uses Garns
governed transactions or supported schema management. Static reads of current
committed data do not prove an external mutation entered history. The legacy
inherited capture code remains preserved evidence, not a release claim.

Closure: W7 inventories source, config and docs to prevent enabling or
advertising capture. A future project requires its own reviewed architecture.
