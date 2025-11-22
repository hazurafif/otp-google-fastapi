from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from auth import oauth
from database import SessionLocal, engine
from email_utils import send_otp_email
from models import Base, User
from otp import generate_otp

Base.metadata.create_all(bind=engine)


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_SESSION_KEY_CHANGE_ME"
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "FastAPI OTP Google Login"}


@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    email = user_info["email"]
    google_id = user_info["sub"]

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, google_id=google_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate OTP
    otp_code = generate_otp()
    user.otp = otp_code
    user.otp_expires = datetime.now() + timedelta(minutes=5)
    db.commit()

    # Normally send via email or SMS
    await send_otp_email(email, otp_code)
    return {"message": "OTP generated and sent", "email": email}


@app.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.otp != otp or user.otp_expires < datetime.now():
        return {"status": "failed", "message": "Invalid OTP"}

    return {"status": "success", "message": "Login successful"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
