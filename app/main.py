from fastapi import FastAPI, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import authenticate_user, create_access_token
from app.database import get_db
from sqlalchemy.orm import Session
from app.routes import user_routes, menu_routes, chatbot_routes, protected_routes
from app.database import Base, engine
from app.auth import get_current_user_from_cookie
from app.models import User
from app.models import Menu
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import Response
from app.routes import docu_routes
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from app.auth import verify_access_token

# OAuth2PasswordBearer를 사용하여 token을 가져옵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

app = FastAPI()

# 테이블 생성
Base.metadata.create_all(bind=engine)

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def check_token_middleware(request: Request, call_next):

    # 로그인 화면으로 리디렉션
    if request.url.path in ["/login", "/users/listview", "/users/save", ]:  # 로그인 페이지와 메인 페이지 허용
        response = await call_next(request)
        return response

    token = request.cookies.get("access_token")

    print('check_token_middleware token:', token)

    # 로그인 화면이 아닌 경우 토큰 검사
    # token = request.headers.get("Authorization")
    if not token or not verify_access_token(token):
        print('check_token_middleware ----------------------- 3-1')
        return RedirectResponse(url="/login")

    response = await call_next(request)

    return response


# 로그인 화면 렌더링
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_action(
    request: Request,  # Request 객체 추가
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    
    try:
        user = authenticate_user(db, username, password)
        if not user:
            # 로그인 실패 시 알림 메시지 추가
            return templates.TemplateResponse("login.html", {
                "request": request,  # request 객체 전달 
                "error_message": "로그인 실패: 사용자 이름 또는 비밀번호가 잘못되었습니다."
            })  # 로그인 실패 시    

        # 액세스 토큰 생성
        access_token = create_access_token(data={"sub": user.username})
        
        # 응답 생성
        response = RedirectResponse(url="/main", status_code=303)  # 로그인 성공 시 메인 화면으로 리다이렉트
        
        # 쿠키에 토큰 설정
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            path="/"
        )

        return response

    except Exception as e:
        # 예외 발생 시 로깅 및 에러 처리
        print(f"로그인 중 오류 발생: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": f"로그인 중 오류가 발생했습니다: {str(e)}"
        })

@app.post("/logout")
async def logout(request: Request):
 
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie(key="access_token", path="/", domain=None)
    
    # 로그인 페이지로 리다이렉트
    return response

@app.get("/protected/")
def protected_page(user: User = Depends(get_current_user_from_cookie)):
    return {"message": f"Hello, {user.username}. You are authenticated!"}

@app.get("/main")
def main_page(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
#     # 쿠키에서 토큰 확인
    token = request.cookies.get("access_token")
    if not token:
        # 토큰 없으면 로그인 페이지로 리다이렉트
        return RedirectResponse(url="/login", status_code=302)

    # 메인 화면 렌더링
    return templates.TemplateResponse(
        "layouts/main.html", {
        "request": request, 
        "username": user.username, 
        # "menus": menu_list,
        "page_title": "Dashboard",
        "active_menu": "dashboard",
        "show_cards": False  # 대시보드 카드 표시 여부    
    })
    
@app.get("/admin")
async def admin_page(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
):
    
     # 쿠키에서 토큰 확인
    token = request.cookies.get("access_token")
    print('token :', token)

    if not token:
        # 토큰 없으면 로그인 페이지로 리다이렉트
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "layouts/main.html", {
        "request": request,
        "page_title": "Dashboard",
        "active_menu": "dashboard",
        "show_cards": False  # 대시보드 카드 표시 여부
    })    


# 라우터 추가
app.include_router(user_routes.router)
app.include_router(menu_routes.router)
app.include_router(chatbot_routes.router)

# 보호된 라우터 등록
app.include_router(protected_routes.router)
# 라우터 등록
app.include_router(docu_routes.router)
