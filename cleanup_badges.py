import os
import shutil
import json
import re

source_dir = r"D:\coduku-private-\frontend\public\badge"
dest_dir = r"D:\coduku-private-\frontend\public\clean-badges"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

mappings = {}

for root, dirs, files in os.walk(source_dir):
    for filename in files:
        old_path = os.path.join(root, filename)
        
        # relative path from source_dir
        rel_path = os.path.relpath(old_path, source_dir)
        folder = os.path.dirname(rel_path)
        
        clean_folder = slugify(folder)
        base, ext = os.path.splitext(filename)
        clean_filename = f"{slugify(base)}{ext.lower()}"
        
        new_folder_path = os.path.join(dest_dir, clean_folder)
        os.makedirs(new_folder_path, exist_ok=True)
        
        new_path = os.path.join(new_folder_path, clean_filename)
        shutil.copy2(old_path, new_path)
        
        url_path = f"/clean-badges/{clean_folder}/{clean_filename}"
        mappings[os.path.join(folder, filename)] = url_path

with open("D:\coduku-private-\mapping.json", "w") as f:
    json.dump(mappings, f, indent=2)
