COMPLETE — design-only drafting is finished and writes are stopped.

Output: [W1A11-WorkerExitRedesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W1A11-WorkerExitRedesign.md)  
SHA-256: `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`  
Size: 737 lines, 45,357 bytes.

Key decisions:

- The lifetime registry is the sole mutable owner of worker authorization, reservations, exit, containment, result acceptance, and terminal release. Worker-authority files may hold identities/helpers only.
- Defines the complete success/failure/cancel state grammar, exact receiver and worker trust, registry-held success escrow, executor-issued authoritative stop receipt, replay tombstones, conflict behavior, and closed late completion.
- Atomically reserves ordinals before fixed issuer-owned effects. Nested, reentrant, and concurrent effects refuse. `BaseException`, cancellation, cleanup failure, and racing exits retain charges and transfer safely to containment.
- Keeps worker quiescence, operation terminal state, and A7 transaction truth independent.
- Allows result acceptance only by the original live receiving runtime task without transferring `TrustedContext` or claims; publication remains a separate atomic barrier.
- Selects registration retirement plus complete A6 refetch for unpublished FIFO-head failure. Failed delivery never advances the old delivered frontier or permits successors to cross.
- Defines activation-bracketed membership, preactivation close, immutable attempt membership, and quiescence-bound final leave.
- Defines ordered changed/neutral lineage across zero, queued, and active ranges. Neutral progress cannot make earlier changed work appear delivered or strand later changed work.
- Binds no-effect evidence to exact attempt, phase serial, phase request, and requested successor; reopen invalidates old admissions and queued buffers atomically.
- Maps all five stopped roots and retained IDs, preserves the initial 18 and correction-1 13 regressions plus expanded revocation, and does not claim source closure.
- Retains the 796-line lifetime registry as an explicit atomic-state cohesion exception; no speculative split is proposed.
- Preserves A7, result roles, pinned parameters, parent-owned derived commands, public task-bound context, and the no-raw-`Plan` boundary.
- Production worker/runtime, databases, durability, physical fencing, activation, external capture, and public naming remain explicitly deferred.

Inputs read included both accepted W2 documents, W1/W2 acceptances, A1–A16, checkpoint/layout material, the stopped amendment and remediation records, all five final stop-root reports, current relevant contract sources/tests, the complete review-loop skill/template, and the split-files skill. The review-loop instructions determined the prospective-only finding language and independent GO/GO gate; split-files guidance informed the lifecycle-ownership boundary and no-split decision.

Integrity checks were run at both start and end using `shasum -a 256 -c`:

- Redesign Inputs: 19 verified, 0 failures.
- Frozen MANIFEST-3 source: 71 verified, 0 failures.
- Read-only guard: 111 verified, 0 failures.
- Product guard: 614 verified, 0 failures.

Pinned hashes independently confirmed:

- Brief: `9ba4854b5ce14c86b22b76f1b1a42c05acef228723aa427999c7a5123b1f6a56`
- Inputs: `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`
- MANIFEST-3: `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`
- W2 base: `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`
- W2 overlay: `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`

Read-only structural checks found 14 numbered sections and 26 balanced Markdown fences.

No tests were run because this is design-only and test success cannot establish redesign closure. No helper agents, source/test/ADR edits, Git operations, network access, installs, services, databases, bytecode generation, `tools/check.py`, or implementation launch occurred. The only write was the authorized design file via `apply_patch`.

This testimony is not a self-GO. The next authorized action is manager pinning followed by independent Consistency and Safety reviews and originating-counterexample retracing.
