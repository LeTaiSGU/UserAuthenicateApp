from datetime import timedelta
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models, utils, database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from app.auth.dependencies import ALGORITHM, SECRET_KEY, get_current_user
from app import email_utils
from fastapi import Request
from urllib.parse import urlencode
from jose import JWTError, jwt
from app.auth.google_auth import oauth
from app.log_utils import log_login


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), request: Request = None):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)
    # Tạo token chứa thông tin user
    token = utils.create_access_token(data={
        "sub": user.email,
        "hashed_password": hashed_password
    })
    verify_url = f"{request.base_url}auth/verify-email?{urlencode({'token': token})}"

    html = f"""
    <h3>Chào mừng {user.email}</h3>
    <p>Vui lòng xác minh tài khoản bằng cách nhấn vào link bên dưới:</p>
    <a href="{verify_url}">Xác minh tài khoản</a>
    """

    email_utils.send_email(user.email, "Xác minh tài khoản", html)

    # Trả về thông báo (không trả về user vì chưa có user trong DB)
    return {"msg": "Vui lòng kiểm tra email để xác minh tài khoản."}

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    try:
        payload = utils.jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        email = payload.get("sub")
        hashed_password = payload.get("hashed_password")
    except Exception:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc đã hết hạn.")

    # Kiểm tra user đã tồn tại chưa
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        if user.is_verified:
            return {"message": "Tài khoản đã được xác minh trước đó."}
        user.is_verified = True
        user.is_active = True
        db.commit()
        return {"message": "Xác minh thành công! Bạn có thể đăng nhập."}

    # Nếu chưa có user, tạo mới và xác minh luôn
    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Xác minh thành công! Bạn có thể đăng nhập."}

@router.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db), request: Request = None):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access_token = utils.create_access_token(data={"sub": user.email})
    
    log_login(user.email, request, method="manual")

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def get_me(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = utils.jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/forgot-password", summary="Yêu cầu reset mật khẩu")
def forgot_password(data: schemas.ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    token = utils.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=15))
    reset_link = f"http://localhost:8000/reset-password?token={token}"

    html = f"""
    <h3>Đặt lại mật khẩu</h3>
    <p>Bấm vào liên kết dưới để đặt lại mật khẩu (hết hạn sau 15 phút):</p>
    <a href="{reset_link}">{reset_link}</a>
    """

    email_utils.send_email(user.email, "Reset mật khẩu", html)
    return {"msg": "Đã gửi email reset mật khẩu nếu email tồn tại."}

@router.post("/reset-password", summary="Reset mật khẩu bằng token")
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc hết hạn")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    user.hashed_password = utils.get_password_hash(data.new_password)
    db.commit()

    return {"msg": "Mật khẩu đã được cập nhật thành công"}

@router.get("/users", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.hashed_password = utils.get_password_hash(user_update.password)
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)
    return user

@router.get("/google-login")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", response_model=schemas.Token)
async def google_callback(request: Request, db: Session = Depends(database.get_db)):
    print("SESSION:", request.session)
    print("STATE FROM QUERY:", request.query_params.get("state"))
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.userinfo(token=token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Xác thực Google thất bại")

    email = user_info["email"]

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, hashed_password="", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = utils.create_access_token({"sub": user.email})
    log_login(user.email, request, method="google")
    return {"access_token": jwt_token, "token_type": "bearer"}