from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.schemas import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(tags=["Upload"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=201,
    summary="Upload CSV files",
    description="Accept customer, policy, and claims CSV files. Validates, cleans, and inserts valid records.",
)
async def upload_csv(
    customer_file: UploadFile = File(...),
    policy_file: UploadFile = File(...),
    claims_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    service = UploadService(db)
    return service.process(
        await customer_file.read(),
        await policy_file.read(),
        await claims_file.read(),
    )
