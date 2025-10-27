"""
packages/rag_audit/source_indexer.py

Indexes source documents from /sources_clean for RAG retrieval.
Supports both FAISS (local) and Qdrant (server-based) backends.
"""

import json
import numpy as np
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_config(config_path: str = 'configs/retrieval.yaml') -> Dict[str, Any]:
    """Load retrieval configuration."""
    with open(config_path, encoding='utf-8-sig') as f:
        return yaml.safe_load(f)


def load_embedding_model(config: Dict[str, Any]):
    """Load sentence transformer model for embedding."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-unresolved]
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "sentence-transformers is required for RAG indexing. "
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


def chunk_text(text: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chunk text according to strategy in config.
    
    Args:
        text: Source text to chunk
        config: Chunking configuration
    
    Returns:
        List of chunk dictionaries with text and metadata
    """
    chunking_config = config.get('chunking', {})
    strategy = chunking_config.get('strategy', 'sentence')
    chunk_size = chunking_config.get('chunk_size', 512)
    chunk_overlap = chunking_config.get('chunk_overlap', 64)
    
    chunks = []
    
    if strategy == 'sentence':
        # Simple sentence-based chunking
        sentences = text.split('. ')
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Rough token estimate (words * 1.3)
            estimated_tokens = len(current_chunk.split()) * 1.3
            
            if estimated_tokens >= chunk_size and current_chunk:
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': current_chunk.strip(),
                    'char_start': text.find(current_chunk),
                    'char_end': text.find(current_chunk) + len(current_chunk)
                })
                chunk_id += 1
                
                # Overlap: keep last sentence
                last_sentences = '. '.join(current_chunk.split('. ')[-2:])
                current_chunk = last_sentences + '. ' + sentence
            else:
                current_chunk += (' ' if current_chunk else '') + sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'chunk_id': chunk_id,
                'text': current_chunk.strip(),
                'char_start': text.find(current_chunk),
                'char_end': text.find(current_chunk) + len(current_chunk)
            })
    
    elif strategy == 'fixed':
        # Fixed-size character chunks with overlap
        text_len = len(text)
        chunk_id = 0
        start = 0
        
        while start < text_len:
            end = min(start + chunk_size * 4, text_len)  # ~4 chars per token
            chunk_text = text[start:end]
            
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'char_start': start,
                'char_end': end
            })
            
            chunk_id += 1
            start += chunk_size * 4 - chunk_overlap * 4
    
    else:
        # Default: treat whole text as one chunk
        chunks.append({
            'chunk_id': 0,
            'text': text,
            'char_start': 0,
            'char_end': len(text)
        })
    
    return chunks


def embed_chunks(chunks: List[Dict[str, Any]], model) -> np.ndarray:
    """Embed all chunks using the model."""
    if model is None:
        raise RuntimeError("Embedding model must be available to embed chunks")

    texts = [chunk['text'] for chunk in chunks]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    print(f"✓ Generated {len(embeddings)} embeddings")
    return embeddings


