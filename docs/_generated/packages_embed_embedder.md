# app.packages.embed.embedder

packages/embed/embedder.py

Embeds segment text using sentence-transformers (bge-large-en).
Falls back to smaller models if bge-large unavailable.

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- create_mock_embedding(text: str, dim: int = 1024) -> numpy.ndarray
- embed_job(job_dir: str, model_name: str = 'BAAI/bge-large-en-v1.5') -> Dict[str, Any]
- embed_segments(segments: List[Dict[str, Any]], model=None, use_mock: bool = False) -> List[Dict[str, Any]]
- load_embedding_model(model_name: str = 'BAAI/bge-large-en-v1.5')
