# InsulinSense — OCR Feature Integration Guide

## Files Delivered

| File | Purpose |
|------|---------|
| `ocr_utils.py` | OCR engine — preprocessing, text extraction, regex parsing |
| `ocr_route.py` | Flask route (`POST /ocr-upload`) to paste into `app.py` |
| `OCRUpload.jsx` | React upload component |
| `OCRUpload.css` | Styles for the component |

---

## Step 1 — Install Python Dependencies

```bash
pip install pytesseract pillow pdf2image
```

Also install **Tesseract OCR** on your system:
- **Windows**: https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

For PDF support, install **Poppler**:
- **Windows**: https://github.com/oschwartz10612/poppler-windows
- **Linux**: `sudo apt install poppler-utils`
- **macOS**: `brew install poppler`

---

## Step 2 — Add `ocr_utils.py` to your project

Place `ocr_utils.py` in the same folder as `app.py`.

---

## Step 3 — Add the OCR route to `app.py`

At the **top** of `app.py`, add this import (alongside your other imports):

```python
from ocr_utils import run_ocr
```

Then paste the contents of `ocr_route.py` into `app.py`,
anywhere alongside the other routes (e.g. after the `/predict` route).

---

## Step 4 — Add the React Component

Copy `OCRUpload.jsx` and `OCRUpload.css` into your frontend `src/components/` folder.

---

## Step 5 — Wire into your Prediction Form

In your prediction form component (wherever the fields like Glucose, Insulin, HbA1c live),
import and use `OCRUpload` like this:

```jsx
import OCRUpload from "./OCRUpload";

export default function PredictForm() {
  const [formData, setFormData] = useState({
    Glucose: "", Insulin: "", HbA1c: "",
    Triglycerides: "", HDL: "", /* ...other fields */
  });

  // Called by OCRUpload after extraction
  const handleAutofill = (ocrValues) => {
    setFormData(prev => ({ ...prev, ...ocrValues }));
  };

  return (
    <div>
      {/* Place OCRUpload at the TOP of your form */}
      <OCRUpload onAutofill={handleAutofill} />

      {/* Your existing form fields */}
      <input
        type="number"
        placeholder="Fasting Glucose"
        value={formData.Glucose}
        onChange={e => setFormData(prev => ({ ...prev, Glucose: e.target.value }))}
      />
      <input
        type="number"
        placeholder="Fasting Insulin"
        value={formData.Insulin}
        onChange={e => setFormData(prev => ({ ...prev, Insulin: e.target.value }))}
      />
      {/* ...rest of fields... */}
    </div>
  );
}
```

The key is:
- Your form fields must be **controlled inputs** (value driven by state)
- `handleAutofill` merges OCR values into your existing state
- Fields NOT found by OCR remain empty for manual input ✅

---

## How It Works (Flow)

```
User uploads image/PDF
        ↓
Flask reads file bytes → ocr_utils.run_ocr()
        ↓
Image preprocessing (grayscale + contrast boost)
        ↓
pytesseract extracts raw text
        ↓
Regex keyword matching per field
        ↓
Numeric value extracted from window after keyword
        ↓
JSON returned: { "glucose": "110", "hba1c": "", ... }
        ↓
React OCRUpload receives response
        ↓
onAutofill() called → form fields auto-filled
        ↓
User reviews + edits + clicks Predict ✅
```

---

## OCR Field → Form Field Mapping

| OCR Key | Form Field Key | Label |
|---------|---------------|-------|
| `glucose` | `Glucose` | Fasting Glucose |
| `insulin` | `Insulin` | Fasting Insulin |
| `hba1c` | `HbA1c` | HbA1c |
| `triglycerides` | `Triglycerides` | Triglycerides |
| `hdl` | `HDL` | HDL Cholesterol |
| `ldl` | `LDL` | LDL Cholesterol |
| `cholesterol` | `cholesterol` | Total Cholesterol |

> **Note:** LDL and Total Cholesterol are extracted but are not required by the `/predict` endpoint.
> They are included in case you add them to future models.

---

## Behavior Summary

| Scenario | Result |
|----------|--------|
| Value found in report | Field auto-filled ✅ |
| Value NOT in report | Field left empty — user fills manually ✅ |
| Unreadable / blurry image | Returns all empty strings gracefully ✅ |
| PDF upload | Converted page-by-page then OCR'd ✅ |
| Wrong file type | Error message shown to user ✅ |
| Server unreachable | Error message shown to user ✅ |
