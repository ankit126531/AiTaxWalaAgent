import os
import psycopg2
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

def create_database_tables():
    """Create the required tables in Supabase database"""
    
    # Get database URL from environment
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        print("Error: DB_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create UserFinancials table
        user_financials_table = """
        CREATE TABLE IF NOT EXISTS UserFinancials (
            session_id UUID PRIMARY KEY,
            gross_salary NUMERIC(15, 2),
            basic_salary NUMERIC(15, 2),
            hra_received NUMERIC(15, 2),
            rent_paid NUMERIC(15, 2),
            deduction_80c NUMERIC(15, 2),
            deduction_80d NUMERIC(15, 2),
            standard_deduction NUMERIC(15, 2),
            professional_tax NUMERIC(15, 2),
            tds NUMERIC(15, 2),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Create TaxComparison table
        tax_comparison_table = """
        CREATE TABLE IF NOT EXISTS TaxComparison (
            session_id UUID PRIMARY KEY REFERENCES UserFinancials(session_id),
            tax_old_regime NUMERIC(15, 2),
            tax_new_regime NUMERIC(15, 2),
            best_regime VARCHAR(10),
            selected_regime VARCHAR(10),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        # Execute table creation
        cursor.execute(user_financials_table)
        cursor.execute(tax_comparison_table)
        
        # Commit changes
        conn.commit()
        
        print("✅ Database tables created successfully!")
        print("✅ UserFinancials table created")
        print("✅ TaxComparison table created")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def test_database_connection():
    """Test the database connection"""
    
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        print("Error: DB_URL not found in environment variables")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Database connection successful!")
        print(f"✅ Database version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Tax Advisor Application Database...")
    print("=" * 50)
    
    # Test connection first
    if test_database_connection():
        # Create tables
        create_database_tables()
    else:
        print("❌ Cannot proceed without database connection")
        print("Please check your DB_URL in .env file") 