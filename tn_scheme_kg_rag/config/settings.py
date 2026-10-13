import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LangSmith Observability Configuration
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "tn-schemes-rag-production")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    
    # Neo4j Knowledge Graph Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "secure_neo4j_password")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Vector Database & Source Data Configuration
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/chroma_db")
    SOURCE_URL = os.getenv("SOURCE_URL", "https://www.tn.gov.in/scheme_list.php?dep_id=Mg==")
    
    # AI Model Selection
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"

settings = Settings()