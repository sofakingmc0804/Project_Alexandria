# app.packages.embed.indexer

packages/embed/indexer.py

Builds FAISS index from segment embeddings for fast similarity search.
Falls back to simple numpy-based search if FAISS unavailable.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- build_and_save_index(job_dir: str) -> Dict[str, Any]
- build_faiss_index(embeddings: numpy.ndarray, index_type: str = 'IndexFlatIP') -> Any
- load_faiss()
- numpy_similarity_search(embeddings: numpy.ndarray, query_embedding: numpy.ndarray, k: int = 6) -> Tuple[numpy.ndarray, numpy.ndarray]
- search_index(index: Any, query_embedding: numpy.ndarray, k: int = 6) -> Tuple[numpy.ndarray, numpy.ndarray]
