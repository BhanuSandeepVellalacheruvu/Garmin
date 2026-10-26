"""Connect+ Perks, Offers, and Active Capabilities status endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def get_offers_and_perks():
    return {
        "tier": "Connect+ Pro",
        "status": "active",
        "active_intelligence_enabled": True,
        "features": [
            {
                "id": "active_intelligence",
                "title": "Garmin AI Active Intelligence",
                "description": "Real-time physiological readiness calculation, acute-chronic load balancing, and automated workout adjustments.",
                "badge": "Active",
                "badge_color": "emerald",
            },
            {
                "id": "smart_nutrition",
                "title": "Adaptive Nutrition & Hydration",
                "description": "Dynamic daily caloric and electrolyte targets tailored to your scheduled training load and recent sweat rate.",
                "badge": "Included",
                "badge_color": "blue",
            },
            {
                "id": "livetrack_enhanced",
                "title": "Enhanced LiveTrack & Course Sharing",
                "description": "Unlimited sharable LiveTrack links with interactive GPS waypoints and granular privacy controls.",
                "badge": "Included",
                "badge_color": "blue",
            },
            {
                "id": "route_explorer",
                "title": "Garmin Trails Route Explorer",
                "description": "Direct GPX course synthesis and waypoint elevation analysis directly from historical activity data.",
                "badge": "Included",
                "badge_color": "blue",
            },
            {
                "id": "ollama_coach",
                "title": "Private LLM AI Coach",
                "description": "Zero-data-leakage coaching with Ollama Cloud Gemma 4 integration grounded in your personal training database.",
                "badge": "Connected",
                "badge_color": "purple",
            },
        ],
        "partner_perks": [
            {
                "partner": "Garmin Express & IQ Store",
                "offer": "Custom Data Fields & Watch Faces",
                "code": "IQ-LAB-2026",
                "status": "Available",
            },
            {
                "partner": "Precision Fuel & Hydration",
                "offer": "15% Athlete Sweat Test & Electrolyte Plans",
                "code": "GARMINLAB15",
                "status": "Claimable",
            },
            {
                "partner": "Stryd & Running Dynamics",
                "offer": "Advanced Power Meter Calibration Guide",
                "code": "STRYD-GARMIN-SYNC",
                "status": "Available",
            },
        ],
    }
