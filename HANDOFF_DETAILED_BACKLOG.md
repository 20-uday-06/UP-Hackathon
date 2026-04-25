# UP Maternal Care - Detailed Handoff and Backlog

## 1) Purpose of this document
This document is the single source of truth for what is still pending, what must be improved, and exactly how to continue implementation.

Operational rule:
- Update this document at every pause or handoff.
- Add completed items to the done log and remove them from pending sections.
- Keep implementation notes concrete (file names, endpoint names, schema changes, test evidence).

## 2) Current product state (as of April 25, 2026)
The project now has a working backend vertical slice and an operational demo UI.

Implemented:
- Pregnancy registration API with EDD calculation.
- ANC visit API with expanded clinical fields.
- HRP rule engine with broad initial coverage and persistent condition storage.
- Birth plan create/update API.
- Referral create and stage transition API.
- Alerts table and alert APIs (list, acknowledge).
- Daily jobs endpoint for HRP 30-day alert creation and alert escalation.
- Audit event table and write hooks for selected workflows.
- Basic state dashboard summary endpoint.
- Demo browser console under /app.

Important status note:
- This is a functional end-to-end demo baseline, not yet a production-complete implementation of the full specification.

## 3) Architecture snapshot
Backend:
- FastAPI + SQLModel
- Local database currently SQLite (default: up_maternal_care_v2.db)
- Background work exposed as trigger endpoints (not yet distributed scheduler/worker)
- Static demo UI served from app/web

Core API groups currently present:
- /api/v1/pregnancies
- /api/v1/anc-visits
- /api/v1/birth-plans
- /api/v1/referrals
- /api/v1/alerts
- /api/v1/jobs
- /api/v1/dashboards
- /api/v1/audit

## 4) Critical product gaps (priority order)

### P0 - Must complete before judging or pilot

#### 4.1 Authentication and RBAC enforcement
Current state:
- No complete authentication workflow for real users and roles.
- No strict endpoint-level authorization matrix.

Pending work:
- Add user, role, role_permission, user_facility, user_geography scope tables.
- Add login flow (OTP or mock OTP), JWT access + refresh token rotation.
- Implement authorization dependency middleware per endpoint.
- Enforce role restrictions:
  - Only MO can resolve HRP conditions.
  - Worker-level data access must be geography-scoped.
  - District/state roles must get aggregate and privileged read access.

Acceptance criteria:
- Every write endpoint rejects unauthorized actor with 403.
- Cross-scope access attempts are blocked.
- Token refresh and expiry paths are covered by tests.

#### 4.2 HRP rule engine completion and clinical correctness
Current state:
- Rules are partially/approximately implemented.
- Some rules need proper temporal/context logic.

Pending work:
- Implement all 20 HRP conditions exactly per specification.
- Add context-aware rules requiring history:
  - PIH requires two qualifying readings.
  - Pre-eclampsia timing and proteinuria constraints.
  - GDM first-test and rescreen window (min gap logic).
  - Thyroid trimester-specific thresholding with FT4 conditions.
- Add deterministic rule trace output (which data point triggered which rule).
- Build MO resolution workflow with immutable condition-resolution audit details.

Acceptance criteria:
- 20/20 rule vectors pass.
- Borderline threshold tests pass (just below, equal, just above).
- Resolution path logs actor, role, timestamp, previous/new condition set.

#### 4.3 Mandatory 30-day HRP alert workflow hardening
Current state:
- Alert creation exists, but full acknowledgement hierarchy and supervisor escalation mapping is not complete.

Pending work:
- Persist stakeholder acknowledgement records per alert.
- Build supervisor lookup chain by role and geography.
- Enforce escalation policy:
  - Escalate at 24h to supervisor.
  - Escalate at 48h to district and create call-center follow-up task.
- Add idempotent job execution and duplicate prevention keys.
- Add SLA dashboard counters for pending, acknowledged, escalated.

Acceptance criteria:
- For EDD minus 30 HRP pregnancies, all 8 stakeholder alerts are created exactly once.
- 24h and 48h escalations trigger exactly as required.
- Dashboard reflects real-time status counts.

#### 4.4 Closed-loop referral completion controls
Current state:
- Stage updates exist but strict guardrails are incomplete.

Pending work:
- Enforce legal stage transition order.
- Add stage-level SLA timers and escalation events.
- Require minimum fields per stage before progression.
- Lock referral closure unless admission and outcome are present.
- Add facility acknowledgement timeout handling (1 hour rule).

Acceptance criteria:
- Invalid stage transitions return 400 with clear reason.
- SLA breach creates escalation event and appears on dashboard.
- Referral cannot close without required fields.

### P1 - Required for full spec parity

#### 4.5 ANC due/missed reminder orchestration
Current state:
- Trigger endpoint exists for jobs, but ANC reminder timeline is not fully implemented.

Pending work:
- Build scheduler jobs for:
  - Due reminder D-7, D-3, D0
  - Missed escalation D+1 (ASHA), D+3 (ANM), D+7 (MO)
- Add repeated-miss logic for 2 consecutive missed visits.
- Create worker task queue entries and clear-on-completion behavior.

Acceptance criteria:
- Synthetic time advancement tests confirm reminders/escalations on exact dates.
- Queue entries are generated and cleared correctly.

#### 4.6 Kit distribution module
Current state:
- Not implemented.

Pending work:
- Add kit distribution schema for 6 stages.
- Add distribution APIs and beneficiary acknowledgement APIs.
- Add overdue kit detection and supply-gap dashboard integration.

