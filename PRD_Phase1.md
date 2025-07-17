# Tax Advisor Application - Phase 1 PRD

## Phase 1: Project Setup, Database Schema, and Landing Page

### 1. Objective
Establish the foundational structure for the Tax Advisor Application, including project scaffolding, database schema creation, and a modern landing page.

---

### 2. Deliverables

- Project directory and file structure as per Master PRD
- Supabase database schema with required tables
- Landing page served at the root URL

---

### 3. Technical Requirements

#### Project Structure
- All code and configuration files must reside in the project root (not in subfolders or the virtual environment).
- Required files and folders:
  - `.env` (environment variables)
  - `app.py` (main Flask app)
  - `requirements.txt` (Python dependencies)
  - `supabase_db_create.py` (database setup script)
  - `tax_calculator.py` (tax logic)
  - `/templates/index.html` (landing page template)
  - `/uploads/` (temporary PDF storage)

#### Database Schema (Supabase)
- **Table 1: UserFinancials**
  - `session_id` (UUID, Primary Key)
  - `gross_salary` (NUMERIC)
  - `basic_salary` (NUMERIC)
  - `hra_received` (NUMERIC)
  - `rent_paid` (NUMERIC)
  - `deduction_80c` (NUMERIC)
  - `deduction_80d` (NUMERIC)
  - `standard_deduction` (NUMERIC)
  - `professional_tax` (NUMERIC)
  - `tds` (NUMERIC)
  - `created_at` (TIMESTAMPTZ)
- **Table 2: TaxComparison**
  - `session_id` (UUID, Primary Key, Foreign Key)
  - `tax_old_regime` (NUMERIC)
  - `tax_new_regime` (NUMERIC)
  - `best_regime` (VARCHAR)
  - `selected_regime` (VARCHAR)
  - `created_at` (TIMESTAMPTZ)

#### Landing Page
- Modern, branded landing page with a "Start" button.
- Served at `/` using `/templates/index.html`.
- Should introduce the app, its features, and guide the user to start the process.

---

### 4. Acceptance Criteria

- Project structure matches the Master PRD.
- Database tables (`UserFinancials`, `TaxComparison`) are created in Supabase using the provided script.
- User visiting the root URL sees the landing page and can click "Start" to begin.
- No code, templates, or uploads inside the virtual environment directory.

---

### 5. Out of Scope for Phase 1

- PDF upload, extraction, and data review (Phase 2)
- Tax calculation and comparison (Phase 3)
- AI-powered advisor (Phase 4)
