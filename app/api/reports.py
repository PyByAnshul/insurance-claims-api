from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.schemas import StateReportSchema
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/state",
    response_model=list[StateReportSchema],
    summary="State-level claims report",
    description="Returns total claims, average, max, and total payout grouped by state.",
)
def state_report(db: Session = Depends(get_db)):
    return ReportService(db).get_state_report()
