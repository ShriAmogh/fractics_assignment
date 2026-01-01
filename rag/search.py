from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from utils import validate_date

VECTOR_TOP_K = 20
FINAL_TOP_K = 5
CHROMA_DIR = "chroma_store"
COLLECTION_NAME = "cscl_papers"

#query = input("Enter prompt: ")

client = PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(COLLECTION_NAME)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

cross_encoder_model= CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2")


def hybrid_search(query: str, published_after: str | None = None, top_k: int = VECTOR_TOP_K):
    where_clause = {}

    if published_after:
        if not validate_date(published_after):
            raise ValueError("Date must be in YYYY-MM-DD format")
        year = int(published_after.split("-")[0])
        where_clause["submission_date"] = {"$gte": year}

    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause if where_clause else None,
        include=["documents", "metadatas", "distances"]
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    if not documents:
        return []
    
    chunk_pairs = []
    for doc in documents:
        chunk_pairs.append((query, doc))

    rerank_scores = cross_encoder_model.predict(chunk_pairs, 
                                                batch_size=32, 
                                                show_progress_bar= True)
    reranked = []
    for doc, meta, dist, score in zip(documents, metadatas, distances, rerank_scores):
        reranked.append({
            "document": doc,
            "metadata": meta,
            "vector_distance": dist,
            "rerank_score": float(score)
        })
    reranked.sort(key= lambda x:x["rerank_score"], reverse= True)

    if reranked[0]["rerank_score"] < 0.2:
        return []
    

    return reranked

#print(hybrid_search(query, published_after= None, top_k= VECTOR_TOP_K))

