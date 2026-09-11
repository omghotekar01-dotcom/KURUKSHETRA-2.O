from fastapi import APIRouter

from app.schemas.evaluation import EvaluationReport
from app.services.evaluation import run_evaluation

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])


@router.get("/run", response_model=EvaluationReport)
def evaluation_run() -> EvaluationReport:
    return run_evaluation()
