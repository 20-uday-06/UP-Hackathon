from fastapi import APIRouter

from app.api.v1.anc_visits import router as anc_visits_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.audit import router as audit_router
from app.api.v1.birth_plans import router as birth_plans_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.pregnancies import router as pregnancies_router
from app.api.v1.referrals import router as referrals_router

router = APIRouter()
router.include_router(health_router)
router.include_router(pregnancies_router)
router.include_router(anc_visits_router)
router.include_router(birth_plans_router)
router.include_router(referrals_router)
router.include_router(alerts_router)
router.include_router(audit_router)
router.include_router(dashboards_router)
router.include_router(jobs_router)
