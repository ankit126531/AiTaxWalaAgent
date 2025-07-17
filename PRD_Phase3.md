# Tax Advisor Application - Phase 3 PRD

## Phase 3: Tax Calculation Engine, Regime Comparison, and Results Display

### 1. Objective
Implement the backend logic to calculate tax liabilities under both the Old and New regimes, compare results, and display them to the user in a clear, visual format.

---

### 2. Deliverables
- Tax calculation logic for both regimes (FY 2024-25)
- Backend integration to process reviewed data and selected regime
- Results page showing side-by-side comparison of Old vs. New Regime
- Highlight the user's selected regime
- Save results to the database (Supabase)

---

### 3. Technical Requirements

#### Tax Calculation Logic
- Implement tax calculation for both regimes:
  - **Old Regime:**
    - Deductions: Standard Deduction (₹50k), HRA, Professional Tax, 80C, 80D, etc.
    - Slabs: 0% up to ₹2.5L, 5% up to ₹5L, 20% up to ₹10L, 30% above
  - **New Regime:**
    - Deductions: Standard Deduction (₹50k) only
    - Slabs: 0% up to ₹3L, 5% up to ₹6L, 10% up to ₹9L, 15% up to ₹12L, 20% up to ₹15L, 30% above
  - 4% cess applies to the final tax amount in both regimes
- Use the reviewed data and selected regime from the previous phase

#### Backend Integration
- On form submission, process the reviewed data and selected regime
- Calculate tax for both regimes
- Save the results to the Supabase database (`UserFinancials` and `TaxComparison` tables)
- Store results in the session for further use

#### Results Display
- Render a results page (`results.html`) showing:
  - Tax under Old Regime
  - Tax under New Regime
  - Highlight the regime with lower tax and the user's selected regime
  - Show a summary of the user's financial data
- Ensure the results are visually distinct and easy to compare

---

### 4. Acceptance Criteria
- User sees a results page with a clear comparison of Old vs. New Regime
- The user's selected regime is highlighted
- Tax calculation matches the FY 2024-25 rules
- Results are saved to the database
- All endpoints and logic are implemented in root-level Python files

---

### 5. Out of Scope for Phase 3
- AI-powered advisor and suggestions (Phase 4)
- Session retrieval and admin analytics (future phases) 