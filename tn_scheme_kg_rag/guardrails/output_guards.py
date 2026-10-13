from typing import List

class OutputGuard:
    @staticmethod
    def validate_citations(answer_citations: List[str], available_sources: List[str]) -> bool:
        for citation in answer_citations:
            if citation not in available_sources:
                return False
        return True