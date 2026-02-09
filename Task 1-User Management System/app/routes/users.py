from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.utils.security import hash_password
from datetime import datetime
from app.config import ADMIN_SECRET
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=201)
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already in use")

    if db.query(models.User).filter(
        models.User.country_code == user.country_code,
        models.User.phone_number == user.phone_number
    ).first():
        raise HTTPException(status_code=400, detail="Phone number already in use")

    name_parts = user.username.strip().split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    dob = datetime.strptime(user.date_of_birth, "%d-%m-%Y").date()

    new_user = models.User(
        first_name=first_name,
        last_name=last_name,
        email=user.email,
        country_code=user.country_code,
        phone_number=user.phone_number,
        gender=user.gender,
        account_type=user.account_type,
        date_of_birth=dob
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    auth = models.AuthCredential(
        user_id=new_user.id,
        password_hash=hash_password(user.password),
        passcode_hash=hash_password(user.passcode) if user.passcode else None
    )

    db.add(auth)

    address = models.Address(
        user_id=new_user.id,
        door_number=user.address.door_number,
        street_name=user.address.street_name,
        district=user.address.district,
        state=user.address.state,
        pincode=user.address.pincode,
        country=user.address.country
    )

    db.add(address)

    kyc = models.KYCDetail(
        user_id=new_user.id,
        kyc_status="INCOMPLETE"
    )

    db.add(kyc)
    db.commit()

    return {
        "message": "Registration successful. Please complete KYC.",
        "user_id": new_user.id
    }


@router.delete("/admin/deactivate/{user_id}")
def admin_deactivate_user(user_id: int, admin_key: str, db: Session = Depends(get_db)):

    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin access only")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated successfully"}

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    kyc_status = (
        user.kyc.kyc_status
        if user.kyc
        else "NOT_SUBMITTED"
    )

    return {
        "id": user.id,
        "full_name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "phone": f"{user.country_code}{user.phone_number}",
        "is_active": user.is_active,
        "kyc_status": kyc_status
    }
    
#update by admin
@router.put("/admin/update/{user_id}")
def admin_update_user(
    user_id: int,
    data: schemas.AdminUserUpdate,
    admin_key: str,
    db: Session = Depends(get_db)
):

    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin only")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if data.account_type:
        user.account_type = data.account_type

    if data.aadhar_number:
        kyc = db.query(models.KYCDetail).filter(
            models.KYCDetail.user_id == user_id
        ).first()
        if kyc:
            kyc.aadhar_number = data.aadhar_number

    if data.address:
        address = db.query(models.Address).filter(
            models.Address.user_id == user_id,
            models.Address.is_active == True
        ).first()
        if address:
            address.door_number = data.address.door_number
            address.street_name = data.address.street_name
            address.district = data.address.district
            address.state = data.address.state
            address.pincode = data.address.pincode
            address.country = data.address.country

    db.commit()

    return {"message": "User updated successfully"}

