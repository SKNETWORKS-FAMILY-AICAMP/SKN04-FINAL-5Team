from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from .models import User
from .database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.responses import RedirectResponse

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 암호화 구성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

# 암호화된 비밀번호 생성
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        
        return payload
    except JWTError:
        return None


# 비밀번호 검증 함수
def verify_password(plain_password: str, hashed_password: str):
    try:
        
        print('verify_password plain_password:', plain_password)
        print('verify_password hashed_password:', hashed_password)
        
        # bcrypt 또는 다른 해싱 라이브러리 사용
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"비밀번호 검증 중 오류: {e}")
        return False

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# 사용자 인증 함수 (예시)
def authenticate_user(db: Session, username: str, password: str):

    print('authenticate_user Start')
    try:
        
        print('username:', username)
        print('password:', password)
        
        # 사용자 조회
        user = db.query(User).filter(User.username == username).first()
        # print('authenticate_user user:', user)
        
        if not user:
            print(f"사용자 {username} 찾을 수 없음")
            return None
        
        # 비밀번호 검증 (해시된 비밀번호 사용)
        if not verify_password(password, user.password):
            print(f"사용자 {username} 비밀번호 불일치")
            return None

        return user

    except Exception as e:
        print(f"인증 중 오류 발생: {e}")
        return None

# 액세스 토큰 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        print('encoded_jwt:', encoded_jwt)
        
        return encoded_jwt

    except Exception as e:
        print(f"토큰 생성 중 오류: {e}")
        raise

    
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    # 쿠키에서 JWT 토큰 읽기
    token = request.cookies.get("access_token")

    if not token:
        # raise HTTPException(status_code=401, detail="Not authenticated")
        print('get_current_user_from_cookie ----------------------------------2 ')
        # 토큰 없으면 로그인 페이지로 리다이렉트
        return RedirectResponse(url="/login", status_code=302)    
    
    try:
        # "Bearer <token>" 형식에서 "Bearer " 제거 후 디코딩
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")    