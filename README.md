# Tax Advisor Application

A web-based platform for salaried individuals to analyze tax liabilities and receive personalized, AI-powered tax-saving strategies. Users upload their salary slip or Form 16, review/enter data, compare tax regimes, and get actionable investment advice from Google Gemini.

## 🚀 Features

- **PDF Upload & Data Extraction**: Upload salary slips or Form 16 for automatic data extraction
- **Tax Regime Comparison**: Compare Old vs New tax regimes with detailed breakdowns
- **AI-Powered Advisor**: Get personalized investment suggestions using Google Gemini
- **Modern UI/UX**: Beautiful, responsive design with Aptos Display font
- **Secure Data Handling**: Session-based storage with UUIDs, no persistent file storage

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini Flash API
- **PDF Processing**: PyPDF2, pytesseract, pdf2image
- **Deployment**: Render

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── tax_calculator.py      # Tax calculation engine
├── supabase_db_create.py  # Database setup script
├── requirements.txt       # Python dependencies
├── build.sh              # Deployment script
├── env_example.txt       # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html        # Landing page
│   ├── form.html         # Data review form
│   ├── results.html      # Tax comparison results
│   └── ask.html          # AI advisor interface
└── uploads/              # Temporary PDF storage
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Supabase account
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tax-advisor-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your credentials
   GEMINI_API_KEY = "your-gemini-api-key"
   DB_URL = "postgresql://postgres:password@host:5432/postgres"
   ```

4. **Set up database**
   ```bash
   python supabase_db_create.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📊 Tax Calculation Logic

### Old Tax Regime (FY 2024-25)
- **Deductions**: Standard Deduction (₹50k), HRA, Professional Tax, 80C, 80D
- **Slabs**: 0% up to ₹2.5L, 5% up to ₹5L, 20% up to ₹10L, 30% above

### New Tax Regime (Default)
- **Deductions**: Standard Deduction (₹50k) only
- **Slabs**: 0% up to ₹3L, 5% up to ₹6L, 10% up to ₹9L, 15% up to ₹12L, 20% up to ₹15L, 30% above

*4% cess applies to final tax amount in both regimes*

## 🗄️ Database Schema

### UserFinancials Table
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

### TaxComparison Table
- `session_id` (UUID, Primary Key, Foreign Key)
- `tax_old_regime` (NUMERIC)
- `tax_new_regime` (NUMERIC)
- `best_regime` (VARCHAR)
- `selected_regime` (VARCHAR)
- `created_at` (TIMESTAMPTZ)

## 🔧 API Routes

- `GET /` - Landing page
- `GET /upload` - PDF upload form
- `POST /upload` - Handle PDF upload and data extraction
- `GET /review` - Data review form
- `POST /review` - Process reviewed data
- `GET /calculate` - Show tax calculation results
- `POST /calculate` - Proceed to AI advisor
- `GET /advisor` - AI advisor question
- `POST /advisor` - Get AI suggestions
- `GET /restart` - Clear session and restart

## 🚀 Deployment

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Set environment variables in Render dashboard**
   - `GEMINI_API_KEY`
   - `DB_URL`
3. **Deploy automatically on push to main branch**

The `build.sh` script handles:
- Installing system dependencies (Tesseract OCR)
- Installing Python dependencies
- Setting up the environment

## 🔒 Security Features

- Session-based data storage with UUIDs
- No persistent file storage (PDFs deleted after processing)
- All secrets stored as environment variables
- HTTPS enforced in production
- Input validation and sanitization

## 🎨 UI/UX Features

- Modern, light theme with blue highlights
- Aptos Display font for distinct typography
- Responsive design for all devices
- Multi-page flow with clear navigation
- Accessible design with proper contrast
- Loading states and error handling

## 🤖 AI Integration

The application uses Google Gemini for:
- Contextual follow-up questions based on user data
- Personalized investment suggestions
- Tax optimization recommendations
- Actionable advice with estimated savings

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions, please open an issue in the repository.

---

**Note**: This application is for educational and demonstration purposes. Always consult with a qualified tax professional for actual tax advice. 