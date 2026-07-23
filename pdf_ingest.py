import os
import uuid

from pinecone import Pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    PINECONE_API_KEY,
    PINECONE_HOST
)

from document_db import (
    add_document,
    document_exists,
    get_namespace
)

from document_db import add_document

def upload_pdf_to_pinecone(pdf_path):

    filename = os.path.basename(
        pdf_path
    )

    # Skip duplicate PDFs
    if document_exists(filename):

        print(
            "PDF already exists."
        )

        return {
            "namespace": get_namespace(
                filename
            ),
            "chunks": 0,
            "duplicate": True
        }

    # Dynamic Namespace Creation- Create namespace from filename
    namespace = filename.lower()

    namespace = namespace.replace(
        ".pdf",
        ""
    )

    namespace = namespace.replace(
        " ",
        "_"
    )

    print("Loading PDF...")

    # Load PDF
    loader = PyPDFLoader(pdf_path)

    # Read PDF
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # Create chunks
    chunks = splitter.split_documents(
        documents
    )

    # Create Pinecone connection
    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    # Connect to index
    index = pc.Index(
        host=PINECONE_HOST
    )

    records = []

    for i, chunk in enumerate(chunks):

        records.append(
            {
                "_id": f"{uuid.uuid4()}-{i}",
                "text": chunk.page_content,
                "page": chunk.metadata.get(
                    "page",
                    0
                )
            }
        )

    batch_size = 96

    for i in range(
        0,
        len(records),
        batch_size
    ):

        batch = records[
            i:i + batch_size
        ]

        index.upsert_records(
            namespace=namespace,
            records=batch
        )

    # Save PDF -> namespace mapping - Registry Storage
    add_document(
        filename,
        namespace
    )

    return {
        "namespace": namespace,
        "chunks": len(chunks),
        "duplicate": False
    }