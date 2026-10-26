"""Import all models so Alembic can discover them."""
from app.models.base import Base  # noqa: F401
from app.models.user import UserProfile  # noqa: F401
from app.models.activity import Activity, ActivityLap, ActivitySample  # noqa: F401
from app.models.health import DailyHealthMetric, SleepRecord  # noqa: F401
from app.models.training import RaceGoal, PersonalRecord, TrainingPlan, TrainingPlanDay  # noqa: F401
from app.models.ai import Conversation, ConversationMessage, AIInsight  # noqa: F401
from app.models.sync import SyncJob, ProviderCredential  # noqa: F401
from app.models.nutrition import NutritionEntry, NutritionTarget  # noqa: F401
from app.models.trail import SavedTrail  # noqa: F401
from app.models.milestone import BadgeMilestone  # noqa: F401
from app.models.sharing import ActivityShareLink  # noqa: F401
from app.models.live import LiveSession  # noqa: F401

__all__ = [
    "Base",
    "UserProfile",
    "Activity", "ActivityLap", "ActivitySample",
    "DailyHealthMetric", "SleepRecord",
    "RaceGoal", "PersonalRecord", "TrainingPlan", "TrainingPlanDay",
    "Conversation", "ConversationMessage", "AIInsight",
    "SyncJob", "ProviderCredential",
    "NutritionEntry", "NutritionTarget",
    "SavedTrail",
    "BadgeMilestone",
    "ActivityShareLink",
    "LiveSession",
]
