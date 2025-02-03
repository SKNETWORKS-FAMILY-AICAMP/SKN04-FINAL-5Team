import faiss
import numpy as np

def create_faiss_index(dim: int):
    index = faiss.IndexFlatL2(dim)  # L2 거리 기반 인덱스 생성
    return index

def add_vector_to_index(index, vector):
    index.add(np.array([vector], dtype=np.float32))  # 벡터 추가
