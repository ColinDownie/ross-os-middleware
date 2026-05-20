import re

class RossNormalizer:
    @staticmethod
    def sanitize_lexical_noise(raw_text: str) -> str:
        """
        Rule Group A: Strips conversational padding, markdown markers, 
        emojis, and enforces whitespace flattening.
        """
        if not raw_text:
            return ""
            
        # Remove common markdown symbols (*, _, `, #, -, >)
        clean = re.sub(r"[\*\_`#\-\>]", "", raw_text)
        
        # Strip common emojis and non-standard symbols via regex range
        clean = re.sub(r"[\u2000-\u3300]||[\ud83c-\udfff]", "", clean)
        
        # Flatten multi-spaces, tabs, and newlines into a single space
        clean = re.sub(r"\s+", " ", clean).strip()
        
        # Enforce clean UTF-8 sequence
        return clean.encode("utf-8", errors="ignore").decode("utf-8")

    @classmethod
    def compile_canonical_string(cls, primary_action: str, variables: dict) -> str:
        """
        Rule Group C: Formats clean data into the absolute system string template:
        [Action]. [Parameter 1]: [Value 1]. [Parameter 2]: [Value 2].
        """
        # Format action from UPPERCASE_SNAKE to Title Case spaces
        action_display = primary_action.replace("_", " ").title()
        
        # Map out and sort variables to avoid sequence drift
        kv_pairs = []
        for key in sorted(variables.keys()):
            val = variables[key]
            kv_pairs.append(f"{key.capitalize()}: {val}")
            
        if kv_pairs:
            return f"{action_display}. {'. '.join(kv_pairs)}."
        return f"{action_display}."
