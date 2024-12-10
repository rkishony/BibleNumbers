str1 = 'שִׁשִּׁים'  # Chirik first, then Dagesh
str2 = 'שִׁשִּׁים'  # Dagesh first, then Chirik

print(str1 == str2)  # False, because the order of marks differs

import unicodedata

# Normalize both strings
str1_normalized = unicodedata.normalize('NFC', str1)
str2_normalized = unicodedata.normalize('NFC', str2)

print(str1 == str1_normalized)  # True, after normalization
print(str2 == str2_normalized)  # True, after normalization
