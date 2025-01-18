from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_google_vertexai.embeddings import VertexAIEmbeddings


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings()


def get_vertex_ai_embeddings() -> VertexAIEmbeddings:
    return VertexAIEmbeddings(model_name="text-embedding-004")
