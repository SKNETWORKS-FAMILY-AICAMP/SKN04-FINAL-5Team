from fastapi import APIRouter, HTTPException, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends, APIRouter
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from fastapi import Request
from typing import List
import bcrypt
import logging
import psycopg2
from sqlalchemy import text
from datetime import datetime
from pydantic import BaseModel


router = APIRouter(tags=["Users"])

templates = Jinja2Templates(directory="app/templates")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 사용자 리스트 조회
@router.get("/users/listview", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("user/user_manager.html", {"request": request, "users": users})

def strToDate(strDate):
    if strDate and len(strDate) == 8:  # "YYYYMMDD" 형식 확인
        str_dt = f"{strDate[:4]}-{strDate[4:6]}-{strDate[6:]}"  # "YYYY-MM-DD" 형식으로 변경
        str_dt = datetime.strptime(str_dt, "%Y-%m-%d").date() 
    else:
        str_dt

    return str_dt
 

@router.get("/users/list")
def get_users(request: Request, db: Session = Depends(get_db)):

    # 쿼리 파라미터를 Request 객체에서 가져오기
    username = request.query_params.get("username")
    user_id = request.query_params.get("user_id")
    start_dt = request.query_params.get("start_dt")
    
    # 쿼리 파라미터를 사용하여 사용자 목록을 필터링하는 로직       
    query = "SELECT * FROM users WHERE 1=1"
    # SQL 쿼리 및 파라미터 초기화
    query = """
        SELECT * FROM users WHERE 1=1
    """
    params = {}

    # 동적으로 조건 추가
    if username:
        query += " AND username ILIKE :username"
        params["username"] = f"%{username}%"
    if user_id:
        query += " AND user_id = :user_id"
        params["user_id"] = user_id
    if start_dt:
        start_dt = start_dt.replace('-','')
        query += " AND start_dt = :start_dt"
        params["start_dt"] = start_dt

    query += " ORDER BY username"
    
    # ... 기존 코드 ...
    # SQLAlchemy에서 raw SQL 실행
    result = db.execute(text(query), params)
    users = result.fetchall()
        #    return users 
    print('users:', users)
    
    response = []       

    for user in users:
        # created_at = user[6].strftime("%Y-%m-%d")
        
        start_dt = strToDate(user[8])
        print('start_dt:' , start_dt)
        response.append({
            "id": user[0],          # user_id
            "user_id": user[1],     # user_id
            "email": user[4],       # email
            "username": user[2],    # username
            "start_dt": start_dt,   # start_dt
        })        
    
    return {"results": response}   
 
# 사용자 
@router.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # created_at = user.created_at.strftime('%Y-%m-%d');
    start_dt = strToDate(user.start_dt)
    
    return {
        "id": user.id,
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "start_dt": start_dt,
    }
     
# API to delete a user by ID
@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):

    # SQLAlchemy에서 직접 SQL 쿼리 실행
    result = db.execute(text("DELETE FROM users WHERE id = :id RETURNING id"), {"id": id})
    deleted_id = result.fetchone()
    
    if not deleted_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.commit()
    return {"message": f"User with ID {id} has been deleted"}    
       
   
class UserRegister(BaseModel):
    user_id: str
    username: str
    password: str
    email: str
    start_dt: str   
           
# 사용자 등록 처리
@router.post("/users/save")
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    
    print('user_id:' , user.user_id)
    print('username:' , user.username)
    print('password:' , user.password)
    print('email:' , user.email)
    print('start_dt:' , user.start_dt)
    
    try:
        
        # 사용자 이름 중복 확인
        userinfo = db.query(User).filter(User.user_id == user.user_id).first()
        start_dt = user.start_dt.replace('-','')
        
        if userinfo:
            
            # 기존 사용자 업데이트
            userinfo.username = user.username
            userinfo.email = user.email
            userinfo.user_id = user.user_id
            userinfo.password = hash_password(user.password)  # 비밀번호 해시화
            userinfo.start_dt = start_dt  # 필요 시 업데이트
            db.commit()
            
            return {"message": "User updated successfully!"}

        else:
                          
            # 비밀번호 해시화 및 사용자 추가
            hashed_password = hash_password(user.password)
            new_user = User(
                user_id=user.user_id, 
                username=user.username, 
                email=user.email, 
                password=hashed_password,     
                start_dt=start_dt,     
            )
            print('register_user new_user:', new_user)

            db.add(new_user)
            db.commit()

            return {"message": "User registered successfully"}

    except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
    
    # except Exception as e:
        # return (f"message:", {e})  # 오류 출력
        # raise HTTPException(status_code=500, detail="Internal Server Error")       

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
