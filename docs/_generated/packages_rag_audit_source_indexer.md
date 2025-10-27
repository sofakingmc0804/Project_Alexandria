# app.packages.rag_audit.source_indexer

packages/rag_audit/source_indexer.py

Indexes source documents from /sources_clean for RAG retrieval.
Supports both FAISS (local) and Qdrant (server-based) backends.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- build_faiss_index(chunks: List[Dict[str, Any]], embeddings: numpy.ndarray, config: Dict[str, Any], sources_metadata: List[Dict[str, Any]]) -> Dict[str, Any]
- build_qdrant_index(chunks: List[Dict[str, Any]], embeddings: numpy.ndarray, config: Dict[str, Any], sources_metadata: List[Dict[str, Any]]) -> Dict[str, Any]
- chunk_text(text: str, config: Dict[str, Any]) -> List[Dict[str, Any]]
- embed_chunks(chunks: List[Dict[str, Any]], model) -> numpy.ndarray
- index_sources(sources_dir: str = 'knowledge/sources_clean', config_path: str = 'configs/retrieval.yaml', job_dir: Optional[str] = None) -> Dict[str, Any]
- load_config(config_path: str = 'configs/retrieval.yaml') -> Dict[str, Any]
- load_embedding_model(config: Dict[str, Any])
