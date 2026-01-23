"""Convert webp image to jpg for OCR compatibility"""
from PIL import Image

# Open the webp image
img = Image.open('filled-medical-prescription-isolated-on-260nw-144551783.webp')

# Convert to RGB (in case it has alpha channel)
rgb_img = img.convert('RGB')

# Save as JPG
rgb_img.save('prescription_sample.jpg', 'JPEG', quality=95)

print("✓ Converted prescription_sample.webp to prescription_sample.jpg")
