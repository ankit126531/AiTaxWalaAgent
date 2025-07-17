from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
import PyPDF2
import pytesseract
from PIL import Image
import io
import pdf2image
import google.generativeai as genai
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection function
def get_db_connection():
    """Create and return a database connection using DB_URL from environment"""
    try:
        conn = psycopg2.connect(os.getenv('DB_URL'))
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper to check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def structure_with_gemini(extracted_text):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None, 'Gemini API key not found.'
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            """
            You are an expert at reading Indian salary slips and Form 16s. Given the following extracted text, return a JSON object with the following fields (use 0 or empty string if not found):
            - gross_salary
            - basic_salary
            - hra_received
            - rent_paid
            - deduction_80c
            - deduction_80d
            - standard_deduction
            - professional_tax
            - tds
            
            Only return a valid JSON object, no explanation or extra text.
            
            Extracted text:
            """
            + extracted_text
        )
        response = model.generate_content(prompt)
        # Try to parse the first code block as JSON
        match = re.search(r'\{[\s\S]*\}', response.text)
        if match:
            data = json.loads(match.group(0))
            return data, None
        else:
            return None, 'Gemini did not return valid JSON.'
    except Exception as e:
        return None, f'Gemini API error: {e}'

# PDF extraction logic (basic, can be improved)
def extract_pdf_data(pdf_path):
    extracted_text = ""
    try:
        # Try text extraction with PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
        print("PyPDF2 extracted:", extracted_text)
        # If text is empty, try OCR
        if not extracted_text.strip():
            from pdf2image.pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                print("OCR page text:", ocr_text)
                extracted_text += ocr_text
        print("After OCR extracted:", extracted_text)
    except Exception as e:
        extracted_text = f"Error extracting PDF: {e}"
        print(extracted_text)
    # Use Gemini to structure data
    gemini_data, gemini_error = structure_with_gemini(extracted_text)
    print("Gemini data:", gemini_data)
    print("Gemini error:", gemini_error)
    is_salary_slip = False
    note = None
    if gemini_data:
        # Detect if it's a salary slip (not Form 16)
        if 'form 16' not in extracted_text.lower():
            is_salary_slip = True
            note = "Detected as salary slip. All values multiplied by 12 to estimate annual amounts. Please verify."
            # Multiply relevant fields by 12 if they are numbers and nonzero
            for key in ['gross_salary', 'basic_salary', 'hra_received', 'rent_paid', 'deduction_80c', 'deduction_80d', 'professional_tax', 'tds']:
                try:
                    val = gemini_data.get(key, '')
                    if val is not None and str(val).strip() != '' and float(val) != 0:
                        gemini_data[key] = str(round(float(val) * 12, 2))
                except Exception:
                    pass
        gemini_data['raw_text'] = extracted_text[:1000]
        gemini_data['is_salary_slip'] = is_salary_slip
        gemini_data['note'] = note
        return gemini_data
    else:
        # Fallback: dummy parse
        return {
            'gross_salary': '',
            'basic_salary': '',
            'hra_received': '',
            'rent_paid': '',
            'deduction_80c': '',
            'deduction_80d': '',
            'standard_deduction': '50000',
            'professional_tax': '',
            'tds': '',
            'raw_text': extracted_text[:1000],
            'gemini_error': gemini_error,
            'is_salary_slip': False,
            'note': None
        }

def get_ai_question(financial_data, tax_results):
    """Generate contextual AI question based on user data"""
    try:
        import google.generativeai as genai
        prompt = f"""
        Based on the following financial data and tax calculation results, ask ONE smart, contextual follow-up question to help the user optimize their taxes:
        
        Financial Data:
        - Gross Salary: ₹{financial_data.get('gross_salary', 0):,.2f}
        - Basic Salary: ₹{financial_data.get('basic_salary', 0):,.2f}
        - HRA Received: ₹{financial_data.get('hra_received', 0):,.2f}
        - Rent Paid: ₹{financial_data.get('rent_paid', 0):,.2f}
        - 80C Deductions: ₹{financial_data.get('deduction_80c', 0):,.2f}
        - 80D Deductions: ₹{financial_data.get('deduction_80d', 0):,.2f}
        
        Tax Results:
        - Old Regime Tax: ₹{tax_results.get('old_regime_tax', 0):,.2f}
        - New Regime Tax: ₹{tax_results.get('new_regime_tax', 0):,.2f}
        - Best Regime: {tax_results.get('best_regime', 'unknown')}
        
        Ask a specific, actionable question that would help them save more on taxes.
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        else:
            return "What additional investments are you planning to make this financial year?"
    except Exception as e:
        print(f"Error generating AI question: {e}")
        return "What additional investments are you planning to make this financial year?"

def get_ai_suggestions(financial_data, tax_results, user_answer):
    """Generate personalized AI suggestions"""
    try:
        import google.generativeai as genai
        prompt = f"""
        Based on the following information, provide personalized, actionable tax-saving suggestions:
        
        Financial Data:
        - Gross Salary: ₹{financial_data.get('gross_salary', 0):,.2f}
        - Basic Salary: ₹{financial_data.get('basic_salary', 0):,.2f}
        - HRA Received: ₹{financial_data.get('hra_received', 0):,.2f}
        - Rent Paid: ₹{financial_data.get('rent_paid', 0):,.2f}
        - 80C Deductions: ₹{financial_data.get('deduction_80c', 0):,.2f}
        - 80D Deductions: ₹{financial_data.get('deduction_80d', 0):,.2f}
        
        Tax Results:
        - Old Regime Tax: ₹{tax_results.get('old_regime_tax', 0):,.2f}
        - New Regime Tax: ₹{tax_results.get('new_regime_tax', 0):,.2f}
        - Best Regime: {tax_results.get('best_regime', 'unknown')}
        
        User's Answer: {user_answer}
        
        Provide 3-5 specific, actionable suggestions with estimated tax savings for each.
        Format the response in a clear, readable manner.
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        else:
            return "Consider increasing your 80C investments to ₹1.5L to maximize deductions."
    except Exception as e:
        print(f"Error generating AI suggestions: {e}")
        return "Consider increasing your 80C investments to ₹1.5L to maximize deductions."

