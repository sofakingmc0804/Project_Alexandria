"""
packages/graph/builder.py

Computes cosine similarity between segments and flags duplicates.
Creates a graph representation with nodes (segments) and edges (similarities).
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple


def compute_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarity matrix.
    
    Args:
        embeddings: numpy array of shape (n_segments, embedding_dim)
    
    Returns:
        Similarity matrix of shape (n_segments, n_segments)
    """
    # Normalize embeddings (should already be normalized, but ensure)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    normalized = embeddings / norms
    
    # Compute cosine similarity via dot product
    similarity_matrix = np.dot(normalized, normalized.T)
    
    return similarity_matrix


def find_duplicates(
    similarity_matrix: np.ndarray,
    threshold: float = 0.90
) -> List[Tuple[int, int, float]]:
    """
    Find duplicate pairs based on similarity threshold.
    
    Args:
        similarity_matrix: Pairwise similarity matrix
        threshold: Similarity threshold for duplicates (default: 0.90)
    
    Returns:
        List of (idx1, idx2, similarity) tuples
    """
    n = similarity_matrix.shape[0]
    duplicates = []
    
    for i in range(n):
        for j in range(i + 1, n):  # Only upper triangle, avoid self-comparison
            sim = similarity_matrix[i, j]
            if sim >= threshold:
                duplicates.append((i, j, float(sim)))
    
    return duplicates


def build_graph(
    segments: List[Dict[str, Any]],
    similarity_matrix: np.ndarray,
    similarity_threshold: float = 0.70,
    duplicate_threshold: float = 0.90
) -> Dict[str, Any]:
    """
    Build graph from segments and similarity matrix.
    
    Args:
        segments: List of segment dictionaries
        similarity_matrix: Pairwise similarity matrix
        similarity_threshold: Minimum similarity to create edge (default: 0.70)
        duplicate_threshold: Similarity threshold for flagging duplicates (default: 0.90)
    
    Returns:
        Graph dictionary with nodes, edges, and duplicate info
    """
    n = len(segments)
    
    # Create nodes
    nodes = []
    for i, seg in enumerate(segments):
        nodes.append({
            'id': seg['id'],
            'index': i,
            'start_ms': seg['start_ms'],
            'end_ms': seg['end_ms'],
            'text_preview': seg['text'][:100] + '...' if len(seg['text']) > 100 else seg['text'],
            'lang': seg['lang']
        })
    
    # Create edges for similar segments
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = similarity_matrix[i, j]
            if sim >= similarity_threshold:
                edges.append({
                    'source': segments[i]['id'],
                    'target': segments[j]['id'],
                    'source_index': i,
                    'target_index': j,
                    'similarity': float(sim),
                    'is_duplicate': bool(sim >= duplicate_threshold)
                })
    
    # Find duplicates
    duplicates = find_duplicates(similarity_matrix, duplicate_threshold)
    
    duplicate_pairs = [
        {
            'segment1_id': segments[i]['id'],
            'segment2_id': segments[j]['id'],
            'segment1_index': i,
            'segment2_index': j,
            'similarity': sim
        }
        for i, j, sim in duplicates
    ]
    
    graph = {
        'nodes': nodes,
        'edges': edges,
        'num_nodes': len(nodes),
        'num_edges': len(edges),
        'num_duplicates': len(duplicate_pairs),
        'duplicates': duplicate_pairs,
        'similarity_threshold': similarity_threshold,
        'duplicate_threshold': duplicate_threshold
    }
    
    return graph


def build_segment_graph(job_dir: str) -> Dict[str, Any]:
    """
    Main graph building function.
    
    Args:
        job_dir: Path to job directory
    
    Returns:
        Graph dictionary
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
        print("Warning: No segments to build graph from")
        output = {
            'job_id': data['job_id'],
            'nodes': [],
            'edges': [],
            'num_nodes': 0,
            'num_edges': 0,
            'num_duplicates': 0,
            'duplicates': []
        }
    else:
        # Extract embeddings
        embeddings = np.array([seg['embedding'] for seg in segments], dtype=np.float32)
        
        print(f"Computing similarity matrix for {len(segments)} segments...")
        similarity_matrix = compute_similarity_matrix(embeddings)
        
        print(f"Building graph...")
        graph = build_graph(
            segments,
            similarity_matrix,
            similarity_threshold=0.70,
            duplicate_threshold=0.90
        )
        
        output = {
            'job_id': data['job_id'],
            **graph
        }
        
        print(f" Graph built: {output['num_nodes']} nodes, {output['num_edges']} edges")
        print(f" Duplicates found: {output['num_duplicates']}")
        
        if output['num_duplicates'] > 0:
            print(f"  Duplicate pairs:")
            for dup in output['duplicates'][:5]:  # Show first 5
                print(f"    - Segments {dup['segment1_index']}  {dup['segment2_index']}: {dup['similarity']:.3f}")
    
    # Save graph
    output_path = job_path / 'graph.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f" Saved graph to: {output_path}")
    
    return output


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python builder.py <job_dir>")
        print("Example: python builder.py tmp/input_sample_30s_20251015_041747")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    graph = build_segment_graph(job_dir)
