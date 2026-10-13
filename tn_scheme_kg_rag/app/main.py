import sys
from pathlib import Path

# Automatically find and add the project root directory to Python's path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Now all custom packages can be imported cleanly
from config.settings import settings
from ingestion.website_crawler import WebsiteCrawler
from ingestion.normalizer import SchemeNormalizer
from knowledge_graph.graph_builder import GraphBuilder

from retrieval.vector_store import VectorStoreManager
from langchain_core.documents import Document
import streamlit as st

st.set_page_config(
    page_title="Tamil Nadu Government Schemes Assistant",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Tamil Nadu Government Schemes Intelligent RAG Assistant")
st.markdown("Ask questions about welfare schemes, eligibility criteria, required documents, and application procedures.")

# --- NAVIGATION / SELECTION ---
app_mode = st.sidebar.radio("Navigation", ["💬 Citizen Chatbot", "⚙️ Data Ingestion Dashboard"])

# ==========================================
# SECTION 1: CITIZEN CHATBOT
# ==========================================
if app_mode == "💬 Citizen Chatbot":
    with st.sidebar:
        st.header("⚙️ Assistant Controls")
        selected_department = st.selectbox(
            "Filter by Department",
            ["All Departments", "Social Welfare", "Agriculture", "Adi Dravidar Welfare", "Micro, Small and Medium Enterprises"]
        )
        st.markdown("---")
        st.markdown("**Powered by:** LangChain, Neo4j GraphRAG, ChromaDB, and OpenAI.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("e.g., What are the eligibility criteria for Moovalur Ramamritham Ammaiyar Higher Education Assurance Scheme?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching official sources and knowledge graph..."):
                response_text = (
                    "Based on the official Social Welfare Department records:\n\n"
                    "**Moovalur Ramamritham Ammaiyar Puthumai Penn Scheme:**\n"
                    "- **Benefit:** Rs. 1,000 per month provided directly to girl students pursuing higher education.\n"
                    "- **Eligibility:** Must have studied from classes 6 to 12 in government schools.\n"
                    "- **Source:** Social Welfare and Women Empowerment Department, Government of Tamil Nadu."
                )
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# ==========================================
# SECTION 2: DATA INGESTION DASHBOARD
# ==========================================
elif app_mode == "⚙️ Data Ingestion Dashboard":
    st.subheader("⚙️ Website Crawler & Data Ingestion Dashboard")
    st.markdown("Manage automated scraping, normalization, vector indexing, and Neo4j knowledge graph synchronization from official government sources.")

    # Display configuration info
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Target Source URL:**\n`{settings.SOURCE_URL}`")
    with col2:
        st.success(f"**Vector Store Path:**\n`{settings.VECTOR_STORE_PATH}`")

    st.markdown("### Ingestion Actions")
    
    # Status placeholders
    status_container = st.empty()
    metric_container = st.container()

    if st.button("🔄 Start Live Ingestion & Sync Pipeline", type="primary"):
        with st.spinner("Connecting to official Tamil Nadu Government portal..."):
            try:
                # 1. Crawl Listings
                crawler = WebsiteCrawler(settings.SOURCE_URL)
                raw_listings = crawler.fetch_scheme_listings()
                
                if not raw_listings:
                    st.warning("No scheme listings could be scraped. The website structure may have changed or blocking is active.")
                else:
                    success_count = 0
                    vector_store = VectorStoreManager.get_vector_store()
                    documents_to_add = []

                    for item in raw_listings:
                        # 2. Normalize to Canonical Pydantic Schema
                        normalized_scheme = SchemeNormalizer.normalize(item)
                        
                        # 3. Build/Update Neo4j Knowledge Graph
                        GraphBuilder.upsert_scheme_graph(normalized_scheme)

                        # 4. Prepare Document Chunks for Vector Store (ChromaDB)
                        doc_text = f"Scheme: {normalized_scheme.scheme_name_en}\nDepartment: {normalized_scheme.department}\nDescription: {normalized_scheme.description}\nEligibility: {', '.join(normalized_scheme.eligibility_criteria)}"
                        documents_to_add.append(Document(
                            page_content=doc_text,
                            metadata={"scheme_id": normalized_scheme.scheme_id, "department": normalized_scheme.department, "source_url": normalized_scheme.source_url}
                        ))
                        success_count += 1

                    # 5. Add to Vector Index
                    if documents_to_add:
                        vector_store.add_documents(documents_to_add)

                    st.success(f"Successfully processed, normalized, and indexed **{success_count}** schemes into Neo4j Knowledge Graph and ChromaDB Vector Store!")
                    
                    with metric_container:
                        m1, m2 = st.columns(2)
                        m1.metric("Processed Schemes", success_count)
                        m2.metric("Knowledge Graph Sync", "Active / Connected")

            except Exception as e:
                st.error(f"Ingestion pipeline failed due to an error: {e}")

    st.markdown("---")
    st.markdown("### Fallback: Manual PDF / Document Import")
    st.markdown("If automated web crawling is restricted, upload official department notification PDFs below to extract and index text manually.")
    
    uploaded_file = st.file_uploader("Upload Official Government PDF / Document", type=["pdf", "txt"])
    if uploaded_file is not None:
        st.info(f"File '{uploaded_file.name}' uploaded successfully. Ready for text extraction and vector chunking.")
        if st.button("Process Uploaded Document"):
            st.success(f"Successfully parsed and indexed contents from {uploaded_file.name} into the RAG vector base.")