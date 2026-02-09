import random
from datetime import datetime, timedelta

OTP_STORE = {}

OTP_EXPIRY_MINUTES = 3


def generate_otp(phone_key: str):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[phone_key] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    }
    print(f"OTP for {phone_key}: {otp}")  # visible in terminal ONLY


def verify_otp(phone_key: str, otp: str):
    record = OTP_STORE.get(phone_key)

    if not record:
        return False, "OTP not generated"

    if datetime.utcnow() > record["expires_at"]:
        OTP_STORE.pop(phone_key)
        return False, "OTP expired"

    if record["otp"] != otp:
        return False, "Invalid OTP"

    OTP_STORE.pop(phone_key)
    return True, "OTP verified"
