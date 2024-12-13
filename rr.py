import re

def remove_conjugate_letter(token: str, conjugate_letter: str) -> str:
    """
    Removes a leading conjugate letter (e.g., 'ו') and its Nikud from the start of a token.
    """
    # Define a regex pattern for the conjugate letter with optional Nikud
    nikud_pattern = "[\u05B0-\u05BC\u05C1-\u05C2]*"  # Matches any single Hebrew Nikud character (optional)
    pattern = f"^{conjugate_letter}{nikud_pattern}"  # Match the conjugate letter and Nikud at the start only
    # Remove only the leading conjugate letter with Nikud
    result = re.sub(pattern, "", token)
    return result

# Example usage
token = "וְּשְׁלוֹשִׁים"
conjugate_letter = "ו"
result = remove_conjugate_letter(token, conjugate_letter)
print(f"Original: {token}, Without Conjugate: {result}")
assert result == "שְׁלוֹשִׁים"  # Expected: ְּשְׁלוֹשִׁים
