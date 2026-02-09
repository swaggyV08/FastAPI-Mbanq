from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from datetime import datetime

router = APIRouter(
    prefix="/kyc",
    tags=["KYC"]
)

# Dependency to get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/kyc/submit/{user_id}")
def submit_kyc(
    user_id: int,
    kyc_data: schemas.KYCRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(404, "User not found")

    existing_kyc = db.query(models.KYCDetail).filter(
        models.KYCDetail.user_id == user_id
    ).first()

    if existing_kyc:
        raise HTTPException(400, "KYC already submitted")

    kyc = models.KYCDetail(
        user_id=user_id,
        aadhar_number=kyc_data.aadhar_number,
        kyc_status="PENDING"
    )

    db.add(kyc)
    db.commit()

    return {"message": "KYC submitted successfully"}

@router.put("/admin/verify/{user_id}")
def admin_verify_kyc(
    user_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    kyc = db.query(models.KYCDetail).filter(
        models.KYCDetail.user_id == user_id
    ).first()

    if not kyc:
        raise HTTPException(404, "KYC record not found")

    if status not in ["VERIFIED", "REJECTED"]:
        raise HTTPException(400, "Invalid KYC status")

    kyc.kyc_status = status
    kyc.verified_at = datetime.utcnow() if status == "VERIFIED" else None

    db.commit()

    return {"message": f"KYC {status.lower()} successfully"}
