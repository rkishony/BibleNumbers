import re



# Example usage
s = "הוּא וַאֲנָשִׁים--מִיהוּדָה"
tokens = tokenize(s)
reconstructed = reconstruct(tokens)

# Separate into words and separators for display
words = [part for t, part in tokens if t == "word"]
separators = [part for t, part in tokens if t == "separator"]

print("Tokens:", tokens)
print("Words:", words)
print("Separators:", separators)
print("Reconstructed:", reconstructed)
