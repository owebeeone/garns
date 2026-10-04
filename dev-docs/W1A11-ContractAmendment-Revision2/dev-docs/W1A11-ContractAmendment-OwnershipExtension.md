# W1/A11 amendment ownership extension

**Status:** manager-approved mechanical ownership extension  
**Date:** 2026-10-04

This supplements, without rewriting, the execution brief at SHA-256
1400d30c27e844a35ed1f59a75ec1bce5742e76fafb6df5fce41d984417e14c7.
The sole builder may additionally create and edit:

- src/garns/backends/contracts/generation_reference.py

Purpose: relocate ReferenceGenerationCoordinator from lifetime_reference.py
at a stable checkpoint. Deployment-wide activation/generation coordination
and per-runtime admission/resource/lease/queue ownership are distinct
responsibilities and share public lifetime values, not mutable ownership.
Existing allowed imports/tests may be adjusted for this mechanical boundary.
No new behavior, operational coordinator or execution scope is authorized by
this extension. All remaining ownership, review and evidence rules persist.

The builder requested approval before creating the file, identifying a genuine
cohesion boundary at roughly 617 lines. The split-files guidance informed the
boundary choice; it is not an unrelated repository-wide refactor.
