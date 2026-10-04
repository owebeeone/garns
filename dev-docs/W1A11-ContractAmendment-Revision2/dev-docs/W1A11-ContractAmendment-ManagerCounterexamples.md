# Manager additional frozen-tuple counterexamples

**Status:** reproduced; originating State review requested; no source correction yet  
**Date:** 2026-10-04

Current initial manifest47 SHA-256 is
76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8.
This is supplemental evidence after both initial blind reports were returned
and filed, not an input to either initial independent verdict. Their reports
remain unedited. Code plan-cache escape and State buffered-close findings
independently reproduce two manager probes. Two additional sequences below
need explicit reviewer classification before the consolidated correction:

- Acquire a lease, revoke_generation(), then guarded PUBLICATION still invokes
  its callback and increments publications. Acquisition-only revocation is not
  a barrier for already-held operations.
- Move ACQUIRED to RUNNING, then transfer_owner(old,new,queued=True) raises
  ValueError but has already set owner=new. A refused transition changes
  ownership and prevents the prior owner from using the lease.

Read-only probe used the allowed Python 3.14 environment, -B and no file writes:

```python
from tests.contracts.test_admission_contracts import build_fixture
from tests.contracts.test_lifetime_contracts import make_lifetime_fixture, envelope
from garns.backends.contracts.admission import OperationKind, PlanStep
from garns.backends.contracts.values import ParameterValues
from garns.backends.contracts.semantic import Plan
def lease(f):
 return f['registry'].acquire(f['handle'],OperationKind.EXECUTE,ParameterValues({}),f['context'],resource=f['connection'],owner=f['task'][0])
f=build_fixture(); l=lease(f); retained=[]
f['registry'].run_plan_step(l,PlanStep.LOWER,f['task'][0],lambda p: retained.append(p) or 'sql')
print('SIDE_EFFECT_PLAN_ESCAPE',type(retained[0]) is Plan)
f=build_fixture(); l=lease(f); f['registry'].revoke_generation(); effects=[]
f['registry'].run_plan_step(l,PlanStep.PUBLICATION,f['task'][0],lambda p: effects.append('published') or 'rows')
print('REVOKED_LEASE_PUBLICATION',effects,f['registry'].publications)
f=build_fixture(); l=lease(f); r=f['registry']; old=f['task'][0]; new=object()
r.run_plan_step(l,PlanStep.LOWER,old,lambda p: 'sql')
try: r.transfer_owner(l,old,new,queued=True)
except ValueError: pass
try: r.run_plan_step(l,PlanStep.FETCH,old,lambda p: 'rows'); print('OLD_OWNER_RETAINS',True)
except Exception as e: print('OLD_OWNER_RETAINS',False,type(e).__name__)
f=make_lifetime_fixture(); r=f['registry']; e=envelope(f); r.enqueue_buffer(f['queue'],e); r.start_close(f['subscription'])
print('BUFFERED_CLOSE',r.close_outcome(f['subscription']).knowledge,f['coordinator'].count())

```

Observed: SIDE_EFFECT_PLAN_ESCAPE True; REVOKED_LEASE_PUBLICATION
['published'] 1; OLD_OWNER_RETAINS False ContractRefusal; BUFFERED_CLOSE
CloseKnowledge.CLOSED 1. The current manifest verified47/47 after the probe.
No reviewer closure is claimed. The extra two roots should join the same
bounded correction, not an unreviewed manager patch.
