# Quick Fix Guide - "No Medicines Detected"

## ⚠️ Issue: No medicines detected on handwritten prescription

## ✅ Solution: Enable Handwriting Mode

### The Problem
You uploaded the image **WITHOUT** checking the "Handwriting Mode" checkbox. 
The system used standard preprocessing which is too strict for messy handwriting.

### The Fix (3 Steps)

1. **Go to upload page**: `http://localhost:5000/upload?user_id=pharma_001`

2. **✅ CHECK the Handwriting Mode checkbox**:
   ```
   🖊️ Handwriting Mode (Messy/Cursive Prescriptions)
   ```

3. **Upload your Manipal Hospital prescription again**

### Why This Matters

| Mode | Preprocessing | Parsing | Result |
|------|---------------|---------|--------|
| **Standard** (unchecked) | 2x resize, basic | Strict (0.5 threshold) | ❌ No medicines |
| **Handwriting** (checked) | 3x resize, CLAHE, deskew | Lenient (0.3 threshold) | ✅ Detects medicines |

---

## 🧪 Test Your Image First

Before uploading to the UI, test your image:

```bash
python debug_prescription.py
```

**When prompted, enter the path to your Manipal Hospital image.**

This will show you:
- ✓ OCR extracted text
- ✓ Detected medicines
- ✓ Confidence scores
- ✓ Database matches

---

## 📋 Checklist

- [ ] App is running (`python app.py`)
- [ ] Go to upload page
- [ ] **✅ CHECK "Handwriting Mode" checkbox** ← CRITICAL!
- [ ] Upload image
- [ ] Review detected medicines

---

## 🎯 Expected Results (With Handwriting Mode)

Your Manipal Hospital prescription should detect:
- ✅ LIPOSOMAL AMPHOTERICIN
- ✅ AMPHOTERICIN CONVENTIONAL
- ✅ Dosages (50mg, 300mg, etc.)
- ✅ Frequencies (OD, vials/day)

---

## 🐛 Still Not Working?

Run the debug script:
```bash
python debug_prescription.py
```

Check the output:
1. **OCR extracted text** - Should show medicine names
2. **Parsed medicines** - Should show detected medicines
3. **Debug images** - Check `debug_handwriting.jpg`

If OCR shows text but parser doesn't detect medicines:
- The patterns might need adjustment
- Share the OCR output with me

If OCR shows no text:
- Image quality is too low
- Try a clearer photo

---

## ✨ Remember

**The checkbox is CRITICAL!** 

Without it, the system uses standard mode which can't handle:
- Cursive handwriting
- Low contrast
- Faint ink
- Rotated text

**With handwriting mode**, it uses:
- 3x resize (vs 2x)
- CLAHE contrast enhancement
- Deskew rotation correction
- Lenient parsing (0.3 vs 0.5 threshold)

---

## 🚀 Quick Test

1. Run: `python debug_prescription.py`
2. Enter your image path
3. Check if medicines are detected
4. If yes → Use handwriting mode in UI
5. If no → Share debug output
