import sqlite3
import os

# Ensure the persistent data directory exists
os.makedirs('./data', exist_ok=True)

DB_PATH = './data/core_banking.db'

def init_mock_banking_system():
    print("Initializing Project Covenant Core Banking Database (SQLite)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create a table for baseline customer loan files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_applications (
            loan_id TEXT PRIMARY KEY,
            borrower_name TEXT,
            reported_annual_income REAL,
            stated_liquid_assets REAL,
            loan_amount REAL,
            property_value REAL,
            debt_to_income_ratio REAL
        )
    ''')

    # 2. Create a table for unstructured underwriter risk logs (Where fraud/mistakes usually hide)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS underwriting_notes (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id TEXT,
            underwriter_id TEXT,
            risk_assessment_text TEXT,
            FOREIGN KEY(loan_id) REFERENCES loan_applications(loan_id)
        )
    ''')

    # 3. Seed Mock Data (Loan 1001: Flawless / Loan 1002: Compliance Violation)
    mock_loans = [
        ('LN1001', 'Alice Vance', 145000.0, 85000.0, 400000.0, 500000.0, 31.5),
        ('LN1002', 'Bob Miller', 55000.0, 4500.0, 480000.0, 500000.0, 54.2) 
    ]

    mock_notes = [
        ('LN1001', 'UW_99', 'Borrower verified with 2 years of W2s. Assets verified via bank statements. DTI is well within standard conventional thresholds.'),
        ('LN1002', 'UW_42', 'Application indicates high DTI at 54.2%. Primary income documents show a secondary job that was only started 2 months ago. Stated liquid assets seem insufficient to cover required reserves, closing costs, and down payment.')
    ]

    # Insert data cleanly
    cursor.executemany('INSERT OR REPLACE INTO loan_applications VALUES (?, ?, ?, ?, ?, ?, ?)', mock_loans)
    cursor.executemany('INSERT OR REPLACE INTO underwriting_notes (loan_id, underwriter_id, risk_assessment_text) VALUES (?, ?, ?)', mock_notes)

    conn.commit()
    conn.close()
    print(f"Success! Core database initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_mock_banking_system()
