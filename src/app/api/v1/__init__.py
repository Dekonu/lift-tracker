from fastapi import APIRouter

from .exercises import router as exercises_router
from .login import router as login_router
from .logout import router as logout_router
from .muscle_groups import router as muscle_groups_router
from .posts import router as posts_router
from .rate_limits import router as rate_limits_router
from .tasks import router as tasks_router
from .tiers import router as tiers_router
from .users import router as users_router
from .workouts import router as workouts_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(tasks_router)
router.include_router(tiers_router)
router.include_router(rate_limits_router)
router.include_router(muscle_groups_router)
router.include_router(exercises_router)
router.include_router(workouts_router)
