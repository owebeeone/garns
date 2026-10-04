You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: State
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/W1-RegistryContainmentRedesign-ReviewState.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- /Volumes/projects/limbo/datascad/garns-v9-6: W1-RegistryContainmentRedesign-MANIFEST.sha256 SHA-256 fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff, all 26 listed files
- Object: operator-authorized W1 registry/containment replacement design integrated with retained architecture
- Controlling DRAFT document: dev-docs/W1-RegistryContainmentRedesign-DRAFT.md at d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd
- Out of scope: unrelated inherited source/research and current peer report; manager reports are authorized external outputs

AUTHORITY AND DEFERRALS
- Process authority: review-loop skill, accepted plan §15 pinning exception, operator-approved redesign brief
- Controlling documents to check the object against: Read workspace AGENTS_GWZ.md, product AGENTS.md, then dev-docs/CurrentProgramCheckpoint.md as state authority. Read full review-loop skill and canonical template at /Users/owebeeone/.claude/skills/review-loop/. The inherited accepted plan §15 authorizes SHA-pinned pre-initial-commit review, not Git landing.
Read full dev-docs/W1-RegistryContainmentRedesign-Brief.md SHA afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d. Operator explicitly chose narrow redesign after W1 STOP, preserving trust promises; prior W1 two architectural rounds remain audited. This new replacement object has zero remediation rounds so far, ordinary two-round cap.
Read W1-STOP.md, both W1-ReviewCode-3.md and W1-ReviewState-3.md (LEGITIMATE prior-object testimony), previous remediation plans and W1 execution brief, all controlling accepted plan/seam/decision/scope records it names, W0-ACCEPTANCE.md, docs/PRODUCT_LAYOUT.md. Scope amendment supersedes external capture and historic W6 dependencies; all operator decisions closed.
Controlling hashes: plan 11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512; provider-neutral seam b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01; D6a/D7/D8 079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f; D4/D6b 94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce; governed scope d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe; scope acceptance dac75fd0554b09bda91bfe91c9e03a5c24ad18fc8339503e971355b3d0f8b799; W1 brief 1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344.
Read all 26 manifested files and retained type/IR semantics as needed. Verify only six authorized paths differ from historical W1-MANIFEST-3: A11, A8, ADR README, authority.py, state.py, contract tests. Prior manifest/draft hashes aren't current source checks. No historical before-source snapshot/Git diff exists; compare hash inventories and prior report counterexamples honestly.
- Explicitly deferred (do not report as findings): external capture W6/P6 (DEFERRED, not PASS), crypto/providers, arbitrary host-memory/Python-process secrecy, actual DB/runtime/worker implementations and fault cuts, W2 exhaustive algebra, W3 public names/Surface. Deferrals do not excuse broken W1 shape.
  Deferrals cover a decision's OUTCOME only. Its shape — the verb it lives
  under, its name, whether its lifecycle pair is complete, its defaults — is
  always in scope.

REVIEW AREAS
AXIS: STATE — durable-state semantics and adversity.
Attack state machines, restart legality, ordering/cuts, races/lock scope and closed fail-closed recovery grammar. Focus original unsafe finish trace; outcome-bound completion, every permitted/invalid/malformed final outcome, identity and scope qualification, idempotent conflicting/repeated resolution, commit-before-fence uncertainty, terminal close and all prior recovery/authority fixes. Pure models are not database proof. Closed-state grammar must not invent final knowledge or erase unresolved identities.
Both final prior counterexamples must be independently retried and filed with closure table; confirm all previous W1 fixes survive. Builder self-assessment and green tests aren't closure. Examine the complete integrated tuple, not only changed files. Label any new ARCHITECTURAL root; public names stay provisional until W3 Surface.

COMMANDS
Working directory /Volumes/projects/limbo/datascad/garns-v9-6. Allowed read-only cat/sed/nl/rg/find/wc/shasum/comm inspections; shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256 and manifest/DRAFT/brief/control digest checks at START and END. Compare rg --files docs/adr src/garns/backends/contracts tests/contracts with manifest; compare old/new checksum inventories.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:src /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .
Pure in-memory Python -B counterexamples/introspection with same environment allowed. No writes/bytecode, installations, Git/GWZ mutations, service/database ops or helper agents. Official primary-doc browsing only if verification necessary. Record commands/results/locations.

SEVERITY AND VERDICT CONTRACT
- Findings use IDs P0-n / P1-n / P2-n / P3-n:
  P0 = active corruption, data loss, credential exposure, or false composition.
  P1 = likely destructive or unrecoverable release blocker.
  P2 = concrete correctness, recovery, compatibility, parity, or
       diagnosability defect.
  P3 = bounded robustness, coverage, maintainability, or documentation defect
       with a concrete consequence.
- Verdict is GO or NO-GO. NO-GO while any P0, P1, or P2 is open.
- Each finding: ONE root cause, exact location, violated invariant, credible
  reproduction or state/interleaving sequence, impact, required correction,
  and a closure/regression test. Separate independent root causes.
- Style preferences and speculative unease are not defects. Do not pad.
  Interface shape is not style: wrong command placement, a misleading name,
  a missing half of a lifecycle pair, or an option without a default is a
  finding (P2 or P3), on every axis.
- If your verdict is NO-GO but every blocking finding has a bounded,
  text-or-code-fixable remedy, you may pre-commit: "I pre-commit to GO on a
  revision that resolves {IDs} as specified." This makes the re-verdict cheap
  and is encouraged when honest.

Use complete canonical standalone report template: exact object/baseline/date/axis and verdict; add PRIOR-FINDING CLOSURE TABLE and CHANGED-RANGE ANALYSIS before section 0; evidence, findings, invariant analysis (failed attacks too), risks/next action. No current peer report. Final complete report ONLY, manager files verbatim; do not write it.
