from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, users, kyc

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management System")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(kyc.router)


@app.get("/")
def root():
    return {"status": "User Management System Running"}
