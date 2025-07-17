# Tax Advisor Application - Phase 2 PRD

## Phase 2: PDF Upload, Extraction, and Manual Data Review

### 1. Objective
Enable users to upload their Pay Slip or Form 16 (PDF), extract relevant financial data, and review/edit the extracted data in a user-friendly form.

---

### 2. User Flow

1. **Landing Page**  
   - User clicks "Start" and is directed to the PDF upload page.

2. **PDF Upload**  
   - User uploads a Pay Slip or Form 16 (PDF).
   - The backend saves the uploaded file to the `/uploads` directory.

3. **Data Extraction**  
   - The backend extracts data from the PDF using:
     - `PyPDF2` for text extraction.
     - `pytesseract` (OCR) for scanned PDFs.
     - (Optionally) Google Gemini LLM for structuring ambiguous data.
   - Extracted data is mapped to the fields required for tax calculation.

4. **Manual Data Review**  
   - The user is presented with a form (`/templates/form.html`) pre-filled with the extracted data.
   - The user can review and edit all fields.
   - The user selects their preferred tax regime (Old/New) via a radio button.
   - On submission, the form data is posted to the backend for further processing.

---

### 3. Technical Requirements

- **Frontend**
  - `/templates/form.html` displays a form with all required fields (see Data Model below).
  - The form is pre-filled with extracted data and allows user edits.
  - Includes a radio button for tax regime selection.

- **Backend**
  - `app.py` handles:
    - File upload endpoint.
    - Data extraction logic (using `PyPDF2`, `pytesseract`, and Gemini).
    - Serving the pre-filled form for user review.
    - Saving uploaded files to `/uploads`.

- **File Storage**
  - Uploaded PDFs are stored temporarily in `/uploads`.

- **Integration**
  - `/templates/form.html` posts to a backend endpoint in `app.py`.
  - All logic resides in root-level Python files.

---

### 4. Data Model (Fields to Extract & Review)

| Field Name           | Description                        |
|----------------------|------------------------------------|
| gross_salary         | Total gross salary                  |
| basic_salary         | Basic salary component              |
| hra_received         | HRA received                        |
| rent_paid            | Annual rent paid                    |
| deduction_80c        | 80C investments                     |
| deduction_80d        | 80D medical insurance               |
| standard_deduction   | Standard deduction                  |
| professional_tax     | Professional tax paid               |
| tds                  | Tax Deducted at Source              |

---

### 5. Acceptance Criteria

- User can upload a PDF and see a pre-filled form with extracted data.
- User can edit any field and select a tax regime.
- Uploaded files are saved to `/uploads`.
- The form posts data to the backend for the next phase (tax calculation).
- All endpoints and logic are implemented in `app.py` at the project root.

---

### 6. Out of Scope for Phase 2

- Tax calculation and comparison (Phase 3).
- AI-powered advisor and suggestions (Phase 4).
- Database persistence (beyond temporary file storage). 