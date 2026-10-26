"""V1 API router — aggregates all sub-routers."""
from fastapi import APIRouter
from app.api.v1 import (
    health,
    garmin,
    activities,
    health_metrics,
    analytics,
    ai,
    training,
    user,
    nutrition,
    insights,
    live,
    share,
    trails,
    badges,
    rundown,
    offers,
)

router = APIRouter()
router.include_router(health.router, tags=["Health"])
router.include_router(garmin.router, prefix="/garmin", tags=["Garmin Sync"])
router.include_router(activities.router, prefix="/activities", tags=["Activities"])
router.include_router(health_metrics.router, prefix="/health", tags=["Health Metrics"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(ai.router, prefix="/ai", tags=["AI Coach"])
router.include_router(training.router, prefix="/training", tags=["Training"])
router.include_router(user.router, prefix="/user", tags=["User"])

# Garmin Connect+ Extended Features
router.include_router(nutrition.router, prefix="/nutrition", tags=["Nutrition & Hydration"])
router.include_router(insights.router, prefix="/insights", tags=["Active Intelligence"])
router.include_router(live.router, prefix="/live", tags=["Live Activity"])
router.include_router(share.router, prefix="/share", tags=["Activity Sharing"])
router.include_router(trails.router, prefix="/trails", tags=["Trails & Routes"])
router.include_router(badges.router, prefix="/badges", tags=["Badges & Milestones"])
router.include_router(rundown.router, prefix="/rundown", tags=["Year in Review"])
router.include_router(offers.router, prefix="/offers", tags=["Offers & Connect+"])
