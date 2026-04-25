# UP Maternal Care Backend

This backend now supports a complete operational demo flow from pregnancy registration to ANC-based HRP detection, birth planning, referral progression, daily alert jobs, and monitoring summaries.

## Implemented so far

- FastAPI backend with versioned API routing.
- SQLModel persistence and automatic table bootstrap.
- Pregnancy registration with EDD calculation and manual HRP baseline risk factors.
- ANC visit ingestion with expanded clinical fields.
- HRP rule engine with broad condition coverage and persistent HRP code storage.
- Stakeholder alert generation on HRP flagging.
- Mandatory 30-day HRP pre-delivery alert job and escalation job.
- Birth plan create/update flow with HRP facility constraint checks.
- Closed-loop referral lifecycle API with stage transitions.
- Immutable audit event recording for write operations.
- State summary dashboard endpoint.
- Embedded web console for end-to-end demo operations at /app.

## API endpoints

- GET / -> service metadata
- GET /app -> interactive operations console
- GET /api/v1/health
- POST /api/v1/pregnancies
- GET /api/v1/pregnancies
- GET /api/v1/pregnancies/{pregnancy_id}
- PATCH /api/v1/pregnancies/{pregnancy_id}/touch
- POST /api/v1/pregnancies/{pregnancy_id}/resolve-hrp (MO-only)
- POST /api/v1/anc-visits
- POST /api/v1/birth-plans
- POST /api/v1/referrals
- POST /api/v1/referrals/{referral_id}/stage
- GET /api/v1/alerts
- POST /api/v1/alerts/{alert_id}/ack
- POST /api/v1/alerts/jobs/hrp-30-day
- POST /api/v1/alerts/jobs/escalate
- POST /api/v1/jobs/run-daily
- GET /api/v1/dashboards/state-summary
- GET /api/v1/audit

## Local setup

1. Create a virtual environment.
2. Install dependencies.
3. Copy .env.example to .env.
4. Start the API server.

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- Swagger: http://127.0.0.1:8000/docs
- Demo console: http://127.0.0.1:8000/app

## Suggested week-by-week roadmap (next 6 weeks)

1. Week 1: Stabilize data layer with Alembic migrations and PostgreSQL; add role/user tables and strict RBAC middleware.
2. Week 2: Complete ANC reminder and missed-visit escalation scheduler with durable queue workers.
3. Week 3: Implement WhatsApp adapter service and template-based outbound messaging with delivery tracking.
4. Week 4: Integrate 102/108 transport and strengthen referral SLA escalation rules.
5. Week 5: Build role-specific dashboards and task queues with websocket updates.
6. Week 6: Add integration adapters for HMIS/RCH/ABDM, full test automation, and security hardening.
