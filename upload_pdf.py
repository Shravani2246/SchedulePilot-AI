
from pinecone import Pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =========================
# CONFIG
# =========================
# #Import Config
from config import (
    PINECONE_API_KEY,
    PINECONE_HOST,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    NAMESPACE,
    PINECONE_INDEX_NAME
)

PDF_PATH = "data/sample.pdf"


# IMPORTANT:
# Replace with the text field configured in your Pinecone index.
# Most integrated indexes use "chunk_text".
TEXT_FIELD = "text"

# =========================
# LOAD PDF
# =========================

print("Loading PDF...")

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")

# =========================
# CHUNKING
# =========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# =========================
# CONNECT TO PINECONE
# =========================

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(host=PINECONE_HOST)

# =========================
# PREPARE RECORDS
# =========================

records = []

for i, chunk in enumerate(chunks):

    records.append({
        "_id": f"chunk-{i}",
        TEXT_FIELD: chunk.page_content,
        "page": chunk.metadata.get("page", 0),
        "source": PDF_PATH
    })

# =========================
# UPLOAD IN BATCHES
# =========================

batch_size = 96

for i in range(0, len(records), batch_size):

    batch = records[i:i + batch_size]

    index.upsert_records(
        namespace=NAMESPACE,
        records=batch
    )

    print(f"Uploaded {min(i + batch_size, len(records))}/{len(records)}")

print("\nPDF uploaded successfully!")