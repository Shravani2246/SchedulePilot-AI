from pinecone import Pinecone

from config import (
    PINECONE_API_KEY,
    PINECONE_HOST
)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    host=PINECONE_HOST
)


def delete_namespace(namespace):

    index.delete(
        delete_all=True,
        namespace=namespace
    )