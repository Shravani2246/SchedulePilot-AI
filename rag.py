from pinecone import Pinecone

from config import (
    PINECONE_API_KEY,
    PINECONE_HOST
)
#Create Pinecone Client
pc = Pinecone(api_key=PINECONE_API_KEY)

#Connects to a specific Pinecone index.
index = pc.Index(host=PINECONE_HOST)

def search_pdf(query: str , namespace: str):

    results = index.search(
        namespace=namespace,
        query={
            "top_k": 5,
            "inputs": {
                "text": query
            }
        }
    )

    contexts = []
    #Iterates over every retrieved chunk.

    for hit in results["result"]["hits"]:
        contexts.append(
            f"""
            Page: {hit['fields'].get('page')}

            {hit['fields']['text']}
            """
        )

    return "\n\n".join(contexts) #Combines all retrieved chunks into one large string.