from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.utils.security import verify_password
from app.utils.jwt import create_access_token
from app.utils.otp import generate_otp, verify_otp
from datetime import datetime, timedelta
from app.utils.security import hash_password, verify_password
from app.utils.otp import generate_otp, verify_otp
from app.models import User, AuthCredential, Admin, Transaction, KYCDetail
from app.schemas import LoginPasscode

import random


router = APIRouter(prefix="/auth", tags=["Authentication"])

WELCOME_MESSAGE = "WELCOME TO ZBANQUe"

ADMIN_EMAIL = "vishnup@email.com"
ADMIN_PHONE = "+919123456789"
ADMIN_PASSWORD = "Rasenshuriken@1"
ADMIN_NAME = "VISHNU P (ADMIN)"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import datetime

def build_user_dashboard(user: User, db: Session):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).all()

    balance = 0
    for t in transactions:
        if t.transaction_type == "DEPOSIT":
            balance += t.amount
        elif t.transaction_type == "WITHDRAW":
            balance -= t.amount

    return {
        "message": WELCOME_MESSAGE,
        "account_id": user.id,
        "account_holder": user.full_name,
        "login_time": str(datetime.utcnow()),
        "kyc_status": user.kyc.kyc_status if user.kyc else "INCOMPLETE",
        "available_balance": balance,
        "transactions": [
            {
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "timestamp": str(t.created_at)
            }
            for t in transactions
        ]
    }


#Admin as well as User login 
@router.post("/login/email")
def login_with_email(data: schemas.LoginEmail, db: Session = Depends(get_db)):

    # Admin Login how
    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:

        users = db.query(User).all()

        return {
            "message": WELCOME_MESSAGE,
            "admin_name": ADMIN_NAME,
            "login_time": str(datetime.utcnow()),
            "users": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "phone": f"{u.country_code}{u.phone_number}",
                    "account_type": u.account_type,
                    "kyc_status": u.kyc.kyc_status if u.kyc else "INCOMPLETE",
                    "is_active": u.is_active
                }
                for u in users
            ]
        }


    # User Login
    user = db.query(User).filter(
        User.email == data.email,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="NOT REGISTERED")

    auth = db.query(AuthCredential).filter(AuthCredential.user_id == user.id).first()

    if not auth or not verify_password(data.password, auth.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return build_user_dashboard(user, db)


# Phone number Login 
@router.post("/login/phone")
def login_phone(data: schemas.LoginPhone):
    full_phone = f"{data.country_code}{data.phone_number}"
    otp = generate_otp(full_phone)

    return {
        "message": "OTP sent successfully"
    }


@router.post("/login/phone/verify")
def verify_phone(data: schemas.OTPVerify, db: Session = Depends(get_db)):

    full_phone = f"{data.country_code}{data.phone_number}"

    # Admin OTP login
    if full_phone == ADMIN_PHONE:
        token = create_access_token({"role": "admin"})
        return {
            "message": "Admin logged in",
            "token": token,
            "admin": {"name": "admin"}
        }

    status = verify_otp(full_phone, data.otp)

    if status == "expired":
        raise HTTPException(401, "Session expired, try again")

    if not status:
        raise HTTPException(401, "Invalid OTP")

    user = db.query(models.User).filter(
        models.User.country_code == data.country_code,
        models.User.phone_number == data.phone_number,
        models.User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(404, "Register if new account")

    token = create_access_token({"user_id": user.id})

    kyc_status = user.kyc.kyc_status if user.kyc else "INCOMPLETE"

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": full_phone,
            "kyc_status": kyc_status,
            "available_balance": random.randint(0, 1_000_000),
            "status": "Active" if kyc_status == "VERIFIED" else "KYC incomplete"
        }
    }
#with phone number the token is generated access token 

#Passcode
@router.post("/login/passcode")
def login_with_passcode(data: LoginPasscode, db: Session = Depends(get_db)):

    auth = db.query(AuthCredential).filter(
        AuthCredential.user_id == data.user_id
    ).first()

    if not auth or not auth.passcode_hash:
        raise HTTPException(status_code=401, detail="Passcode not set")

    if not verify_password(data.passcode, auth.passcode_hash):
        raise HTTPException(status_code=401, detail="Invalid passcode")

    user = db.query(User).filter(
        User.id == data.user_id,
        User.is_deleted == False
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return build_user_dashboard(user, db)
