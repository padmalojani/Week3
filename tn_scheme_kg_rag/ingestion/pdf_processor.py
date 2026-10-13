import os
from langchain_community.document_loaders import PyPDFLoader
from typing import List

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> List[str]:
        if not os.path.exists(pdf_path):
            return []
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        return [page.page_content for page in pages]