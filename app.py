import streamlit as st
import sqlite3
import pandas as pd
import os
from auditor_agent import fetch_loan_data, fetch_relevant_regulations, run_compliance_audit
import ollama

# 1. Set up professional Page Configuration
st.set_page_config(
    page_title="Project Covenant | Autonomous Loan Auditor",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling for an enterprise dashboard feel
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛡️ Project Covenant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Local Loan Compliance Auditor Engine (Zero-Trust/Private RAG)</div>', unsafe_allow_html=True)

# 2. Sidebar for System Status
with st.sidebar:
    st.header("Infrastructure Status")
    st.success("🟢 Core Banking System (SQLite) Connected")
    st.success("🟢 Vector Engine (ChromaDB) Ready")
    st.info("🤖 Model Backend: Qwen 2.5 (7B) via ROCm")
    
    st.markdown("---")
    st.markdown("**Secure Enclave Mode Active**\nAll processing takes place locally on bare-metal hardware. No data is transmitted externally.")

# 3. Pull all available loan IDs from the Core Banking System for the dropdown
def get_all_loan_ids():
    conn = sqlite3.connect('./data/core_banking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT loan_id, borrower_name FROM loan_applications")
    rows = cursor.fetchall()
    conn.close()
    return rows

try:
    loans = get_all_loan_ids()
    loan_options = {f"{r[0]} - {r[1]}": r[0] for r in loans}
except Exception as e:
    st.error("Could not read Core Banking Database. Ensure you have run init_databases.py")
    st.stop()

# 4. Dropdown Selector
selected_display = st.selectbox("Select Active Loan File for Inspection:", list(loan_options.keys()))
selected_id = loan_options[selected_display]

# Fetch baseline profile
profile = fetch_loan_data(selected_id)

if profile:
    # 5. UI Layout Layout: Metrics Cards
    st.subheader("📋 Loan Profile Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Loan ID", value=profile['loan_id'])
    with col2:
        st.metric(label="Borrower", value=profile['borrower'])
    with col3:
        st.metric(label="Stated Annual Income", value=f"${profile['income']:,.2f}")
    with col4:
        # Highlight DTI color code conditionally
        if profile['dti'] > 43.0:
            st.metric(label="Debt-to-Income (DTI) Ratio", value=f"{profile['dti']}%", delta="Exceeds 43% Limit", delta_color="inverse")
        else:
            st.metric(label="Debt-to-Income (DTI) Ratio", value=f"{profile['dti']}%", delta="Compliant")

    # Display Raw Underwriter Text Notes
    st.markdown("### 📝 Unstructured Underwriter Notes")
    st.info(f'"{profile["underwriter_notes"]}"')

    st.markdown("---")

    # 6. Execution Button Trigger
    if st.button("🚀 Execute Autonomous Compliance Audit", type="primary"):
        with st.spinner("Analyzing data points & generating local vector space embedding context..."):
            # Pull vector database rules matching this profile
            context_rules = fetch_relevant_regulations(profile)
            
            # Show a small expander with the rules ChromaDB found
            with st.expander("🔍 View Context Retrieved from Vector Database (ChromaDB)"):
                st.write(context_rules)
            
            # Prepare the system engineering prompt (Identical to our terminal script)
            prompt = f"""
            You are an elite, automated Enterprise Mortgage Compliance Auditor running inside a secure, zero-trust pipeline.
            Your task is to audit the following Loan Profile against the provided Federal Lending Guidelines.
            
            ### DATA INPUTS
            ---
            [VERIFIED REGULATORY GUIDELINES]:
            {context_rules}
            
            [BORROWER LOAN PROFILE]:
            - Loan ID: {profile['loan_id']}
            - Borrower Name: {profile['borrower']}
            - Debt-to-Income (DTI) Ratio: {profile['dti']}%
            - Stated Income: ${profile['income']:,}
            - Underwriter Risk Notes: "{profile['underwriter_notes']}"
            ---
            
            ### INSTRUCTIONS
            Analyze the inputs for explicit compliance violations. Generate a highly structured Audit Report containing:
            1. **AUDIT STATUS**: Boldly mark as [PASSED] or [COMPLIANCE VIOLATION DETECTED].
            2. **FINDINGS**: Explicitly cross-reference the metrics against the named rules (e.g., REG-RULE-101).
            3. **RISK ANALYSIS**: Call out any discrepancies hidden inside the unstructured underwriter notes.
            4. **REQUIRED ACTION**: Provide exact remediation steps for the operations team on the ground.
            
            Do not hallucinate rules. Base your judgment entirely on the verified inputs. Use clean Markdown styling.
            """
            
        # Stream the model response directly into the UI interface!
        st.subheader("📊 Generated Audit Report")
        report_placeholder = st.empty()
        
        # We call the streaming API so it types onto the screen in real-time
        full_response = ""
        try:
            with st.spinner("Model synthesizing compliance report via Local AMD GPU..."):
                response_stream = ollama.generate(model='qwen2.5:7b', prompt=prompt, stream=True)
                for chunk in response_stream:
                    full_response += chunk['response']
                    report_placeholder.markdown(full_response + "▌")
                # Remove typing block cursor at end
                report_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Execution Error connecting to local Ollama framework: {str(e)}")
