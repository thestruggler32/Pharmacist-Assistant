"""Quick test script for OCR engine"""
import sys
sys.path.insert(0, '.')

from utils.ocr_engine import OCREngine

# Initialize OCR
print("Initializing OCR engine...")
ocr = OCREngine(lang='en')

# Extract text
print("\nExtracting text from prescription image...")
result = ocr.extract_text('filled-medical-prescription-isolated-on-260nw-144551783.webp')

print(f"\n✓ Extracted {len(result)} lines\n")
print("=" * 80)

# Display first 15 lines
for r in result[:15]:
    conf_emoji = "🟢" if r['confidence'] >= 0.8 else "🟡" if r['confidence'] >= 0.5 else "🔴"
    print(f"{conf_emoji} Line {r['line_number']:2d} | Conf: {r['confidence']:.2%} | {r['text']}")

if len(result) > 15:
    print(f"\n... and {len(result) - 15} more lines")

print("=" * 80)
