from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from langchain_core.documents import Document  # 필요시 import 확인
# from app.models import Document
from app.utils import embed_pdf, check_duplicate
from fastapi import Request, Depends, APIRouter
import os
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import uuid
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from fastapi.responses import RedirectResponse
from fastapi import Request
import PyPDF2
from datetime import datetime, timezone 
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Documents"])
templates = Jinja2Templates(directory="app/templates")


# .env 파일 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Chroma DB 초기화
# "db" 디렉토리에 벡터 데이터 저장
persist_directory = "./my_db2"
os.makedirs(persist_directory, exist_ok=True)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = Chroma(collection_name="documents", embedding_function=embeddings, persist_directory=persist_directory)
    
@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("documents/upload.html", {"request": request})

# 벡터 임베딩 리스트 조회
@router.get("/docu_list", response_class=HTMLResponse)
async def docu_list(request: Request):
    return templates.TemplateResponse("documents/docu_list.html", {"request": request})
 
def dataConv(documents: str):
    # 문서명으로 유니크한 값만 추출
    unique_documents = {doc['source']: doc for doc in documents}.values()

    # 문서 목록을 업로드 시간 기준으로 정렬
    sorted_documents = sorted(unique_documents, key=lambda doc: doc['upload_time'])

    # 업로드 시간을 원하는 형식으로 변경
    i = 1;
    for doc in sorted_documents:
        doc['no'] = i
        doc['upload_time'] = datetime.fromisoformat(doc['upload_time']).strftime('%Y-%m-%d %H:%M:%S')
        i += 1
        
    return sorted_documents   


# 요청 모델 정의
class DeleteRequest(BaseModel):
    doc_ids: List[str]

@router.delete("/docu_del")
async def docu_del(request: DeleteRequest):

    # 삭제 처리
    for doc_id in request.doc_ids:
        result = deleteVectorDB(doc_id)
        if ( result ):
            print('Success')
        else:
            print('Fail')
    
    return {"message": "문서가 성공적으로 삭제되었습니다."}    
    print('delete:-----------------------------1', doc_id)
    # print('docu_del-vectorstore.get():', vectorstore.get())

def deleteVectorDB(doc_id: str):
    # 데이터베이스에서 문서 삭제
    result = vectorstore.get(where={"doc_id": doc_id})  # 문서 ID로 문서 검색

    if result is None or len(result['metadatas']) == 0:
        print(f"문서 ID {doc_id}를 찾을 수 없습니다.")
        return False  # 문서가 존재하지 않으면 False 반환

    try:
        # 문서 삭제 로직
        remaining_docs = vectorstore.delete(where={"doc_id": doc_id})  # doc_id로 문서 삭제
        vectorstore.persist()
        if not remaining_docs:  # 문서가 존재하지 않으면 삭제 성공
            print(f"문서 ID {doc_id}가 성공적으로 삭제되었습니다.")
            return True
        else:
            print(f"문서 ID {doc_id} 삭제 실패: 여전히 문서가 존재합니다.")
            return False
    except Exception as e:
        print(f"삭제 중 오류 발생: {str(e)}")
        return False
    
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        reader = PyPDF2.PdfReader(file.file)
        text = ""
        total_pages = len(reader.pages)  # 총 페이지 수 계산
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip(), total_pages  # 텍스트와 총 페이지 수 반환
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 읽기 오류: {e}")

# PDF 파일 읽기
def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# 임베딩 저장
def store_embedding(texts):
    vectorstore.add_texts(texts)

def split_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file:
        raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다.")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
    
    # 기존 문서 확인
    query_result = vectorstore.get(where={"source": file.filename})

    if query_result is None or 'documents' not in query_result:
        return {"message": "문서 확인 중 오류가 발생했습니다."}

    print('len(query_result[documents])', len(query_result['documents']))
    # print('query_result[documents]', query_result['documents'])

    if len(query_result['documents']) > 0:
        # return {"message": "이미 업로드된 문서입니다."}
        return JSONResponse(content={"message": "이미 업로드된 문서입니다.", "filename": file.filename})
        # return {"message": "이미 업로드된 문서입니다."}

    # 1. 텍스트 추출 및 총 페이지 수 가져오기
    text, total_pages = extract_text_from_pdf(file)
    if not text:
        return {"message": "PDF에서 텍스트를 추출할 수 없습니다."}

    # 텍스트 분할 및 저장
    chunks = split_text(text)
    # store_embedding(chunks)  # 분할된 텍스트를 임베딩으로 저장
    
    # 문서 ID 생성
    doc_id = str(uuid.uuid4())  # 문서 ID
    upload_time = datetime.now(timezone.utc).isoformat()  # 업로드 시간
    metadata = {
        "source": file.filename,
        "doc_id": doc_id,
        "upload_time": upload_time,
        "total_pages": total_pages  # 총 페이지 수 추가
    }

    # 청크별로 메타데이터와 함께 DB에 삽입 (chunk_id 추가)
    docs = [
        Document(
            page_content=c,  # 청크 내용
            metadata={
                **metadata,  # 공통 메타데이터 포함
                "chunk_id": f"{doc_id}-{i+1}"  # 문서 ID와 청크 순서 번호 결합
            }
        )
        for i, c in enumerate(chunks)  # chunks는 PDF에서 추출한 텍스트 청크
    ]  
    
    vectorstore.add_documents(docs)
    vectorstore.persist()

    return {"message": "파일이 성공적으로 업로드되었습니다."}

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@router.post("/search")
async def search(request: SearchRequest):
    """
    쿼리 문장에 대해 유사한 문서 청크 검색
    """
    query = request.query
    k = request.k
    
    print('query:', query)

    # if not query:
    #     raise HTTPException(status_code=400, detail="쿼리를 입력해주세요.")

    if not query:
        results = vectorstore.get()  # 모든 문서 가져오기
    else:    
        results = vectorstore.get(
            where={"source": query}
        )
    
    response = []
    seen_doc_ids = set()  # 중복된 doc_id를 추적하기 위한 집합

    for r in results['metadatas']:
        
        doc_id = r.get('doc_id', None)
        if doc_id is None:
            continue

        # doc_id가 이미 seen_doc_ids에 있는지 확인
        if doc_id not in seen_doc_ids:
            seen_doc_ids.add(doc_id)  # doc_id를 집합에 추가
            response.append({
                "doc_id": doc_id,
                "source": r['source'],
                "total_pages": r['total_pages'],
                "upload_time": r['upload_time'],
            })

    return {"results": response}