def build_faiss_index(
    chunks: List[Dict[str, Any]],
    embeddings: np.ndarray,
    config: Dict[str, Any],
    sources_metadata: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build FAISS index from chunk embeddings.
    
    Args:
        chunks: List of chunk dictionaries
        embeddings: Chunk embeddings (n_chunks, dim)
        config: Retrieval configuration
        sources_metadata: Metadata for each source file
    
    Returns:
        Index metadata dictionary
    """
    try:
        import faiss
    except ImportError:
        print("Warning: faiss-cpu not installed, saving numpy index only")
        faiss = None
    
    dim = embeddings.shape[1]
    n_chunks = len(chunks)
    
    # Create FAISS index if available
    if faiss is not None:
        index = faiss.IndexFlatIP(dim)  # Inner Product for cosine similarity
        index.add(embeddings.astype(np.float32))
        print(f"✓ Built FAISS index: {n_chunks} vectors, {dim}d")
    else:
        index = None
    
    # Prepare index directory
    db_path = Path(config.get('db_path', './tmp/faiss_index'))
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    if index is not None:
        import faiss
        index_file = db_path / 'sources.index'
        faiss.write_index(index, str(index_file))
        print(f"✓ Saved FAISS index to: {index_file}")
    
    # Save numpy embeddings (fallback)
    embeddings_file = db_path / 'sources_embeddings.npy'
    np.save(embeddings_file, embeddings)
    print(f"✓ Saved embeddings to: {embeddings_file}")
    
    # Save chunks metadata
    chunks_file = db_path / 'sources_chunks.json'
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump({
            'chunks': chunks,
            'sources': sources_metadata,
            'embedding_dim': dim,
            'num_chunks': n_chunks
        }, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved chunks metadata to: {chunks_file}")
    
    return {
        'index_path': str(db_path),
        'num_chunks': n_chunks,
        'embedding_dim': dim,
        'num_sources': len(sources_metadata)
    }


def build_qdrant_index(
    chunks: List[Dict[str, Any]],
    embeddings: np.ndarray,
    config: Dict[str, Any],
    sources_metadata: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build Qdrant collection from chunk embeddings.
    
    Args:
        chunks: List of chunk dictionaries
        embeddings: Chunk embeddings
        config: Retrieval configuration
        sources_metadata: Metadata for each source
    
    Returns:
        Index metadata dictionary
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
    except ImportError:
        print("Warning: qdrant-client not installed")
        print("Install with: pip install qdrant-client")
        return {'error': 'qdrant-client not installed'}
    
    qdrant_config = config.get('qdrant', {})
    url = qdrant_config.get('url', 'http://localhost:6333')
    collection_name = qdrant_config.get('collection_name', 'alexandria_sources')
    distance_metric = qdrant_config.get('distance', 'Cosine')
    
    # Map distance metric
    distance_map = {
        'Cosine': Distance.COSINE,
        'Euclid': Distance.EUCLID,
        'Dot': Distance.DOT
    }
    distance = distance_map.get(distance_metric, Distance.COSINE)
    
    try:
        client = QdrantClient(url=url)
        print(f"✓ Connected to Qdrant at {url}")
    except Exception as e:
        print(f"Error: Could not connect to Qdrant: {e}")
        print("Make sure Qdrant is running: docker compose up -d qdrant")
        return {'error': str(e)}
    
    # Create or recreate collection
    dim = embeddings.shape[1]
    
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dim, distance=distance)
        )
        print(f"✓ Created collection: {collection_name}")
    except Exception as e:
        print(f"Error creating collection: {e}")
        return {'error': str(e)}
    
    # Prepare points
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Find source metadata for this chunk
        source_id = chunk.get('source_id', 'unknown')
        source_meta = next(
            (s for s in sources_metadata if s['source_id'] == source_id),
            {}
        )
        
        points.append(PointStruct(
            id=i,
            vector=embedding.tolist(),
            payload={
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text'],
                'source_id': source_id,
                'source_file': source_meta.get('file_path', ''),
                'char_start': chunk.get('char_start', 0),
                'char_end': chunk.get('char_end', 0)
            }
        ))
    
    # Upload points in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=collection_name, points=batch)
        print(f"  Uploaded {i+len(batch)}/{len(points)} points")
    
    print(f"✓ Indexed {len(points)} chunks in Qdrant")
    
    return {
        'collection_name': collection_name,
        'num_chunks': len(points),
        'embedding_dim': dim,
        'num_sources': len(sources_metadata),
        'url': url
    }


def index_sources(
    sources_dir: str = 'knowledge/sources_clean',
    config_path: str = 'configs/retrieval.yaml',
    job_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main indexing function.
    
    Args:
        sources_dir: Directory containing clean source files
        config_path: Path to retrieval config
        job_dir: Optional job directory (for job-specific indexing)
    
    Returns:
        Index metadata dictionary
    """
    # Load configuration
    config = load_config(config_path)
    
    # Load embedding model
    model = load_embedding_model(config)
    
    # Find source files
    sources_path = Path(sources_dir)
    if not sources_path.exists():
        print(f"Error: Sources directory not found: {sources_dir}")
        return {'error': 'sources directory not found'}
    
    source_files = list(sources_path.glob('*.txt'))
    if not source_files:
        print(f"Warning: No source files found in {sources_dir}")
        return {'error': 'no source files found'}
    
    print(f"Found {len(source_files)} source files")
    
    # Process each source file
    all_chunks = []
    sources_metadata = []
    
    for source_file in source_files:
        print(f"\nProcessing: {source_file.name}")
        
        # Read source text
        with open(source_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            print(f"  Skipping empty file: {source_file.name}")
            continue
        
        # Chunk text
        chunks = chunk_text(text, config)
        print(f"  Created {len(chunks)} chunks")
        
        # Add source metadata to each chunk
        source_id = source_file.stem
        for chunk in chunks:
            chunk['source_id'] = source_id
            chunk['source_file'] = str(source_file)
        
        all_chunks.extend(chunks)
        
        sources_metadata.append({
            'source_id': source_id,
            'file_path': str(source_file),
            'file_name': source_file.name,
            'num_chunks': len(chunks)
        })
    
    if not all_chunks:
        print("Error: No chunks created from source files")
        return {'error': 'no chunks created'}
    
    print(f"\nTotal chunks: {len(all_chunks)}")
    
    # Embed all chunks
    embeddings = embed_chunks(all_chunks, model)
    
    # Build index based on config
    db_type = config.get('db', 'faiss')
    
    if db_type == 'qdrant':
        metadata = build_qdrant_index(all_chunks, embeddings, config, sources_metadata)
    else:  # faiss
        metadata = build_faiss_index(all_chunks, embeddings, config, sources_metadata)
    
    # Save index metadata to job dir if provided
    if job_dir:
        job_path = Path(job_dir)
        metadata_file = job_path / 'source_index_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"\n✓ Saved index metadata to: {metadata_file}")
    
    print(f"\n✓ Source indexing complete!")
    print(f"  Database: {db_type}")
    print(f"  Sources: {metadata.get('num_sources', 0)}")
    print(f"  Chunks: {metadata.get('num_chunks', 0)}")
    print(f"  Dimension: {metadata.get('embedding_dim', 0)}")
    
    return metadata


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--job':
        # Job-specific mode
        if len(sys.argv) < 3:
            print("Usage: python source_indexer.py --job <job_dir>")
            sys.exit(1)
        job_dir = sys.argv[2]
        index_sources(job_dir=job_dir)
    else:
        # Standard mode: index all sources
        index_sources()
