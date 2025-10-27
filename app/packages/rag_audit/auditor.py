"""
packages/rag_audit/auditor.py

Verifies script groundedness against source documents using RAG retrieval.
Generates audit report with groundedness scores and citations.
"""

import json
import numpy as np
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


def load_config(config_path: str = 'configs/retrieval.yaml') -> Dict[str, Any]:
    """Load retrieval configuration."""
    with open(config_path, encoding='utf-8-sig') as f:
        return yaml.safe_load(f)


def load_embedding_model(config: Dict[str, Any]):
    """Load sentence transformer model for embedding queries."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-unresolved]
    except ImportError as exc:  # pragma: no cover - depends on runtime env
        raise RuntimeError(
            "sentence-transformers is required for RAG auditing. "
            "Install with `pip install sentence-transformers`."
        ) from exc

    model_name = config.get('embed_model', 'BAAI/bge-large-en-v1.5')
    device = config.get('embed_device', 'cpu')

    try:
        print(f"Loading embedding model: {model_name}")
        model = SentenceTransformer(model_name, device=device)
        print("✓ Model loaded successfully")
        return model
    except Exception as exc:  # pragma: no cover - runtime dependent
        raise RuntimeError(f"Failed to load embedding model '{model_name}': {exc}") from exc


def load_index(config: Dict[str, Any]) -> Tuple[Any, np.ndarray, Dict]:
    """
    Load FAISS index or numpy embeddings with metadata.
    
    Returns:
        Tuple of (faiss_index or None, embeddings, metadata)
    """
    db_path = Path(config.get('db_path', './tmp/faiss_index'))
    
    # Load metadata
    chunks_file = db_path / 'sources_chunks.json'
    if not chunks_file.exists():
        raise FileNotFoundError(f"Source index not found: {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Try to load FAISS index
    try:
        import faiss
        index_file = db_path / 'sources.index'
        if index_file.exists():
            index = faiss.read_index(str(index_file))
            print(f"✓ Loaded FAISS index: {index.ntotal} vectors")
            embeddings = None
        else:
            index = None
            embeddings = None
    except ImportError:
        index = None
        embeddings = None
    
    # Load numpy embeddings as fallback
    if index is None:
        embeddings_file = db_path / 'sources_embeddings.npy'
        if embeddings_file.exists():
            embeddings = np.load(embeddings_file)
            print(f"✓ Loaded embeddings: {embeddings.shape}")
        else:
            raise FileNotFoundError(f"No index or embeddings found in {db_path}")
    
    return index, embeddings, metadata


def retrieve_sources(
    query: str,
    index: Any,
    embeddings: np.ndarray,
    metadata: Dict,
    model,
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant source chunks for a query.
    
    Args:
        query: Query text
        index: FAISS index or None
        embeddings: Numpy embeddings array or None
        metadata: Index metadata with chunks
        model: Embedding model
        config: Retrieval configuration
    
    Returns:
        List of retrieved chunks with scores
    """
    retrieval_config = config.get('retrieval', {})
    top_k = retrieval_config.get('top_k', 6)
    min_score = retrieval_config.get('min_score', 0.5)
    
    # Embed query
    if model is None:
        raise RuntimeError("Embedding model must be available for auditing")

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )[0]
    
    # Search index
    if index is not None:
        # Use FAISS
        import faiss
        query_vec = query_embedding.reshape(1, -1).astype(np.float32)
        scores, indices = index.search(query_vec, top_k)
        scores = scores[0]
        indices = indices[0]
    elif embeddings is not None:
        # Use numpy cosine similarity
        similarities = np.dot(embeddings, query_embedding)
        indices = np.argsort(similarities)[::-1][:top_k]
        scores = similarities[indices]
    else:
        return []
    
    # Retrieve chunks
    all_chunks = metadata.get('chunks', [])
    results = []
    
    for idx, score in zip(indices, scores):
        if score < min_score:
            continue
        
        if idx < len(all_chunks):
            chunk = all_chunks[idx].copy()
            chunk['relevance_score'] = float(score)
            results.append(chunk)
    
    return results


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text."""
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_groundedness(
    sentence: str,
    retrieved_chunks: List[Dict[str, Any]]
) -> Tuple[float, List[str]]:
    """
    Calculate groundedness score for a sentence.
    
    Args:
        sentence: Sentence to verify
        retrieved_chunks: Retrieved source chunks
    
    Returns:
        Tuple of (groundedness_score, supporting_sources)
    """
    if not retrieved_chunks:
        return 0.0, []
    
    # Simple heuristic: check word overlap with retrieved chunks
    sentence_words = set(sentence.lower().split())
    
    max_overlap = 0.0
    supporting_sources = []
    
    for chunk in retrieved_chunks:
        chunk_text = chunk.get('text', '')
        chunk_words = set(chunk_text.lower().split())
        
        if not sentence_words:
            continue
        
        # Jaccard similarity
        overlap = len(sentence_words & chunk_words) / len(sentence_words | chunk_words)
        
        if overlap > max_overlap:
            max_overlap = overlap
        
        # If significant overlap, consider it supporting
        if overlap > 0.2:
            source_id = chunk.get('source_id', 'unknown')
            if source_id not in supporting_sources:
                supporting_sources.append(source_id)
    
    # Groundedness score based on best overlap
    groundedness_score = min(1.0, max_overlap * 2)  # Scale up
    
    return groundedness_score, supporting_sources


def audit_script(
    script_path: str,
    index: Any,
    embeddings: np.ndarray,
    metadata: Dict,
    model,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Audit script for groundedness.
    
    Args:
        script_path: Path to script markdown file
        index: FAISS index or None
        embeddings: Numpy embeddings or None
        metadata: Index metadata
        model: Embedding model
        config: Configuration
    
    Returns:
        Audit report dictionary
    """
    # Load script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Extract sentences (skip markdown headers)
    lines = script_content.split('\n')
    sentences = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract speaker text
        if ':' in line:
            _, text = line.split(':', 1)
            text = text.strip()
        else:
            text = line
        
        # Split into sentences
        line_sentences = extract_sentences(text)
        sentences.extend(line_sentences)
    
    print(f"Auditing {len(sentences)} sentences...")
    
    # Audit each sentence
    sentence_audits = []
    total_groundedness = 0.0
    
    for i, sentence in enumerate(sentences):
        if not sentence or len(sentence.split()) < 3:
            continue
        
        # Retrieve relevant sources
        retrieved = retrieve_sources(
            sentence,
            index,
            embeddings,
            metadata,
            model,
            config
        )
        
        # Calculate groundedness
        groundedness, sources = calculate_groundedness(sentence, retrieved)
        
        total_groundedness += groundedness
        
        sentence_audits.append({
            'sentence_id': i,
            'text': sentence,
            'groundedness': groundedness,
            'retrieved_chunks': len(retrieved),
            'supporting_sources': sources,
            'top_relevance': retrieved[0]['relevance_score'] if retrieved else 0.0
        })
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(sentences)} sentences...")
    
    # Calculate overall scores
    avg_groundedness = total_groundedness / len(sentence_audits) if sentence_audits else 0.0
    
    # Count sentences above threshold
    quality_config = config.get('quality', {})
    min_groundedness = quality_config.get('min_groundedness', 0.8)
    
    grounded_sentences = sum(
        1 for audit in sentence_audits if audit['groundedness'] >= min_groundedness
    )
    
    # Create report
    report = {
        'script_path': script_path,
        'total_sentences': len(sentence_audits),
        'avg_groundedness': avg_groundedness,
        'grounded_sentences': grounded_sentences,
        'grounded_percentage': grounded_sentences / len(sentence_audits) * 100 if sentence_audits else 0,
        'min_groundedness_threshold': min_groundedness,
        'passed': avg_groundedness >= min_groundedness,
        'sentence_audits': sentence_audits,
        'sources_used': metadata.get('num_sources', 0),
        'chunks_indexed': metadata.get('num_chunks', 0)
    }
    
    print(f"\n✓ Audit complete!")
    print(f"  Average groundedness: {avg_groundedness:.3f}")
    print(f"  Grounded sentences: {grounded_sentences}/{len(sentence_audits)} ({report['grounded_percentage']:.1f}%)")
    print(f"  Passed: {report['passed']}")
    
    return report


