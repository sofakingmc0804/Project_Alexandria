# app.packages.graph.builder

packages/graph/builder.py

Computes cosine similarity between segments and flags duplicates.
Creates a graph representation with nodes (segments) and edges (similarities).

## Members
- Any(*args, **kwargs)
- Path(*args, **kwargs)
- build_graph(segments: List[Dict[str, Any]], similarity_matrix: numpy.ndarray, similarity_threshold: float = 0.7, duplicate_threshold: float = 0.9) -> Dict[str, Any]
- build_segment_graph(job_dir: str) -> Dict[str, Any]
- compute_similarity_matrix(embeddings: numpy.ndarray) -> numpy.ndarray
- find_duplicates(similarity_matrix: numpy.ndarray, threshold: float = 0.9) -> List[Tuple[int, int, float]]
