import sqlite3
import chromadb
import ollama

def fetch_loan_data(loan_id):
    """Step 1: Extract structured and unstructured records from local SQL."""
    conn = sqlite3.connect('./data/core_banking.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT la.loan_id, la.borrower_name, la.reported_annual_income, 
               la.loan_amount, la.debt_to_income_ratio, un.risk_assessment_text
        FROM loan_applications la
        JOIN underwriting_notes un ON la.loan_id = un.loan_id
        WHERE la.loan_id = ?
    '''
    cursor.execute(query, (loan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "loan_id": row[0],
        "borrower": row[1],
        "income": row[2],
        "loan_amount": row[3],
        "dti": row[4],
        "underwriter_notes": row[5]
    }

def fetch_relevant_regulations(loan_profile):
    """Step 2: Query local ChromaDB using semantic text search via Ollama."""
    client = chromadb.PersistentClient(path="./data/vector_store")
    
    # Re-link our embedding pipeline back to the container
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="qwen2.5:7b"
    )
    
    collection = client.get_collection(name="federal_lending_guidelines", embedding_function=ollama_ef)
    
    # Search the vector store using the underwriter notes as the semantic query
    search_query = f"DTI ratio {loan_profile['dti']}% employment history notes: {loan_profile['underwriter_notes']}"
    results = collection.query(query_texts=[search_query], n_results=2)
    
    # Flatten the retrieved documents list
    return "\n".join(results['documents'][0])

def run_compliance_audit(loan_id):
    """Step 3: Combine SQL and Vector data, then stream into local LLM for auditing."""
    print(f"\n[Project Covenant] Commencing autonomous audit for Loan ID: {loan_id}...")
    
    # Pull data points
    loan_profile = fetch_loan_data(loan_id)
    if not loan_profile:
        print(f"Error: Loan ID {loan_id} not found in Core Banking System.")
        return
        
    context_rules = fetch_relevant_regulations(loan_profile)
    
    # Construct an airtight engineering system prompt
    prompt = f"""
    You are an elite, automated Enterprise Mortgage Compliance Auditor running inside a secure, zero-trust pipeline.
    Your task is to audit the following Loan Profile against the provided Federal Lending Guidelines.
    
    ### DATA INPUTS
    ---
    [VERIFIED REGULATORY GUIDELINES]:
    {context_rules}
    
    [BORROWER LOAN PROFILE]:
    - Loan ID: {loan_profile['loan_id']}
    - Borrower Name: {loan_profile['borrower']}
    - Debt-to-Income (DTI) Ratio: {loan_profile['dti']}%
    - Stated Income: ${loan_profile['income']:,}
    - Underwriter Risk Notes: "{loan_profile['underwriter_notes']}"
    ---
    
    ### INSTRUCTIONS
    Analyze the inputs for explicit compliance violations. Generate a highly structured Audit Report containing:
    1. **AUDIT STATUS**: Boldly mark as [PASSED] or [COMPLIANCE VIOLATION DETECTED].
    2. **FINDINGS**: Explicitly cross-reference the metrics against the named rules (e.g., REG-RULE-101).
    3. **RISK ANALYSIS**: Call out any discrepancies hidden inside the unstructured underwriter notes.
    4. **REQUIRED ACTION**: Provide exact remediation steps for the operations team on the ground.
    
    Do not hallucinate rules. Base your judgment entirely on the verified inputs.
    """
    
    # Execute the local model synthesis via the running container
    response = ollama.generate(model='qwen2.5:7b', prompt=prompt)
    
    print("\n================== REGULATORY AUDIT REPORT ==================")
    print(response['response'])
    print("=============================================================\n")

if __name__ == "__main__":
    # Run the audit engine against Bob Miller's high-risk application data (LN1002)
    run_compliance_audit("LN1002")
