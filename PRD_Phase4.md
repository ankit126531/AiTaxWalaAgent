# Tax Advisor Application - Phase 4 PRD

## Phase 4: AI-Powered Advisor (Gemini) - Q&A and Personalized Suggestions

### 1. Objective
Integrate an AI-powered advisor using Google Gemini to provide contextual follow-up questions and personalized, actionable tax-saving suggestions based on the user's data and tax results.

---

### 2. Deliverables
- AI-powered follow-up question after tax calculation
- User can answer the AI's question
- Gemini provides personalized, actionable investment and tax-saving suggestions
- Suggestions are displayed in a modern, readable card format
- All AI interactions are session-based and privacy-compliant

---

### 3. Technical Requirements

#### AI Integration
- Use Google Gemini Flash API for generating follow-up questions and suggestions
- After tax results are shown, Gemini proactively asks a smart, contextual question
- User answers the question; Gemini then provides personalized suggestions
- All AI logic is implemented in `app.py` or a helper module
- Store the full conversation history in a local file (e.g., `ai_conversation_log.json`)

#### Backend
- `/advisor` route handles both GET (show question) and POST (process answer, show suggestions)
- Session stores financial data, tax results, and conversation state
- All endpoints and logic are implemented in root-level Python files

#### Frontend
- `ask.html` template displays:
  - The AI's follow-up question and a form for the user's answer
  - After submission, shows Gemini's personalized suggestions in a card format
- Modern, readable, and accessible UI

---

### 4. Acceptance Criteria
- After tax results, user is shown a relevant AI-generated follow-up question
- User can submit an answer
- Gemini provides 3-5 actionable, personalized suggestions with estimated tax savings
- Suggestions are displayed in a clear, modern format
- Conversation history is saved locally for the session

---

### 5. Out of Scope for Phase 4
- Admin analytics and session retrieval (future phases)
- Multi-user management 