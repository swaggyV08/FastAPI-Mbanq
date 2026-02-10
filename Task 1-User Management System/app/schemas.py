from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
import re

class AccountType(str, Enum):
    student = "Student"
    savings = "Savings"
    corporate = "Corporate"


class KYCStatus(str, Enum):
    incomplete = "INCOMPLETE"
    pending = "PENDING"
    verified = "VERIFIED"
    rejected = "REJECTED"



# Address Schema 
class AddressBase(BaseModel):
    door_number: str
    street_name: str
    district: str
    state: str
    pincode: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )
    country: str


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int

    class Config:
        from_attributes = True

#Password Schema
class PasswordSchema(BaseModel):
    password: str

    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 5:
            raise ValueError("Password must have at least 5 characters")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain one uppercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain one number")

        if not re.search(r"[@$!%*?&]", password):
            raise ValueError("Password must contain one special character")

        return password

#Passcode
class PasscodeSchema(BaseModel):
    passcode: str

    @classmethod
    def validate_passcode(cls, passcode: str):
        if not re.fullmatch(r"\d{6}", passcode):
            raise ValueError("Passcode must be exactly 6 digits")
        return passcode


# User Registration
class UserRegister(BaseModel):
    username: str
    date_of_birth: str  # DD-MM-YYYY
    gender: str

    account_type: str

    email: EmailStr
    country_code: str
    phone_number: str

    password: str
    passcode: Optional[str] = None

    aadhar: str

    address: AddressCreate



# User Login
class LoginEmail(BaseModel):
    email: EmailStr
    password: str


class LoginPhone(BaseModel):
    country_code: str
    phone_number: str


class OTPVerify(BaseModel):
    country_code: str
    phone_number: str
    otp: str
    
class LoginPasscode(BaseModel):
    user_id: int  # account id
    passcode: str




# User Profile information
class UserProfile(BaseModel):
    account_id: int
    account_holder: str
    login_time: str
    kyc_status: str
    available_balance: int
    transactions: list




# Password update by user only 
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)



# Adress by admin 
class AddressUpdate(AddressBase):
    pass



# Kyc limits of the the adhaar and pincode

class KYCRequest(BaseModel):
    aadhar_number: str = Field(
        min_length=12,
        max_length=12,
        pattern="^[0-9]{12}$",
        examples=["123412341234"]
    )

    address: AddressBase


# ADMIN RESPONSE (NO PASSWORDS)

class AdminUserView(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    country_code: str
    phone_number: str

    account_type: AccountType
    is_active: bool
    kyc_status: KYCStatus
    available_balance: int

    class Config:
        from_attributes = True

class AdminUserUpdate(BaseModel):
    aadhar_number: Optional[str] = None
    account_type: Optional[str] = None

    address: Optional[AddressBase] = None
