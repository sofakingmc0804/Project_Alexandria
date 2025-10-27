"""
packages/embed/indexer.py

Builds FAISS index from segment embeddings for fast similarity search.
Falls back to simple numpy-based search if FAISS unavailable.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple


def load_faiss():
    """Try to import FAISS, return None if unavailable."""
    try:
        import faiss
        return faiss
    except ImportError:
        print("Warning: faiss-cpu not installed")
        print("Install with: pip install faiss-cpu")
        return None


def build_faiss_index(
    embeddings: np.ndarray,
    index_type: str = 'IndexFlatIP'
) -> Any:
    """
    Build FAISS index from embeddings.
    
    Args:
        embeddings: numpy array of shape (n_segments, embedding_dim)
        index_type: FAISS index type ('IndexFlatIP' for cosine similarity)
    
    Returns:
        FAISS index or None if FAISS unavailable
    """
    faiss = load_faiss()
    
    if faiss is None:
        return None
    
    dim = embeddings.shape[1]
    
    # Create index (using Inner Product for cosine similarity with normalized vectors)
    if index_type == 'IndexFlatIP':
        index = faiss.IndexFlatIP(dim)
    elif index_type == 'IndexFlatL2':
        index = faiss.IndexFlatL2(dim)
    else:
        # Default to cosine similarity
        index = faiss.IndexFlatIP(dim)
    
    # Add vectors to index
    index.add(embeddings.astype(np.float32))
    
    print(f" Built FAISS index: {index_type}, {index.ntotal} vectors, {dim}d")
    
    return index


def search_index(
    index: Any,
    query_embedding: np.ndarray,
    k: int = 6
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Search FAISS index for similar vectors.
    
    Args:
        index: FAISS index
        query_embedding: Query vector
        k: Number of results to return
    
    Returns:
        Tuple of (distances, indices)
    """
    query = query_embedding.reshape(1, -1).astype(np.float32)
    distances, indices = index.search(query, k)
    return distances[0], indices[0]


def numpy_similarity_search(
    embeddings: np.ndarray,
    query_embedding: np.ndarray,
    k: int = 6
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fallback similarity search using numpy (cosine similarity).
    
    Args:
        embeddings: All embeddings (n_segments, dim)
        query_embedding: Query vector (dim,)
        k: Number of results
    
    Returns:
        Tuple of (similarities, indices)
    """
    # Compute cosine similarities
    similarities = np.dot(embeddings, query_embedding)
    
    # Get top k
    top_k_indices = np.argsort(similarities)[::-1][:k]
    top_k_scores = similarities[top_k_indices]
    
    return top_k_scores, top_k_indices


def build_and_save_index(job_dir: str) -> Dict[str, Any]:
    """
    Main indexing function.
    
    Args:
        job_dir: Path to job directory
    
    Returns:
        Dictionary with index metadata
    """
    job_path = Path(job_dir)
    
    # Load embedded segments
    segments_path = job_path / 'segments_embedded.json'
    if not segments_path.exists():
        raise FileNotFoundError(f"Embedded segments not found: {segments_path}")
    
    with open(segments_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = data.get('segments', [])
    
    if not segments:
        print("Warning: No segments to index")
        return {
            'job_id': data['job_id'],
            'index_type': 'none',
            'num_vectors': 0,
            'dimension': 0
        }
    
    # Extract embeddings
    embeddings = np.array([seg['embedding'] for seg in segments], dtype=np.float32)
    
    print(f"Building index for {len(segments)} segments, {embeddings.shape[1]}d")
    
    # Build FAISS index
    faiss = load_faiss()
    
    if faiss is not None:
        index = build_faiss_index(embeddings, 'IndexFlatIP')
        
        # Save FAISS index
        index_path = job_path / 'index.faiss'
        faiss.write_index(index, str(index_path))
        print(f" Saved FAISS index to: {index_path}")
        
        index_type = 'faiss'
    else:
        # Save numpy embeddings as fallback
        index_path = job_path / 'index.npy'
        np.save(str(index_path), embeddings)
        print(f" Saved numpy index to: {index_path}")
        
        index_type = 'numpy'
    
    # Test retrieval
    print("Testing retrieval with first segment as query...")
    if index_type == 'faiss':
        scores, indices = search_index(index, embeddings[0], k=min(6, len(segments)))
    else:
        scores, indices = numpy_similarity_search(embeddings, embeddings[0], k=min(6, len(segments)))
    
    print(f"Top result: segment {indices[0]}, score: {scores[0]:.4f}")
    
    # Save metadata
    metadata = {
        'job_id': data['job_id'],
        'index_type': index_type,
        'num_vectors': len(segments),
        'dimension': embeddings.shape[1],
        'embedding_model': data.get('embedding_model', 'unknown'),
        'index_path': str(index_path)
    }
    
    metadata_path = job_path / 'index_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print(f" Saved index metadata to: {metadata_path}")
    
    return metadata


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python indexer.py <job_dir>")
        print("Example: python indexer.py tmp/input_sample_30s_20251015_041747")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    metadata = build_and_save_index(job_dir)
    
    if metadata['num_vectors'] == 0:
        print("Warning: No vectors indexed")
