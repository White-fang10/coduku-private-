import json
import re

with open(r"D:\coduku-private-\mapping.json", "r") as f:
    mapping = json.load(f)

# Normalize mapping keys to use forward slashes
normalized_mapping = {}
for k, v in mapping.items():
    normalized_mapping[k.replace("\\", "/")] = v

badges_js_path = r"D:\coduku-private-\frontend\src\pages\Badges.js"
with open(badges_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# We look for /badge/... and replace it if it's in the mapping
def replace_match(m):
    original_path = m.group(1) # e.g. STREAK-BASED BADGES/first-spark.jpg
    if original_path in normalized_mapping:
        return normalized_mapping[original_path]
    return m.group(0) # fallback

new_content = re.sub(r'/badge/([^"\'\n]+)', replace_match, content)

with open(badges_js_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Replacement complete.")
