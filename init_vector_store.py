import os
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# Ensure our local data directory exists
os.makedirs('./data/vector_store', exist_ok=True)

def init_compliance_knowledge_base():
    print("Initializing Project Covenant Vector Store (ChromaDB)...")
    
    # 1. Connect to ChromaDB in persistent client mode (saves files to your disk)
    client = chromadb.PersistentClient(path="./data/vector_store")
    
    # 2. Configure Chroma to use your running local Ollama backend for text embeddings
    # We use qwen2.5:7b because it generates highly accurate embeddings out of the box
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="qwen2.5:7b"
    )
    
    # 3. Create or get the compliance collection
    collection = client.get_or_create_collection(
        name="federal_lending_guidelines",
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"} # Uses cosine similarity for vector searching
    )
    
    # 4. Define our hard regulatory rule compliance snippets
    regulatory_rules = [
        "REG-RULE-101: Standard Conventional Debt-to-Income (DTI) Limit. The maximum allowable debt-to-income ratio for a qualified conventional home loan is 43.00%. Any application exceeding a 43.00% DTI must possess documented significant compensating factors to clear audit.",
        "REG-RULE-102: Employment Continuity Mandate. Borrowers must document a minimum of 24 months of stable, continuous history in their primary field of employment. Secondary source income from an alternative job cannot be counted toward qualifying annual income unless a continuous 2-year history at that secondary job is verified.",
        "REG-RULE-103: Minimum Liquid Asset Reserve Requirements. To mitigate default risk, borrowers must maintain post-closing liquid asset reserves equivalent to at least 6 months of total monthly housing payments (Principal, Interest, Taxes, Insurance) if the transaction is deemed higher-risk due to a credit score below 680 or a high loan-to-value ratio."
    ]
    
    # Create matching deterministic IDs and metadata for tracking back source material
    rule_ids = [f"RULE_{i+1:03d}" for i in range(len(regulatory_rules))]
    metadatas = [
        {"category": "underwriting", "enforcement": "strict"},
        {"category": "employment", "enforcement": "strict"},
        {"category": "assets", "enforcement": "conditional"}
    ]
    
    # 5. Insert the regulations into ChromaDB
    # Under the hood, this sends the text to Ollama, gets the vector arrays, and saves them locally.
    print("Sending compliance guidelines to local Ollama to generate vector embeddings...")
    collection.upsert(
        documents=regulatory_rules,
        ids=rule_ids,
        metadatas=metadatas
    )
    
    print(f"Success! Vector Knowledge Base initialized with {collection.count()} active rules.")

if __name__ == "__main__":
    init_compliance_knowledge_base()
