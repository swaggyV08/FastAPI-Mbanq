from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

#Users Credentials
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime)
    account_type = Column(String)
    
    email = Column(String, unique=True, index=True, nullable=False)
    country_code = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)

    gender = Column(String, nullable=True)
    secondary_contact = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    auth = relationship("AuthCredential", back_populates="user", uselist=False)
    address = relationship("Address", back_populates="user")
    kyc = relationship("KYCDetail", back_populates="user", uselist=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

#Authentication(Password only)
class AuthCredential(Base):
    __tablename__ = "auth_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    password_hash = Column(String, nullable=False)
    passcode_hash = Column(String, nullable=True)
    password_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="auth")

#Address Table
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    door_number = Column(String, nullable=False)
    street_name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    country = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="address")

#Kyc Detail Table
class KYCDetail(Base):
    __tablename__ = "kyc_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    aadhar_number = Column(String, unique=True, nullable=True)
    kyc_status = Column(String, default="INCOMPLETE")  
    verified_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="kyc")

#Trasaction Model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(String)  # DEPOSIT / WITHDRAW
    amount = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    
#Admin Model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


