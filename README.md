# Project Covenant: Autonomous Loan Compliance Auditor

Project Covenant is a bare-metal, enterprise-grade **Autonomous Loan Compliance Auditor** built using an on-premise Retrieval-Augmented Generation (RAG) architecture. The entire application runs completely offline inside a secure enclave framework, leveraging a local AMD GPU for accelerated inference. 

By combining a structured core banking relational database with an unstructured vector database containing regulatory guidelines, the system executes an automated compliance audit loop without transferring sensitive consumer financial data over external networks.

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
