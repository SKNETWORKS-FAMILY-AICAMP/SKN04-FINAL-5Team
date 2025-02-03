from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Menu
from app.utils import log_event
from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends, APIRouter
import os

# 현재 파일의 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/menus", tags=["Menus"])

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/")
def get_dynamic_menu(user_id: int, db: Session = Depends(get_db)):
    menus = db.query(Menu).filter(Menu.user_id == user_id).all()
    log_event(f"Retrieved menus for user_id {user_id}")
    return {"menus": [{"id": menu.id, "title": menu.title, "url": menu.url} for menu in menus]}

@router.post("/")
def create_menu(title: str, url: str, user_id: int, db: Session = Depends(get_db)):
    new_menu = Menu(title=title, url=url, user_id=user_id)
    db.add(new_menu)
    db.commit()
    log_event(f"Created menu {title} for user_id {user_id}")
    return {"message": "Menu created successfully"}

@router.get("/buttons")
async def buttons(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Buttons",
        "active_menu": "buttons",
        "show_cards": False
    })

@router.get("/cards")
async def cards(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Cards",
        "active_menu": "cards",
        "show_cards": True
    })
    
@router.get("/sales")
async def cards(request: Request):
    return templates.TemplateResponse("login/login.html", {
        "request": request,
        "page_title": "sales",
        "active_menu": "sales",
        "show_cards": True
    })    

@router.get("/utilities-color")
async def utilities_color(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Colors",
        "active_menu": "utilities-color",
        "show_cards": False
    })

@router.get("/utilities-border")
async def utilities_border(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Borders",
        "active_menu": "utilities-border",
        "show_cards": False
    })

@router.get("/utilities-animation")
async def utilities_animation(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Animations",
        "active_menu": "utilities-animation",
        "show_cards": False
    })

@router.get("/utilities-other")
async def utilities_other(request: Request):
    return templates.TemplateResponse("layouts/main.html", {
        "request": request,
        "page_title": "Other Utilities",
        "active_menu": "utilities-other",
        "show_cards": False
    })