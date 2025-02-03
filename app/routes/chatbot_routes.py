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
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from langchain.chains import RetrievalQA
import numpy as np
from sentence_transformers import SentenceTransformer

# .env 파일 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(SERPER_API_KEY)

persist_directory = "./my_db2"
os.makedirs(persist_directory, exist_ok=True)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = Chroma(collection_name="documents", embedding_function=embeddings, persist_directory=persist_directory)


# router = APIRouter(prefix="/chatbot", tags=["Chatbot"])
router = APIRouter(tags=["Chatbot"])

templates = Jinja2Templates(directory="app/templates")

class ChatMessage(BaseModel):
    message: str

# OpenAI LLM 초기화
llm = ChatOpenAI(temperature=0.1)

# Runnable 정의
llm_runnable = RunnableLambda(lambda x: llm.invoke({"messages": [{"role": "user", "content": x}]}))

# 벡터 스토어 검색기 초기화
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # 검색할 문서 수 설정

# QA 체인 정의
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# embedding_dim = 384  # all-MiniLM-L6-v2 모델의 기본 임베딩 차원

# # 3) 문서 임베딩 미리 계산
# doc_embeddings = embedding_model.encode(documents)
# doc_embeddings = np.array(doc_embeddings, dtype='float32')

# def search_similar_documents(query: str, top_k: int = 3):
#     """
#     query 문자열을 받아 해당 쿼리와 가장 유사한 상위 top_k 문서와
#     유사도 점수를 반환하는 함수
#     """
#     # (1) 쿼리를 벡터화
#     query_embedding = embedding_model.encode([query])
#     query_embedding = np.array(query_embedding, dtype='float32')

#     # (2) FAISS로 상위 top_k 유사 문서 검색
#     #     D: 유사도 점수(Inner Product), I: 인덱스 목록
#     D, I = faiss_index.search(query_embedding, top_k)
    
#     # (3) 결과 정리
#     retrieved_docs = []
#     retrieved_scores = []
#     for idx, score in zip(I[0], D[0]):
#         retrieved_docs.append(documents[idx])
#         retrieved_scores.append(float(score))  # float 변환
    
#     return retrieved_docs, retrieved_scores

def is_relevant(doc, chat_message) -> bool:
    """
    문서가 사용자 입력 메시지와 관련이 있는지 판단하는 함수.
    """
    # 예시: 문서의 내용이 사용자 메시지에 포함되어 있는지 확인
    user_message = chat_message.message.lower()  # 사용자 메시지 소문자로 변환
    doc_content = doc.page_content.lower()  # 문서 내용 소문자로 변환

    # 키워드 매칭 또는 유사도 점수 계산 (여기서는 단순 포함 여부로 판단)
    return user_message in doc_content

def search_similar_documents(query: str, top_k: int = 3):
    """
    주어진 쿼리를 임베딩한 후, 벡터 DB에서 유사도 높은 상위 top_k 문서를 찾는 함수.
    
    :param query: 검색할 쿼리 문자열
    :param top_k: 반환할 상위 문서 수
    :return: (문서 리스트, 유사도 점수 리스트)
    """
    # 쿼리를 임베딩
    query_embedding = embeddings.embed_query(query)  # embeddings 객체를 사용하여 쿼리 임베딩
    query_embedding = np.array(query_embedding, dtype='float32')  # numpy 배열로 변환
    
    result = vectorstore.similarity_search(query_embedding, top_k)  # 유사도 검색 수행

    print("DEBUG: similarity_search result:", result)  # 반환값 출력

    # 벡터 DB에서 상위 top_k 유사 문서 검색
    D, I = vectorstore.similarity_search(query, top_k)  # 유사도 검색 수행

    # 반환값 확인
    print("DEBUG: similarity_search result:", result)  # 반환값 출력

    print("D (scores):", D)  # (1, 2) => [[score1, score2]]
    print("I (indices):", I)  # (1, 2) => [[idx1, idx2]]
    
    print('--------------------------------------2')

    # 결과 정리
    retrieved_docs = []
    retrieved_scores = []

    print('--------------------------------------3')
    for idx, score in zip(I[0], D[0]):
        retrieved_docs.append(vectorstore.get_document(idx))  # 문서 가져오기
        retrieved_scores.append(float(score))  # 유사도 점수 변환

    print('--------------------------------------4')

    return retrieved_docs, retrieved_scores

def retrieverSearch(message: str) -> str:

    # 벡터 DB에서 검색
    print(f"DEBUG: Attempting to retrieve vector DB data for message: {message}")
    results = retriever.invoke(message)
    print(f"DEBUG: Retrieved results - {results}")    
    
    combined_results = "\n".join([doc.page_content for doc in results])  # 각 Document의 page_content를 결합
    print(f"DEBUG: Retrieved combined_results - {combined_results}")

    prompt = f"""
    You are a summarization model. Please summarize the following content in a clear and concise manner:
    {combined_results}
    """
    # LLM에 벡터 DB 결과를 전달하여 요약
    summarized_response = llm.invoke({"messages": [{"role": "user", "content": prompt}]})
    print(f"DEBUG: LLM summarized response - {summarized_response}")

    return summarized_response

def retrieverGptSearch(message: str) -> str:
    # 벡터 DB에서 결과가 없을 경우 ChatGPT 직접 사용
    print("DEBUG: No relevant data in vector DB. Using LLM for direct response.")
    response = qa_chain.invoke({"query": message})
    reply = response.get("result", "관련된 답변을 찾을 수 없습니다.")
    print(f"DEBUG: QA Chain response - {reply}")
    return reply

