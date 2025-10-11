from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()

# noinspection PyUnusedImports
import services.call
# noinspection PyUnusedImports
import services.calls
# noinspection PyUnusedImports
import services.exercise
# noinspection PyUnusedImports
import services.exercises
# noinspection PyUnusedImports
import services.member
# noinspection PyUnusedImports
import services.members
# noinspection PyUnusedImports
import services.qualification
# noinspection PyUnusedImports
import services.qualifications
# noinspection PyUnusedImports
import services.subject
# noinspection PyUnusedImports
import services.subjects
# noinspection PyUnusedImports
import services.youth_exercise
# noinspection PyUnusedImports
import services.youth_exercises
# noinspection PyUnusedImports
import services.member_extra

app.include_router(router)
