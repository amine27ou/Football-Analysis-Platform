import chromadb

def retrieve(query: str, n_results: int = 5, filters: dict = None) -> list[dict]:
    # 1. Connect to the ChromaDB database
    chroma_client = chromadb.PersistentClient(path="chroma_store")

    # 2. Get the collection
    collection = chroma_client.get_collection(name="barca_history")

    # 3. Search for the most relevant chunks
    query_kwargs = {
        "query_texts":[query],
        "n_results":n_results
    }
    if filters:
        query_kwargs["where"] = filters
    
    results = collection.query(**query_kwargs)

    # 4. Format the results
    retrieved_chunks = []

    for text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        retrieved_chunks.append({
            "text": text,
            "metadata": metadata
        })

    return retrieved_chunks

# import sys
# sys.path.insert(0, "rag")
# from retriever import retrieve

# # Test 1: no filter
# results = retrieve("Messi goal Champions League", n_results=3)
# for r in results:
#     print(r["metadata"]["date"], r["metadata"]["competition"], r["metadata"]["result"])
#     print(r["text"][:150])
#     print()

# # Test 2: filter by competition
# results = retrieve("Barcelona win", n_results=3, filters={"competition": "CL"})
# for r in results:
#     print(r["metadata"]["date"], r["metadata"]["competition"], r["metadata"]["result"])
#     print(r["text"][:150])
#     print()