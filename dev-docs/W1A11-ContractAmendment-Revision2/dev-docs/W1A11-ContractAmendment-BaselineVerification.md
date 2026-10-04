# W1/A11 amendment baseline verification

**Status:** manager-reproduced pre-build evidence; not amendment acceptance  
**Date:** 2026-10-04

Before the builder's first write, the manager preserved 120 controlling files
byte-for-byte under W1A11-ContractAmendment-Baseline/. Aggregate manifest
SHA-256 is a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf.
All 120 aggregate entries verified. Inside the archive, the following original
nested manifests independently verified at their unchanged relative paths:

| Historical manifest | Verified entries |
|---|---:|
| W1-RegistryContainmentRedesign-MANIFEST-3.sha256 | 26 |
| W2-AdmissionLifetimeRedesign-Inputs.sha256 | 11 |
| W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256 | 18 |
| W2-AdmissionLifetimeRedesign-ReviewEvidence.sha256 | 5 |
| W2-Design-MANIFEST-3.sha256 | 13 |
| W2-DesignControlInputs.sha256 | 13 |
| W2-DesignSourceInputs.sha256 | 48 |

The manager reproduced 148/148 full baseline tests on Python 3.14 with cached
Lark 1.3.1 using PYTHONDONTWRITEBYTECODE=1, src and the verified cached archive
on PYTHONPATH, and -B -m unittest discover -s tests -t .; exit zero. Inherited
SQLite ResourceWarnings remained visible, with no warning filters. A preceding
attempt selected obsolete cached Lark 0.7.8 and failed; selecting 1.3.1 fixed
the test environment without any source change. This is not a product repair.

All five checks in -B tools/check_product.py passed. No live gate-report was
regenerated. The builder independently reported verification of the nine-file
input manifest, 120-file baseline and 111-file unchanged-input guard before
writing. The supplemental ProductGuard.sha256 pins 614 unowned product files,
SHA-256 6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818.
Its file inventory excludes all authorized existing and new builder paths.

These are baseline integrity and test results, not independent finding closure,
actual backend/runtime evidence, PostgreSQL support or amendment acceptance.
Historical live manifests are not rewritten after authorized source changes;
current amendment review receives a separate settled manifest.
