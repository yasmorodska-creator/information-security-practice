from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import UserCreate, UserResponse, TokenResponse, TokenRefreshRequest, UserInfo
from app.security import hash_password, verify_password

# Imports for audit and security
from app.audit.detector import check_brute_force
from app.audit.logger import log_login_failed, log_login_success

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    new_user = User(
        username=user_data.username, 
        email=user_data.email, 
        full_name=user_data.full_name, 
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: Request, credentials: dict, db: Session = Depends(get_db)):
    ip = request.client.host
    username = credentials.get("username")
    
    # 1. Brute Force check BEFORE database verification
    if check_brute_force(db, ip):
        log_login_failed(db, username, ip, "brute_force_blocked")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Too many failed attempts. Try again later."
        )

    # 2. User lookup and password verification
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(credentials.get("password"), user.password_hash):
        log_login_failed(db, username, ip, "invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password"
        )

    # 3. Logging successful login
    log_login_success(db, user.id, user.username, ip)

    # 4. Token generation
    role = user.roles[0].name if user.roles else "student"
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required, not access token")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = user.roles[0].name if user.roles else "student"
    return TokenResponse(
        access_token=create_access_token(user_id, role), 
        refresh_token=create_refresh_token(user_id)
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id, 
        username=current_user.username, 
        email=current_user.email, 
        full_name=current_user.full_name, 
        role=role
    )