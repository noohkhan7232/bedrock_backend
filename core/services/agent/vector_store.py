import threading
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter


_vector_store: Optional[FAISS] = None
_lock = threading.Lock()


def get_embeddings():
  from langchain_openai import OpenAIEmbeddings
  return OpenAIEmbeddings(model='text-embedding-3-small')


def get_source_documents():
  from .documents.overviews import OVERVIEW_DOCUMENTS
  from .documents.about import ABOUT_DOCUMENTS
  from .documents.features import FEATURE_DOCUMENTS
  from .documents.landing import LANDING_DOCUMENTS

  return (
    OVERVIEW_DOCUMENTS
    + ABOUT_DOCUMENTS
    + FEATURE_DOCUMENTS
    + LANDING_DOCUMENTS
  )


def build_vector_store(
  chunk_size: int = 800,
  chunk_overlap: int = 100,
  separators: list[str] = ["\n\n", "\n", ". ", ", ", " "],
) -> FAISS:
  global _vector_store

  documents = get_source_documents()
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=separators,
  )

  vector_store = FAISS.from_documents(
    documents=splitter.split_documents(documents),
    embedding=get_embeddings(),
    distance_strategy=DistanceStrategy.COSINE,
  )

  _vector_store = vector_store
  return vector_store


def get_vector_store() -> FAISS:
  global _vector_store

  # Fast path: already initialized, avoid locking.
  if _vector_store is not None:
    return _vector_store

  with _lock:
    # Double-checked locking:
    # another thread may have initialized it while waiting for the lock.
    if _vector_store is not None:
      return _vector_store

    return build_vector_store()


def get_retriever(**kwargs) -> VectorStoreRetriever:
  return get_vector_store().as_retriever(**kwargs)
