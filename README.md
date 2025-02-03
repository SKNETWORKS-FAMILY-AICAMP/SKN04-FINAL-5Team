## 서버실행
uvicorn app.main:app --reload

## 테스트:
/token: 로그인 엔드포인트 테스트.
/chatbot: 챗봇 연동 테스트.

# intall
conda install -c pytorch faiss-cpu
conda install -c conda-forge pymupdf

## OAuth2PasswordRequestForm
OAuth2PasswordRequestForm는 FastAPI에서 제공하는 기본 폼으로, 로그인 시 username과 password를 수집합니다. 클라이언트는 application/x-www-form-urlencoded 형식으로 요청을 보내야 합니다.

## 테스트 체크리스트
/users/register: 사용자 등록.
/users/login: 사용자 로그인 (JWT 토큰 생성).
/menus/: 사용자 동적 메뉴 가져오기 및 생성.
/chatbot/: ChatGPT와 대화.
위 코드를 통해 사용자는 로그인, 동적 메뉴 접근 및 ChatGPT와의 상호작용을 할 수 있습니다. 로그는 logs/app.log에 기록됩니다.

## 시스템 구조도
fastapi-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── document.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── chatbot_routes.py
│   │   └── docu_routes.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   └── document_schema.py
│   └── services/
│       ├── __init__.py
│       └── chatbot_service.py
├── tests/
│   ├── __init__.py
│   ├── test_user.py
│   └── test_chatbot.py
├── requirements.txt
├── README.md
└── .env

[users]
 - id (PK)
 - username
 - password
 - is_active
 - created_at

[menus]
 - id (PK)
 - title
 - url
 - user_id (FK -> users.id)

[logs]
 - id (PK)
 - event
 - timestamp
