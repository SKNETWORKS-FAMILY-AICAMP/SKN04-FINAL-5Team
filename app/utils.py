from loguru import logger
import PyPDF2
import numpy as np
from app.models import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session
import fitz  # PyMuPDF
from fastapi import File, UploadFile, HTTPException
from PyPDF2 import PdfReader

logger.add("logs/app.log", format="{time} {level} {message}", level="INFO")

# 사전 훈련된 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')  # 경량 모델 사용

def embed_pdf(file):
    try:
        
        print('embed_pdf -------------------------------1-1')
        print('embed_pdf ----------file.name:', file.filename)
        # Validate file type
        if not file.name.endswith('.pdf'):
            raise ValueError("The uploaded file is not a valid PDF.")
        
        print('embed_pdf -------------------------------1-2')
        # Reset the file pointer before reading
        file.seek(0)
        
        # Open the PDF
        print('embed_pdf -------------------------------1-3')
        docs = fitz.open(stream=file.read(), filetype="pdf")
        print('embed_pdf -------------------------------1-4')
        
        text = ""
        
        # Extract text from each page
        for page in docs:
            print('embed_pdf -------------------------------1-53')
            text += page.get_text()  # Extract text
            
        # Handle empty text case
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF.")
        
        print('embed_pdf -------------------------------2')
        
        # Convert text to vector (assumes some_embedding_function is defined)
        vector = some_embedding_function(text)
        print('embed_pdf -------------------------------3')
        
        return vector
    
    except fitz.FitzError as fe:
        print(f"PDF parsing error: {fe}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None

# def embed_pdf(file):
    
#     try:
#         # PDF 파일 읽기
#         print('embed_pdf -------------------------------1')
#         docs = fitz.open(stream=file.read(), filetype="pdf")
        
#         text = ""
#         print('embed_pdf -------------------------------1-1')
        
#         # 각 페이지에서 텍스트 추출
#         for page in docs:
#             print('embed_pdf -------------------------------1-3')
#             text += page.get_text()  # 텍스트 추출
            
#         # 텍스트가 비어 있는 경우 예외 처리
#         if not text.strip():
#             raise ValueError("PDF에서 텍스트를 추출할 수 없습니다.")
        
#         print('embed_pdf -------------------------------2')
        
#         # 텍스트를 벡터로 변환
#         vector = some_embedding_function(text)
#         print('embed_pdf -------------------------------3')
        
#         return vector
    
#     except Exception as e:
#         print(f"오류 발생: {e}")
#         return None

def check_duplicate(db: Session, title: str) -> bool:
    return db.query(Document).filter(Document.title == title).first() is not None

def some_embedding_function(text: str) -> np.ndarray:
    # 텍스트를 벡터로 변환
    embeddings = model.encode(text)
    return embeddings.astype(np.float32)  # FAISS에 적합한 형식으로 변환

def log_event(event: str):
    logger.info(event)

def extract_text_from_pdf1(file: UploadFile) -> str:
    try:
        pdf_reader = PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 읽기 오류: {e}")