@app.route('/')
def index():
    """Serve the landing page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Tax Advisor Application is running"})

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return render_template('form.html', error='No file part')
        file = request.files['pdf_file']
        if file.filename == '':
            return render_template('form.html', error='No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Extract data
            extracted_data = extract_pdf_data(file_path)
            # Delete file after extraction
            os.remove(file_path)
            return render_template('form.html', extracted=extracted_data, error=None)
        else:
            return render_template('form.html', error='Invalid file type')
    return render_template('form.html', extracted=None, error=None)

@app.route('/review', methods=['POST'])
def review():
    # Get reviewed data from form
    reviewed_data = request.form.to_dict()
    # For now, just show the data back (Phase 3 will process it)
    return render_template('form.html', extracted=reviewed_data, error=None, reviewed=True)

@app.route('/calculate', methods=['POST'])
def calculate():
    # Get reviewed data from form
    data = request.form.to_dict()
    # Convert all relevant fields to float
    for key in ['gross_salary', 'basic_salary', 'hra_received', 'rent_paid', 'deduction_80c', 'deduction_80d', 'professional_tax', 'tds']:
        data[key] = float(data.get(key, 0) or 0)
    selected_regime = data.get('selected_regime', 'new')
    session_id = str(uuid.uuid4())

    # Calculate tax
    from tax_calculator import TaxCalculator
    tax_calculator = TaxCalculator()
    results = tax_calculator.compare_regimes(
        data['gross_salary'], data['basic_salary'], data['hra_received'],
        data['rent_paid'], data['deduction_80c'], data['deduction_80d'], data['professional_tax']
    )

    # Save to database
    tax_calculator.save_to_database(session_id, data, results, selected_regime)

    # Render results page
    return render_template('results.html', results=results, selected_regime=selected_regime, data=data)

@app.route('/advisor', methods=['GET', 'POST'])
def advisor():
    import json
    print("Advisor route called. Method:", request.method)
    # Try to get from session first
    financial_data = session.get('financial_data')
    tax_results = session.get('tax_results')
    selected_regime = session.get('selected_regime')
    print("Session financial_data:", financial_data)
    print("Session tax_results:", tax_results)
    print("Session selected_regime:", selected_regime)

    # If missing and POST, try to get from form
    if request.method == 'POST':
        print("POST data received:", request.form)
        if not financial_data and request.form.get('financial_data'):
            financial_data = json.loads(request.form['financial_data'])
            print("Loaded financial_data from form:", financial_data)
        if not tax_results and request.form.get('tax_results'):
            tax_results = json.loads(request.form['tax_results'])
            print("Loaded tax_results from form:", tax_results)
        if not selected_regime and request.form.get('selected_regime'):
            selected_regime = request.form['selected_regime']
            print("Loaded selected_regime from form:", selected_regime)

    if not financial_data or not tax_results:
        print("Missing data for advisor. financial_data:", financial_data, "tax_results:", tax_results)
        return "Session expired or missing data. Please start over.", 400

    if request.method == 'POST':
        user_answer = request.form.get('user_answer')
        if not user_answer:
            # Show the question and answer form
            question = get_ai_question(financial_data, tax_results)
            print("AI question generated (POST, no answer):", question)
            return render_template(
                'ask.html',
                question=question,
                show_suggestions=False,
                financial_data=financial_data,
                tax_results=tax_results,
                selected_regime=selected_regime
            )
        print("User answer:", user_answer)
        try:
            suggestions = get_ai_suggestions(financial_data, tax_results, user_answer)
            print("Raw suggestions from Gemini:", suggestions)
        except Exception as e:
            print(f"Exception in get_ai_suggestions: {e}")
            suggestions = f"Error generating suggestions: {e}"
        question = get_ai_question(financial_data, tax_results)
        log = {
            "financial_data": financial_data,
            "tax_results": tax_results,
            "selected_regime": selected_regime,
            "user_answer": user_answer,
            "suggestions": suggestions
        }
        try:
            with open('ai_conversation_log.json', 'a') as f:
                f.write(json.dumps(log) + '\n')
        except Exception as e:
            print(f"Error saving AI conversation log: {e}")
        print("Suggestions generated:", suggestions)
        return render_template(
            'ask.html',
            suggestions=suggestions,
            show_suggestions=True,
            question=question,
            user_answer=user_answer
        )
    else:
        question = get_ai_question(financial_data, tax_results)
        print("AI question generated:", question)
        return render_template(
            'ask.html',
            question=question,
            show_suggestions=False,
            financial_data=financial_data,
            tax_results=tax_results,
            selected_regime=selected_regime
        )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 