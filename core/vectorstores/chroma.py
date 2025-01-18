import json
import pickle
from typing import Callable

from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from langchain.vectorstores import VectorStore


def load_texts():
    with open('saved_raptor_result.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)

    raptor = loaded_dict

    with open('chunked_texts.json', 'r') as f:
        chunked_texts = json.load(f)

    all_texts = chunked_texts.copy()

    for level in sorted(raptor.keys()):
        summaries = raptor[level][1]["summaries"].tolist()
        all_texts.extend(summaries)
    return all_texts


VectorStoreLoader = Callable[[Embeddings, str], VectorStore]


def create_vector_store(
    embeddings: Embeddings,
    chroma_persist_directory: str,
    all_texts: list[str]
) -> VectorStore:
    vectorstore = Chroma.from_texts(
        texts=all_texts,
        embedding=embeddings,
        persist_directory=chroma_persist_directory
    )
    vectorstore.persist()
    return vectorstore


def load_vector_store(embeddings: Embeddings, chroma_persist_directory: str):
    return Chroma(persist_directory=chroma_persist_directory, embedding_function=embeddings)
