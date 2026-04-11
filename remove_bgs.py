import os
from rembg import remove
from PIL import Image

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                input_path = os.path.join(root, file)
                
                # Check if it already has an alpha channel, to skip if possible,
                # though rembg handles it. We'll just overwrite.
                # Only process if we haven't already. (Maybe rename to _nobg?)
                # Actually, the user says "remove the background of the logo's"
                # so I will just overwrite the file with the transparent version.
                # However, if it's a JPG, it doesn't support transparency. 
                # We need to save as PNG. If it's a jpg, we should save as .png and update references?
                # For badges, there's `first-spark.jpg`. Removing its BG converts it to PNG.
                # Let's just process it to a new file and delete the old one. We'd have to update mapping!
                # Since we already updated mapping.json/Badges.js to point to `first-spark.jpg`, changing to `.png` means we must update `Badges.js` AGAIN.
                # So if we convert a jpg to png, we should replace the file path in Badges.js.
                
                try:
                    with open(input_path, 'rb') as i:
                        input_bytes = i.read()
                    
                    output_bytes = remove(input_bytes)
                    
                    if file.lower().endswith(('.jpg', '.jpeg')):
                        # Convert to PNG
                        base, _ = os.path.splitext(file)
                        new_file = base + '.png'
                        output_path = os.path.join(root, new_file)
                        
                        with open(output_path, 'wb') as o:
                            o.write(output_bytes)
                        
                        # Remove old jpg
                        os.remove(input_path)
                        
                        print(f"Processed AND converted to PNG: {input_path}")
                        
                        # Note: We need to tell the user or update Badges.js that '.jpg' became '.png'
                    else:
                        with open(input_path, 'wb') as o:
                            o.write(output_bytes)
                        print(f"Processed: {input_path}")
                except Exception as e:
                    print(f"Error processing {input_path}: {str(e)}")

# Process house logos
print("Processing house logos...")
process_directory(r"D:\coduku-private-\frontend\public\house_logos")

# Process clean badges
print("Processing clean badges...")
process_directory(r"D:\coduku-private-\frontend\public\clean-badges")

# Make sure to update Badges.js if any .jpg was converted to .png!
# Let's do a quick regex replace on Badges.js to ensure all .jpg/.jpeg are now .png
import re
badges_js_path = r"D:\coduku-private-\frontend\src\pages\Badges.js"
if os.path.exists(badges_js_path):
    with open(badges_js_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We only want to replace .jpg or .jpeg inside the /clean-badges/ strings
    def replace_jpg_to_png(m):
        return m.group(0).replace('.jpg', '.png').replace('.jpeg', '.png')
    
    new_content = re.sub(r"'/clean-badges/[^']+'", replace_jpg_to_png, content)
    
    if content != new_content:
        with open(badges_js_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Updated Badges.js to point to new .png extensions")

print("Done.")
