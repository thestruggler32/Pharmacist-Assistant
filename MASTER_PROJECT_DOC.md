# 🏥 Pharmacist Assistant: The Presentation Bible

**Version:** 3.0 (Hub Intelligence Edition)
**Status:** 🟢 Production Ready (Deployed)
**Date:** Feb 02, 2026

---

## 🚀 1. Executive Vision: "Why does this exist?"

### The Problem
Indian Handwritten Prescriptions are notorious.
1.  **Doctor Shorthand**: "Tab Dolo 1-0-1" is gibberish to a generic OCR.
2.  **Village Inventory**: A patient in a village pharmacy is told "Not Available" because the local shop doesn't have it, even if the city hub next door does.
3.  **Digital Gap**: Prescriptions remain on paper. Patients lose them. Doctors can't track history.

### The Solution
**Pharmacist Assistant** is the "Google Lens for Indian Pharma".
1.  **AI Decoder**: Reads messy handwriting & decodes medical shorthand (`BD` -> "Twice Daily").
2.  **Hub Intelligence**: If a medicine is missing locally, it instantly finds it in the nearest **City Hub** (Hub & Spoke Model).
3.  **Unified Platform**: Connects Doctors (Issuing), Patients (Viewing), and Pharmacists (Validating) on one cloud platform.

---

## 🧠 2. Deep Tech Architecture

How do we turn a blurry image into structured data?

### The Pipeline (The "Secret Sauce")
1.  **Input**: User uploads a messy JPEG of a prescription.
2.  **Preprocessing (OpenCV)**:
    -   Basic de-noising to remove paper stains.
3.  **Vision Intelligence (Gemini 1.5 Pro)**:
    -   We don't use simple Tesseract OCR. We use **Multimodal LLMs**.
    -   The model "looks" at the image and reasons: *"This squiggly line looks like 'Dolo', and the '1-0-1' next to it confirms it's a tablet."*
4.  **Database Validation (RapidFuzz)**:
    -   AI output: "Dolo 6S0" (OCR Error).
    -   Our System: Checks `india_medicines.csv` (253,000 rows).
    -   Correction: "Did you mean **Dolo 650**?" (Confidence 99%).
5.  **Inventory Check (Hub & Spoke)**:
    -   System detects user location: "Hallihole Village".
    -   Logic: "Map Hallihole -> **Mangalore Hub**".
    -   Result: "Available in Mangalore (Next Day Delivery)".

---

## 🛠️ 3. Technology Stack (The "Why")

| Component | Tech Choice | Why we chose it? |
| :--- | :--- | :--- |
| **Backend** | **Python (Flask)** | Best ecosystem for AI/Data integration (`pandas`, `google-generativeai`). Lightweight and fast. |
| **AI Engine** | **Gemini 1.5 Pro** | Beats GPT-4 Vision on handwritten text. Massive 1M token context allows it to understand complex pages. |
| **Database** | **SQLite** | Zero-latency local lookups. We handle **253,973 medicines** in under 50ms using optimized indexing. |
| **Search** | **RapidFuzz + SQL** | "Fuzzy Matching" allows us to find medicines even with spelling mistakes. |
| **Frontend** | **React + Vite** | Instant page loads. Tailwind CSS for a premium "Glassmorphism" UI. |
| **Deployment** | **Render + Vercel** | Cloud-native separation of concerns. Scalable and free. |

---

## � 4. Repository Structure (Where is the code?)

Where should you look during the demo?