def audit_job(
    job_dir: str,
    config_path: str = 'configs/retrieval.yaml'
) -> Dict[str, Any]:
    """
    Main auditing function for a job.
    
    Args:
        job_dir: Path to job directory
        config_path: Path to retrieval config
    
    Returns:
        Audit report dictionary
    """
    job_path = Path(job_dir)
    
    # Load configuration
    config = load_config(config_path)
    
    # Load embedding model
    model = load_embedding_model(config)
    
    # Load source index
    try:
        index, embeddings, metadata = load_index(config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run source_indexer.py first to create the index")
        return {'error': str(e)}
    
    # Find script file
    script_path = job_path / 'script.md'
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}")
        return {'error': 'script not found'}
    
    # Audit script
    report = audit_script(
        str(script_path),
        index,
        embeddings,
        metadata,
        model,
        config
    )
    
    # Save report
    report_path = job_path / 'audit_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved audit report to: {report_path}")
    
    return report


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auditor.py --job <job_dir>")
        print("Example: python auditor.py --job tests/fixtures/phase2_test")
        sys.exit(1)
    
    if sys.argv[1] == '--job':
        if len(sys.argv) < 3:
            print("Error: Job directory required")
            sys.exit(1)
        
        job_dir = sys.argv[2]
        report = audit_job(job_dir)
        
        if 'error' in report:
            sys.exit(1)
