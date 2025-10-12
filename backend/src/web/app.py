from fastapi import APIRouter

from services.call import router as call_router
from services.calls import router as calls_router
from services.exercise import router as exercise_router
from services.exercises import router as exercises_router
from services.member import router as member_router
from services.member_extra import router as member_extra_router
from services.members import router as members_router
from services.qualification import router as qualification_router
from services.qualifications import router as qualifications_router
from services.subject import router as subject_router
from services.subjects import router as subjects_router
from services.youth_exercise import router as youth_exercise_router
from services.youth_exercises import router as youth_exercises_router

router = APIRouter()

_api_router = APIRouter(prefix="/api")
_api_router.include_router(call_router)
_api_router.include_router(calls_router)
_api_router.include_router(exercise_router)
_api_router.include_router(exercises_router)
_api_router.include_router(member_router)
_api_router.include_router(members_router)
_api_router.include_router(qualification_router)
_api_router.include_router(qualifications_router)
_api_router.include_router(subject_router)
_api_router.include_router(subjects_router)
_api_router.include_router(youth_exercise_router)
_api_router.include_router(youth_exercises_router)
_api_router.include_router(member_extra_router)
router.include_router(_api_router)