@router.post("/api/chatbot")
async def chatgpt(chat_message: ChatMessage):
    print(f"DEBUG: Received message - {chat_message.message}")

    message = chat_message.message.strip()
    
    if not message:
        print("DEBUG: Empty message received.")
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")

    try:

        # 1. 벡터 검색: 임베딩 후 벡터 DB에서 유사도 높은 문서 찾기
        docs, similarity_scores = search_similar_documents(message, top_k=3)
        print("docs-->", docs)
        print("similarity_scores-->", similarity_scores)

        # 2. 임계값 판단 로직(예: 0.8)
        threshold = 0.5
        if len(docs) > 0 and max(similarity_scores) >= threshold:

            summarized_response = retrieverSearch(docs)
            
            return {
                "output": {
                    "result": summarized_response,
                    "source": "벡터 DB에서 조회된 데이터"
                }
            } 
            
        else:

            reply = retrieverGptSearch(message)
            
            return {
                "output": {
                        "result": reply,
                        "source": "ChatGPT에서 생성된 답변"
                    }
                }

    except Exception as e:
        print(f"ERROR: Exception occurred - {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

def process_vector_db_results(results: list) -> str:
    """
    벡터 DB에서 가져온 결과를 요약하고 출처를 포함한 문자열로 반환.
    """
    from collections import Counter

    if not results:
        return "검색 결과가 없습니다."

    # 문서 내용과 출처 추출
    all_sentences = []
    sources = []
    for doc in results:
        if hasattr(doc, 'page_content') and doc.page_content:
            all_sentences.extend(doc.page_content.split("\n"))
        if hasattr(doc, 'metadata') and 'source' in doc.metadata:
            sources.append(doc.metadata['source'])

    # 중복 제거 및 요약
    unique_sentences = Counter(all_sentences)
    top_sentences = sorted(unique_sentences.items(), key=lambda x: -x[1])[:10]
    summarized_results = "\n".join(
        [f"{i+1}. {sentence.strip()}" for i, (sentence, _) in enumerate(top_sentences)]
    )  + "\n"  # 마지막에 엔터 추가

    # 출처 정리
    unique_sources = set(sources)
    source_info = "\n".join([f"출처 {i+1}: {src}" for i, src in enumerate(unique_sources)])

    return f"{summarized_results}\n\n{source_info or '출처 정보가 없습니다.'}"

# def get_vector_db_response(message: str):
#     """
#     벡터 DB에서 메시지와 관련된 데이터를 검색
#     """
#     try:
#         print(f"DEBUG: Attempting to retrieve vector DB data for message: {message}")

#         # 메시지 유효성 검사
#         if not isinstance(message, str) or not message.strip():
#             print('DEBUG: Invalid message input')
#             raise ValueError("Message must be a non-empty string")

#         # retriever 초기화 상태 확인
#         if retriever is None:
#             print('DEBUG: Retriever not initialized')
#             raise ValueError("Retriever is not initialized.")

#         # retriever.invoke 호출
#         print(f"DEBUG: Querying retriever with message: {message}")

#         results = retriever.invoke(message)
#         print(f"DEBUG: Retrieved results - {results}")

#         print('----------------------------------------2-3')
#         if results:
#             # 검색된 문서 내용을 요약 가능하도록 가공
#             # raw_results = "\n\n".join([result.page_content for result in results])
#             # if not raw_results:
#                 # print("DEBUG: No valid page_content in results")
#                 # return "검색 결과는 있지만 유효한 데이터를 찾을 수 없습니다."

#             # return format_vector_results_for_llm(results)
#             return results
#         else:
#             print("DEBUG: No results found in vector DB.")
#             return "관련된 데이터가 없습니다."

#     except Exception as e:
#         print('----------------------------------------3')
#         print(f"ERROR: Failed to retrieve data from vector DB - {e}")
#         return f"벡터 DB 검색 중 오류 발생: {str(e)}"


# def format_vector_results_for_llm(documents: list) -> str:
#     """
#     벡터 DB 검색 결과를 요약 및 출처 정보 추가
#     """
#     from collections import Counter

#     if not documents:
#         return "검색 결과가 없습니다."

#     # 문서 내용을 결합하고 중복 제거
#     all_sentences = []
#     sources = []
#     for doc in documents:
#         # 문서 내용 추가
#         if hasattr(doc, 'page_content') and doc.page_content:
#             all_sentences.extend(doc.page_content.split("\n"))
        
#         # 출처 정보 추가
#         if hasattr(doc, 'metadata') and 'source' in doc.metadata:
#             sources.append(doc.metadata['source'])

#     # 중복 제거 및 상위 문장 선택
#     unique_sentences = Counter(all_sentences)
#     top_sentences = sorted(unique_sentences.items(), key=lambda x: -x[1])[:5]
#     summarized_results = "\n".join(
#         [f"{i+1}. {sentence.strip()}" for i, (sentence, _) in enumerate(top_sentences)]
#     )

#     # 출처 목록 정리
#     # unique_sources = set(sources)
#     # source_info = "\n".join([f"출처 {i+1}: {src}" for i, src in enumerate(unique_sources)])
    
#     # 출처 추가
#     sources = "\n".join(
#         [f"출처 {i+1}: {doc.metadata.get('source', '알 수 없음')}" for i, doc in enumerate(documents) if hasattr(doc, 'metadata')]
#     )

#     return f"{summarized_results}\n\n{sources or '출처 정보가 없습니다.'}"

@router.get("/chatbot", response_class=HTMLResponse)
async def get_chatbot_page(request: Request):
    return templates.TemplateResponse(
        "chatbot/chatbot.html", {
        "request": request,
        "page_title": "Retriver Checkbot",
        "active_menu": "checkbot",
        "show_cards": False,  # 대시보드 카드 표시 여부
    })
