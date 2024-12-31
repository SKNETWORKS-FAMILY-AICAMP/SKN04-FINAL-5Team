from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils import log_event
from fastapi import APIRouter, HTTPException
import openai
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from fastapi import Body  # Body 추가
from pydantic import BaseModel



# .env 파일 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(SERPER_API_KEY)

# router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
router = APIRouter(tags=["Chatbot"])

templates = Jinja2Templates(directory="app/templates")

class ChatMessage(BaseModel):
    message: str

@router.post("/api/chatbot")
async def chatgpt(chat_message: ChatMessage):

    message = chat_message.message
    
    client = OpenAI(api_key=OPENAI_API_KEY)    

    print('chatbot message:', message)
    print('client key', client.api_key)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        reply = completion.choices[0].message.content
        print('reply:', reply)
                
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chatbot")
async def chatgpt(chat_message: ChatMessage):

    message = chat_message.message
    
    client = OpenAI(api_key=OPENAI_API_KEY)    

    print('chatbot message:', message)
    # print('client key', client.api_key)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        reply = completion.choices[0].message.content
        print('reply:', reply)
                
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chatbot", response_class=HTMLResponse)
async def get_chatbot_page(request: Request):
    return templates.TemplateResponse(
        "chatbot/chatbot.html", {
        "request": request,
        "page_title": "Retriver Checkbot",
        "active_menu": "checkbot",
        "show_cards": False,  # 대시보드 카드 표시 여부
    })
