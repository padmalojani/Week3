from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VectorStoreManager:
    @staticmethod
    def get_vector_store():
        """
        Initializes and returns a persistent ChromaDB vector store 
        using OpenAI embeddings for semantic retrieval.
        """
        try:
            embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL, 
                openai_api_key=settings.OPENAI_API_KEY
            )
            vector_store = Chroma(
                collection_name="tn_schemes_collection",
                embedding_function=embeddings,
                persist_directory=settings.VECTOR_STORE_PATH
            )
            return vector_store
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise e