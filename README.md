# Project Covenant: Autonomous Loan Compliance Auditor

Project Covenant is a proof-of-concept autonomous compliance auditing platform designed to demonstrate how financial institutions could leverage localized AI models to evaluate lending decisions against regulatory guidelines without exposing sensitive customer data to external AI providers.

The platform combines structured borrower data with regulatory policy documentation through a Retrieval-Augmented Generation (RAG) architecture running entirely on-premises. By performing inference locally, the solution explores a governance-first approach to AI adoption in highly regulated environments where data privacy, auditability, and security are critical requirements.

This project was created to investigate how organizations can balance AI-driven productivity gains with compliance, risk management, and data sovereignty concerns.

## Architecture Blueprint

The system splits data ingestion and inference execution into a decoupled, zero-trust pipeline:

1. **Structured Data Layer (SQLite):** Extracts borrower records, loan balances, debt-to-income (DTI) metrics, and unstructured underwriter risk logs.
2. **Vector Space Layer (ChromaDB):** Embeds and indexes real-world lending compliance rules using a local embedding pipeline.
3. **Synthesis Engine (Ollama/Qwen 2.5):** Performs localized token generation using hardware-accelerated inference via AMD ROCm, generating a highly structured compliance report.

---

## Technical Stack

* **Inference Engine:** Ollama running `qwen2.5:7b` (7-Billion Parameter Model optimized for structured processing)
* **Hardware Acceleration:** AMD ROCm runtime passthrough for bare-metal Linux execution
* **Vector Database:** ChromaDB (Persistent local storage)
* **Relational Database:** SQLite3
* **User Interface:** Streamlit (Python Native Web Dashboard)
* **Containerization:** Docker & Docker Compose V2

---

## Quickstart Installation & Deployment

### 1. Prerequisites
Ensure you are running an Ubuntu-based Linux distribution (such as Pop!_OS) with an active AMD GPU configured with the proper driver stack.

### 2. Infrastructure Spin-up
Clone the repository and initialize the containerized Ollama engine using Docker Compose:
```bash
cd ~/onprem-rag-engine
docker compose up -d