Acceptance criteria:
- All 6 kit flows can be completed in a test scenario.
- Overdue kits appear in worker and block queues.

#### 4.7 Consent and privacy controls
Current state:
- Partial privacy-oriented fields, but full consent model is not complete.

Pending work:
- Add explicit consent ledger at registration.
- Implement consent withdrawal effect: stop outbound communication jobs.
- Add log sanitization utility to prevent PII leakage in logs.
- Add Aadhaar masking validation hooks.

Acceptance criteria:
- Outbound messages stop for withdrawn consent cases.
- Security tests show no full Aadhaar persistence/logging.

### P2 - Integration and operational maturity

#### 4.8 Integration adapters (mock first, then live)
Current state:
- No full adapter architecture with retries and observability.

Pending work:
- Build adapter interfaces and providers for:
  - WhatsApp Business API
  - HMIS
  - RCH
  - ABDM
  - 102 transport
  - 108 emergency
- Add webhook processing with signature verification.
- Add message delivery status ingestion and retry logic.

Acceptance criteria:
- All adapters have mock implementation and contract tests.
- Live adapter toggles controlled via config.

#### 4.9 Infrastructure and data reliability
Current state:
- SQLite local mode.

Pending work:
- Move to PostgreSQL for primary storage.
- Add Redis for queues/cache.
- Add Alembic migrations and migration policy.
- Add backup/restore scripts and retention settings.

Acceptance criteria:
- Fresh deployment from migration baseline works end-to-end.
- Restore drill completes successfully.

#### 4.10 Observability and SLO reporting
Current state:
- Minimal operational telemetry.

Pending work:
- Add structured logging and correlation IDs.
- Add metrics for API latency, queue lag, alert throughput, escalation volume.
- Add health/readiness endpoints for dependencies.
- Build SLO dashboard views.

Acceptance criteria:
- P95 endpoints and job latencies are measurable.
- Alert pipeline failures are visible in monitoring.

## 5) Frontend and user experience backlog

### 5.1 Worker and admin dashboards
Pending:
- Build role-specific dashboard pages (state, district, block, facility, worker).
- Show SLA breaches, pending acknowledgements, HRP heatmap, due lists.
- Add CSV/PDF export endpoints and UI actions.

### 5.2 Citizen interaction channel
Pending:
- WhatsApp-first conversational flow implementation.
- Hindi and English templates and fallback handling.
- Danger sign NLP detection and emergency queue linkage.

## 6) Data model backlog details

Add or refine tables:
- users
- roles
- permissions
- user_role_map
- facility
- geography_boundary
- stakeholder_supervisor_map
- consent_ledger
- task_queue
- notification_delivery_status
- kit_distribution
- integration_event_log
- escalation_event

Indexes to add:
- pregnancy (district, status, hrp_flag, edd_date)
- anc_visit (pregnancy_id, visit_date)
- alert_event (pregnancy_id, alert_type, status, created_at)
- referral (pregnancy_id, referral_status, created_at)
- task_queue (assignee, due_at, status)

## 7) API backlog details

Required additions:
- Auth:
  - POST /api/v1/auth/login
  - POST /api/v1/auth/refresh
  - POST /api/v1/auth/logout
- Users and roles:
  - CRUD for users/role assignment
- Tasks:
  - GET/POST/PATCH task queue endpoints
- Kit distribution:
  - POST distribution updates
  - POST acknowledgement
  - GET pending by role
- ANC scheduling:
  - System job endpoints and read APIs for due/missed lists

Refinements:
- Add pagination and cursor support where needed.
- Add idempotency key support on all critical writes.
- Add response envelopes for better client consistency.

## 8) Testing backlog (must be automated)

Unit tests:
- HRP rule vectors and edge thresholds.
- Date window and escalation timing logic.
- Stage transition validators.

Integration tests:
- Registration to ANC to HRP to birth plan to referral closure.
- 30-day alert creation and acknowledgement escalation chain.
- Consent withdrawal suppresses outbound notifications.

Performance tests:
- API read/write latency targets.
- Job throughput under synthetic load.
- Alert fan-out latency under concurrent cases.

Security tests:
- RBAC bypass attempts.
- PII exposure checks.
- Token misuse/replay behavior.

## 9) Known technical debt and risks
- Auto table-creation currently used for development convenience; must move to migration-first.
- Rules are functional but need strict clinical-grade implementation and review.
- Demo UI is operator-friendly but not yet role-specific production UX.
- Integration dependencies can block progress without mock-first adapters.

## 10) Suggested execution order for next person
1. Introduce auth + RBAC middleware and protect all current endpoints.
2. Add Alembic and migrate to PostgreSQL + Redis profile.
3. Complete HRP rule correctness and associated test matrix.
4. Implement ANC scheduling and full escalation engine.
5. Add kit distribution module and role task queues.
6. Implement adapter layer for WhatsApp and transport APIs (mock first).
7. Build role dashboards and exports.
8. Harden security and observability, then run end-to-end rehearsal.

## 11) Done log (update every handoff)
- 2026-04-25: Backend vertical slice operational with demo UI and end-to-end flow support.
- 2026-04-25: Added referral lifecycle APIs, alert job endpoints, and audit events.
- 2026-04-25: Added this detailed handoff and pending-work tracker.
- 2026-04-25: Pushed repository to https://github.com/20-uday-06/UP-Hackathon.git (branch main). Updated .gitignore to exclude runtime artifacts.
