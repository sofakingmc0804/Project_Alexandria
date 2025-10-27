"""Embed segments using sentence-transformers without mock fallbacks."""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any


def load_embedding_model(model_name: str = 'BAAI/bge-large-en-v1.5'):
    """
    Load sentence transformer model.
    Falls back to smaller models if large model unavailable.
    
    Args:
        model_name: HuggingFace model identifier
    
    Returns:
        SentenceTransformer model or None if unavailable
    """
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-unresolved]
    except ImportError as exc:  # pragma: no cover - depends on runtime env
        raise RuntimeError(
            "sentence-transformers is required for embedding generation. "
            "Install with `pip install sentence-transformers`."
        ) from exc

    try:
        print(f"Loading embedding model: {model_name}")
        model = SentenceTransformer(model_name)
        print(" Model loaded successfully")
        return model
    except Exception as exc:  # pragma: no cover - depends on network/state
        raise RuntimeError(f"Failed to load embedding model '{model_name}': {exc}") from exc


def embed_segments(
    segments: List[Dict[str, Any]],
    model,
) -> List[Dict[str, Any]]:
    """
    Embed segment text using sentence transformers.
    
    Args:
        segments: List of segment dictionaries
        model: Pre-loaded SentenceTransformer model (optional)
        use_mock: If True, use mock embeddings instead of real model
    
    Returns:
        List of segments with embeddings added
    """
    
    if not segments:
        return []

    if model is None:
        raise RuntimeError("Embedding model must be provided")
    
    # Extract texts
    texts = [seg['text'] for seg in segments]
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} segments...")
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    
    # Add embeddings to segments
    for i, seg in enumerate(segments):
        seg['embedding'] = embeddings[i].tolist()
        seg['embedding_model'] = getattr(model, 'name_or_path', 'unknown')
        seg['embedding_dim'] = len(embeddings[i])
    
    print(f" Generated {len(segments)} embeddings")
    return segments


def embed_job(job_dir: str, model_name: str = 'BAAI/bge-large-en-v1.5') -> Dict[str, Any]:
    """
    Main embedding function.
    
    Args:
        job_dir: Path to job directory
        model_name: Embedding model to use
    
    Returns:
        Dictionary with embedded segments
    """
    job_path = Path(job_dir)
    
    # Load segments
    segments_path = job_path / 'segments.json'
    if not segments_path.exists():
        raise FileNotFoundError(f"Segments file not found: {segments_path}")
    
    with open(segments_path, 'r', encoding='utf-8') as f:
        segments_data = json.load(f)
    
    segments = segments_data.get('segments', [])
    
    if not segments:
        print("Warning: No segments to embed")
        output = {
            'job_id': segments_data['job_id'],
            'segments': [],
            'embedding_model': 'none',
            'embedding_dim': 0
        }
    else:
        # Load embedding model
        model = load_embedding_model(model_name)

        # Embed segments
        embedded_segments = embed_segments(segments, model)
        
        output = {
            'job_id': segments_data['job_id'],
            'segments': embedded_segments,
            'embedding_model': embedded_segments[0].get('embedding_model', 'unknown') if embedded_segments else 'none',
            'embedding_dim': embedded_segments[0].get('embedding_dim', 0) if embedded_segments else 0
        }
    
    # Save embedded segments
    output_path = job_path / 'segments_embedded.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f" Saved embeddings to: {output_path}")
    print(f" Model: {output['embedding_model']}, Dimension: {output['embedding_dim']}")
    
    return output


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python embedder.py <job_dir> [model_name]")
        print("Example: python embedder.py tmp/input_sample_30s_20251015_041747")
        sys.exit(1)
    
    job_dir = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else 'BAAI/bge-large-en-v1.5'
    
    embed_job(job_dir, model_name)
