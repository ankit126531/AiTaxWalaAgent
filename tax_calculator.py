import uuid
from datetime import datetime
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TaxCalculator:
    """Tax calculation engine for FY 2024-25"""
    
    def __init__(self):
        self.old_regime_slabs = [
            (0, 250000, 0),
            (250001, 500000, 5),
            (500001, 1000000, 20),
            (1000001, float('inf'), 30)
        ]
        
        self.new_regime_slabs = [
            (0, 300000, 0),
            (300001, 600000, 5),
            (600001, 900000, 10),
            (900001, 1200000, 15),
            (1200001, 1500000, 20),
            (1500001, float('inf'), 30)
        ]
        
        self.cess_rate = 0.04  # 4% cess
        self.standard_deduction = 50000  # ₹50k standard deduction
    
    def calculate_tax_old_regime(self, gross_salary, basic_salary, hra_received, 
                                rent_paid, deduction_80c, deduction_80d, 
                                professional_tax):
        """Calculate tax under Old Regime"""
        
        # Calculate HRA exemption
        hra_exemption = min(
            hra_received,
            basic_salary * 0.5,  # 50% of basic salary
            rent_paid - (basic_salary * 0.1)  # Rent paid - 10% of basic
        )
        hra_exemption = max(0, hra_exemption)
        
        # Calculate total deductions
        total_deductions = (
            self.standard_deduction +
            hra_exemption +
            deduction_80c +
            deduction_80d +
            professional_tax
        )
        
        # Calculate taxable income
        taxable_income = gross_salary - total_deductions
        
        # Calculate tax using slabs
        tax = self._calculate_tax_by_slabs(taxable_income, self.old_regime_slabs)
        
        # Add cess
        total_tax = tax + (tax * self.cess_rate)
        
        return round(total_tax, 2)
    
    def calculate_tax_new_regime(self, gross_salary, professional_tax):
        """Calculate tax under New Regime"""
        
        # Only standard deduction is allowed
        total_deductions = self.standard_deduction + professional_tax
        
        # Calculate taxable income
        taxable_income = gross_salary - total_deductions
        
        # Calculate tax using slabs
        tax = self._calculate_tax_by_slabs(taxable_income, self.new_regime_slabs)
        
        # Add cess
        total_tax = tax + (tax * self.cess_rate)
        
        return round(total_tax, 2)
    
    def _calculate_tax_by_slabs(self, taxable_income, slabs):
        """Calculate tax using given slabs"""
        if taxable_income <= 0:
            return 0
        
        total_tax = 0
        remaining_income = taxable_income
        
        for i, (lower, upper, rate) in enumerate(slabs):
            if remaining_income <= 0:
                break
            
            # Calculate income in this slab
            slab_income = min(remaining_income, upper - lower)
            
            # Calculate tax for this slab
            slab_tax = (slab_income * rate) / 100
            total_tax += slab_tax
            
            # Reduce remaining income
            remaining_income -= slab_income
        
        return total_tax
    
    def compare_regimes(self, gross_salary, basic_salary, hra_received, 
                       rent_paid, deduction_80c, deduction_80d, professional_tax):
        """Compare tax under both regimes"""
        
        # Calculate tax for both regimes
        old_regime_tax = self.calculate_tax_old_regime(
            gross_salary, basic_salary, hra_received, rent_paid,
            deduction_80c, deduction_80d, professional_tax
        )
        
        new_regime_tax = self.calculate_tax_new_regime(
            gross_salary, professional_tax
        )
        
        # Determine best regime
        best_regime = "old" if old_regime_tax < new_regime_tax else "new"
        
        return {
            "old_regime_tax": old_regime_tax,
            "new_regime_tax": new_regime_tax,
            "best_regime": best_regime,
            "tax_savings": abs(old_regime_tax - new_regime_tax)
        }
    
    def save_to_database(self, session_id, financial_data, tax_results, selected_regime):
        """Save financial data and tax results to database, or fallback to local file if DB fails"""
        import json
        db_url = os.getenv('DB_URL')
        if not db_url:
            print("Error: DB_URL not found in environment variables")
            self._save_to_local(session_id, financial_data, tax_results, selected_regime)
            return False
        try:
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            # Insert into UserFinancials
            financial_insert = """
            INSERT INTO UserFinancials (
                session_id, gross_salary, basic_salary, hra_received, rent_paid,
                deduction_80c, deduction_80d, standard_deduction, professional_tax, tds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(financial_insert, (
                session_id,
                financial_data.get('gross_salary', 0),
                financial_data.get('basic_salary', 0),
                financial_data.get('hra_received', 0),
                financial_data.get('rent_paid', 0),
                financial_data.get('deduction_80c', 0),
                financial_data.get('deduction_80d', 0),
                self.standard_deduction,
                financial_data.get('professional_tax', 0),
                financial_data.get('tds', 0)
            ))
            # Insert into TaxComparison
            tax_insert = """
            INSERT INTO TaxComparison (
                session_id, tax_old_regime, tax_new_regime, best_regime, selected_regime
            ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(tax_insert, (
                session_id,
                tax_results['old_regime_tax'],
                tax_results['new_regime_tax'],
                tax_results['best_regime'],
                selected_regime
            ))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Data saved to database for session: {session_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            self._save_to_local(session_id, financial_data, tax_results, selected_regime)
            return False

    def _save_to_local(self, session_id, financial_data, tax_results, selected_regime):
        """Fallback: Save results to a local JSON file (append mode)"""
        import json
        local_file = 'local_results.json'
        entry = {
            'session_id': session_id,
            'financial_data': financial_data,
            'tax_results': tax_results,
            'selected_regime': selected_regime
        }
        try:
            # Read existing data
            try:
                with open(local_file, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = []
            data.append(entry)
            with open(local_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Data saved locally to {local_file}")
        except Exception as e:
            print(f"❌ Error saving locally: {e}")

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

# Example usage
if __name__ == "__main__":
    calculator = TaxCalculator()
    
    # Test calculation
    test_data = {
        'gross_salary': 800000,
        'basic_salary': 400000,
        'hra_received': 120000,
        'rent_paid': 144000,
        'deduction_80c': 150000,
        'deduction_80d': 25000,
        'professional_tax': 2400,
        'tds': 50000
    }
    
    results = calculator.compare_regimes(**test_data)
    print("Test Tax Calculation Results:")
    print(f"Old Regime Tax: ₹{results['old_regime_tax']:,.2f}")
    print(f"New Regime Tax: ₹{results['new_regime_tax']:,.2f}")
    print(f"Best Regime: {results['best_regime']}")
    print(f"Tax Savings: ₹{results['tax_savings']:,.2f}") 