"""Competition-specific module: sustainability.

Placeholder status router. The real product logic will be added here in the
dedicated build phase for this competition, keeping all competition-specific
code separate from the generic foundation.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/sustainability", tags=["sustainability"])


@router.get("/status")
def feature_status() -> dict:
    return {
        "feature": "sustainability",
        "status": "planned",
        "note": "AI sustainability action planner (goal -> next steps, milestones, impact tracking). Theme: Earth Forward.",
    }
