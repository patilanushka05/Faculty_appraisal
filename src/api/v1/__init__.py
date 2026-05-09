from fastapi import APIRouter
from .auth import router as auth_router
from .appraisal import router as appraisal_router
from .documents import router as documents_router
from .dashboard import router as dashboard_router
from .remarks import router as remarks_router
from .non_teaching import router as non_teaching_router
from .upload import router as upload_router
from .admin import router as admin_router
from .feedback import router as feedback_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(appraisal_router)
router.include_router(documents_router)
router.include_router(dashboard_router)
router.include_router(remarks_router)
router.include_router(non_teaching_router)
router.include_router(upload_router)
router.include_router(admin_router)
router.include_router(feedback_router)
