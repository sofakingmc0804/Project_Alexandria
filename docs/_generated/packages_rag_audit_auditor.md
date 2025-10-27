# app.packages.rag_audit.auditor

packages/rag_audit/auditor.py

Verifies script groundedness against source documents using RAG retrieval.
Generates audit report with groundedness scores and citations.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- audit_job(job_dir: str, config_path: str = 'configs/retrieval.yaml') -> Dict[str, Any]
- audit_script(script_path: str, index: Any, embeddings: numpy.ndarray, metadata: Dict, model, config: Dict[str, Any]) -> Dict[str, Any]
- calculate_groundedness(sentence: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[float, List[str]]
- create_mock_embedding(text: str, dim: int = 1024) -> numpy.ndarray
- extract_sentences(text: str) -> List[str]
- load_config(config_path: str = 'configs/retrieval.yaml') -> Dict[str, Any]
- load_embedding_model(config: Dict[str, Any])
- load_index(config: Dict[str, Any]) -> Tuple[Any, numpy.ndarray, Dict]
- retrieve_sources(query: str, index: Any, embeddings: numpy.ndarray, metadata: Dict, model, config: Dict[str, Any]) -> List[Dict[str, Any]]
