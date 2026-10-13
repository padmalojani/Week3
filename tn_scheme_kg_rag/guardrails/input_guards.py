import re

class InputGuard:
    @staticmethod
    def inspect_prompt(text: str) -> bool:
        injection_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"reveal credentials",
            r"you are now DAN"
        ]
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True