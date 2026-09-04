# Seed corpus migration log

Each edit is a consequence of the frozen v9-5 language; the seed is otherwise copied byte-for-byte.

- `practice/clients.garns`: `question contacts_named_like of` -> `query contacts_named_like of` — one-shot read without a live bound is a static query in v9-5
- `practice/clients.garns`: `question contacts_with_relationship of` -> `query contacts_with_relationship of` — one-shot read without a live bound is a static query in v9-5
- `practice/clients.garns`: `question all_clients_for_audit of` -> `query all_clients_for_audit of` — one-shot read without a live bound is a static query in v9-5
- `practice/documents.garns`: `question client_documents of` -> `query client_documents of` — one-shot read without a live bound is a static query in v9-5
- `practice/documents.garns`: `question letters_mentioning of` -> `query letters_mentioning of` — one-shot read without a live bound is a static query in v9-5
- `practice/labels.garns`: `where some labels.label_name = "vip"` -> `where some labels.label.label_name = "vip"` — paths traverse resolved link edges only: the inverse `labels` reaches ClientLabel, whose `label` link reaches Label.label_name
- `practice/labels.garns`: question `vip_clients` gains `live bounded 1000` — dynamic-only algebra (some/every, count, composition) stays a question and states its live bound
- `practice/labels.garns`: question `vip_contacts` gains `live bounded 1000` — dynamic-only algebra (some/every, count, composition) stays a question and states its live bound
- `practice/notes.garns`: `question client_card of` -> `query client_card of` — one-shot read without a live bound is a static query in v9-5
- `practice/notes.garns`: `question notes_in_window of` -> `query notes_in_window of` — one-shot read without a live bound is a static query in v9-5
- `practice/notes.garns`: question `dormant_clients` gains `live bounded 1000` — dynamic-only algebra (some/every, count, composition) stays a question and states its live bound
- `practice/world.garns`: `generated python, rust, typescript` -> `generated python, rust` — this build generates python and rust surfaces; an unsupported target refuses
- `practice/deployments.garns`: `engine postgres` -> `engine sqlite` — postgres is recognised but has no lowering in this build; a deployment using it refuses ENGINE_LOWERING_ABSENT at validate (R1 P2.4 repair), so PROD (and AUDIT, which extends it) run on sqlite
- `evolution/g4/world.garns`: `generated python, rust, typescript` -> `generated python, rust` — this build generates python and rust surfaces; an unsupported target refuses
- `evolution/g4/clients.garns`: `use email
    link client -> Client` -> `use email
    use archived_at { optional }
    link client -> Client` — archived_by names a declared optional Instant use; the seed omitted the use on Contact
- `evolution/g5/world.garns`: `generated python, rust, typescript` -> `generated python, rust` — this build generates python and rust surfaces; an unsupported target refuses
- `evolution/g5/clients.garns`: `use email
    link client -> Client` -> `use email
    use archived_at { optional }
    link client -> Client` — archived_by names a declared optional Instant use; the seed omitted the use on Contact
- `everbility/heldout.garns`: `question aget_personal_clients of` -> `query aget_personal_clients of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question aget_client_by_clerk_user_id of` -> `query aget_client_by_clerk_user_id of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question check_org_client of` -> `query check_org_client of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question adelete_client_by_id of` -> `query adelete_client_by_id of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question org_pms_user_maps of` -> `query org_pms_user_maps of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question adapters_by_status of` -> `query adapters_by_status of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question tags_for_property of` -> `query tags_for_property of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question db_get_available_pms_adapters of` -> `query db_get_available_pms_adapters of` — one-shot read without a live bound is a static query in v9-5
- `everbility/heldout.garns`: `question celery_get_org_user_db of` -> `query celery_get_org_user_db of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/world.garns`: `modules traits, people, vault, orgs, auth, events, heldout` -> `modules traits, people, vault, orgs, auth, events` — the seed ships no heldout module; a listed module must be declared (MODULE_UNKNOWN)
- `vaultwarden/events.garns`: `question events_for_user of` -> `query events_for_user of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/events.garns`: `question events_for_org of` -> `query events_for_org of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/orgs.garns`: `question org_collections of` -> `query org_collections of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/vault.garns`: `question unexpired_sends of` -> `query unexpired_sends of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/vault.garns`: `question opaque_present of` -> `query opaque_present of` — one-shot read without a live bound is a static query in v9-5
- `vaultwarden/auth.garns`: `intent grantor : Text "unused; grantor is a link"` -> `(removed)` — an intent used by no carrier refuses (INTENT_HOMELESS)
- `vaultwarden/events.garns`: `intent act_user : Text "unused; acting user is a link"` -> `(removed)` — an intent used by no carrier refuses (INTENT_HOMELESS)
- `appflowy/world.garns`: `modules traits, workspaces, chat, uploads, collab, ai, migrate, heldout_dml` -> `modules traits, workspaces, chat, uploads, collab, ai, migrate` — the seed ships no heldout_dml module; a listed module must be declared (MODULE_UNKNOWN)
- `appflowy/world.garns`: `modules embeddings, heldout_vec` -> `modules embeddings` — the seed ships no heldout_vec module; a listed module must be declared (MODULE_UNKNOWN)
- `appflowy/embeddings.garns`: `link workspace -> Workspace { unenforced scopes inverse embeddings }` -> `link workspace -> Workspace { unenforced scopes }` — an inverse declared on a trait link composes into every carrier of the trait and is ambiguous on the target (INVERSE_DUPLICATED)