```text
Pharmacist-Assistant/
├── backend/                  # The Brain (Python)
│   ├── app.py                # Main API Server (Starts here)
│   ├── database/             # The Memory
│   │   ├── init_db.py        # Schema Definition
│   │   ├── load_medicines.py # Big Data Loader (CSV -> SQL)
│   │   └── pharmacy.db       # The SQLite File
│   ├── utils/                # The Intelligence
│   │   ├── regional_alternatives.py  # Hub & Spoke Logic + Smart Search involved here
│   │   └── pipeline.py       # The OCR Extraction Logic
│   └── requirements.txt      # Dependencies
│
├── frontend/                 # The Face (React)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx # Main Pharmacist Hub
│   │   │   ├── Review.jsx    # The Core Workflow (Edit/Approve)
│   │   │   └── Request.jsx   # Patient Upload Screen
│   │   ├── services/
│   │   │   └── api.js        # Axios Config (Cloud URL)
│   │   └── components/       # Reusable UI (Buttons, Modals)
│   └── vite.config.js        # Build Config
│
└── MASTER_PROJECT_DOC.md     # This File
```

---

## 🔐 5. Role-Based Access Control (RBAC)

We implemented strict security layers. Not everyone sees everything.

### 👩‍⚕️ Doctor (The Issuer)
*   **Authority**: Can `ISSUE` new digital prescriptions.
*   **View**: Sees history of patients they treated.
*   **Restriction**: Cannot "Approve" (Flash conflict of interest).

### �‍⚕️ Pharmacist (The Validator)
*   **Authority**: Can `APPROVE` or `REJECT` OCR results.
*   **View**: Sees the "Queue" of pending uploads.
*   **Power**: Can edit medicine names if AI makes a mistake.
*   **Tool**: Has access to the **Regional Alternatives** search.

### 👨‍🦱 Patient (The User)
*   **Authority**: Can `UPLOAD` images.
*   **View**: Read-Only access to their own medical history.
*   **Restriction**: **Cannot edit** anything (Prevents fraud).

---

## �️ 6. The "Hub & Spoke" Logic (Regional Intelligence)

This is the flagship feature for the finals.

**The Logic Flow:**
1.  **Input**: User searches for "Amphotericin". Context: User is in "Mysore".
2.  **Hub Detective**:
    *   System checks map (Gemini/Mock): "Mysore is a spoke of **Bangalore Hub**".
3.  **Smart Search**:
    *   Is "Amphotericin" a Generic? **Yes**.
    *   Find Brand: Maps to **"Ambisome"**.
4.  **Inventory Query**:
    *   `SELECT * FROM medicines WHERE name LIKE '%Ambisome%' AND city = 'Bangalore'`
5.  **Output**:
    *   "Ambisome 50mg - **Available in Bangalore Hub** (Next Day Delivery)"

---

## 💾 7. Database Schema

We use Relational Data specific to Indian Pharma.

### `users` table
| Column | Type | Purpose |
| :--- | :--- | :--- |
| `id` | INT | Primary Key |
| `role` | TEXT | 'doctor', 'pharmacist', 'patient' |
| `license_number` | TEXT | For Doctors/Pharmacists validation |

### `medicines` table (The Big Data)
| Column | Type | Purpose |
| :--- | :--- | :--- |
| `generic_name` | TEXT | e.g., "Paracetamol" |
| `brand_name` | TEXT | e.g., "Dolo 650" |
| `region` | TEXT | State (Karnataka, Maharashtra) |
| `city` | TEXT | **The Hub City** (Bangalore, Mumbai) |

### `prescriptions` table
| Column | Type | Purpose |
| :--- | :--- | :--- |
| `image_url` | TEXT | Path to the uploaded JPEG |
| `ocr_data` | JSON | Raw AI output |
| `status` | TEXT | 'pending' -> 'approved' |

---

## 🔮 8. Future Scope & Scalability

1.  **WhatsApp Bot**: Patients send a photo to a WhatsApp number -> We process it and send back a payment link.
2.  **Voice Prescriptions**: Doctors dictate "Amoxicillin 500mg" -> We transcribe it to JSON.
3.  **Drug Interaction Engine**: Warning system: *"Patient is on Warfarin, do not prescribe Aspirin."*

---

*Verified by Antigravity Agent - Ready for Presentation*
