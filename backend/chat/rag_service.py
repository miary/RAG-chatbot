"""
RAG Service using Qdrant FastEmbed for hybrid search.

Dense Model: nomic-embed-text-v1.5 (768d -> 256d via MRL truncation)
Sparse Model: Qdrant/bm25 (BM25-based sparse embeddings)

Both models are loaded locally from the 'models' directory for offline deployment.
"""
import logging
import math
import os
from typing import List, Optional

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    SparseVector,
    Prefetch,
    FusionQuery,
    Fusion,
)

logger = logging.getLogger(__name__)

# Global instances (lazy loaded)
_dense_model = None
_sparse_model = None
_qdrant_client = None

# Model paths - loaded from local 'models' directory
MODELS_DIR = os.environ.get('MODELS_DIR', '/app/models')
DENSE_MODEL_PATH = os.path.join(MODELS_DIR, 'dense')
SPARSE_MODEL_PATH = os.path.join(MODELS_DIR, 'sparse')

# FastEmbed model names
DENSE_MODEL_NAME = os.environ.get('DENSE_MODEL_NAME', 'nomic-ai/nomic-embed-text-v1.5-Q')
SPARSE_MODEL_NAME = os.environ.get('SPARSE_MODEL_NAME', 'Qdrant/bm25')

# Embedding dimensions for nomic-embed-text with Matryoshka (MRL)
# nomic-embed-text produces 768-dimensional vectors but is trained with MRL
# allowing truncation to smaller dimensions (256, 128, 64) with minimal quality loss
DENSE_EMBEDDING_DIM = int(os.environ.get('DENSE_EMBEDDING_DIM', '768'))
MRL_EMBEDDING_DIM = int(os.environ.get('MRL_EMBEDDING_DIM', '256'))
USE_MRL = os.environ.get('USE_MRL', 'true').lower() == 'true'

# Final dimension used in Qdrant
EMBEDDING_DIM = MRL_EMBEDDING_DIM if USE_MRL else DENSE_EMBEDDING_DIM


def get_dense_model():
    """Load the nomic-embed-text dense embedding model using FastEmbed.
    
    nomic-embed-text is trained with Matryoshka Representation Learning (MRL),
    which means the first N dimensions of the embedding capture the most important
    semantic information. This allows truncation to 256 dimensions with minimal
    quality loss.
    """
    global _dense_model
    if _dense_model is None:
        from fastembed import TextEmbedding
        
        # Check if model exists locally
        cache_location_file = os.path.join(DENSE_MODEL_PATH, 'CACHE_LOCATION.txt')
        
        if os.path.exists(cache_location_file):
            # Model was downloaded to a cache directory
            with open(cache_location_file, 'r') as f:
                cache_info = f.read()
            logger.info('Dense model cache info: %s', cache_info.strip())
            # Load from the parent models directory as cache
            _dense_model = TextEmbedding(
                model_name=DENSE_MODEL_NAME,
                cache_dir=MODELS_DIR,
            )
        elif os.path.exists(DENSE_MODEL_PATH) and any(
            f.endswith(('.onnx', '.json')) for f in os.listdir(DENSE_MODEL_PATH) if os.path.isfile(os.path.join(DENSE_MODEL_PATH, f))
        ):
            # Model files exist directly in the path
            logger.info('Loading dense model from local path: %s', DENSE_MODEL_PATH)
            _dense_model = TextEmbedding(
                model_name=DENSE_MODEL_NAME,
                cache_dir=os.path.dirname(DENSE_MODEL_PATH),
            )
        else:
            # Fallback: Download model (will use default cache or MODELS_DIR)
            logger.warning('Local dense model not found, downloading: %s', DENSE_MODEL_NAME)
            _dense_model = TextEmbedding(
                model_name=DENSE_MODEL_NAME,
                cache_dir=MODELS_DIR,
            )
        
        # Test to get dimension
        test_emb = list(_dense_model.embed(["test"]))[0]
        full_dim = len(test_emb)
        logger.info(
            'nomic-embed-text loaded via FastEmbed. Full dim: %d, MRL truncated dim: %d',
            full_dim, MRL_EMBEDDING_DIM
        )
    return _dense_model


def get_sparse_model():
    """Load the BM25 sparse embedding model using FastEmbed."""
    global _sparse_model
    if _sparse_model is None:
        try:
            from fastembed import SparseTextEmbedding
            
            # Check if model exists locally
            cache_location_file = os.path.join(SPARSE_MODEL_PATH, 'CACHE_LOCATION.txt')
            
            if os.path.exists(cache_location_file):
                # Model was downloaded to a cache directory
                with open(cache_location_file, 'r') as f:
                    cache_info = f.read()
                logger.info('Sparse model cache info: %s', cache_info.strip())
                _sparse_model = SparseTextEmbedding(
                    model_name=SPARSE_MODEL_NAME,
                    cache_dir=MODELS_DIR,
                )
            elif os.path.exists(SPARSE_MODEL_PATH) and os.listdir(SPARSE_MODEL_PATH):
                # Model files exist
                logger.info('Loading sparse model from local path: %s', SPARSE_MODEL_PATH)
                _sparse_model = SparseTextEmbedding(
                    model_name=SPARSE_MODEL_NAME,
                    cache_dir=os.path.dirname(SPARSE_MODEL_PATH),
                )
            else:
                # Fallback: Download model
                logger.warning('Local sparse model not found, downloading: %s', SPARSE_MODEL_NAME)
                _sparse_model = SparseTextEmbedding(
                    model_name=SPARSE_MODEL_NAME,
                    cache_dir=MODELS_DIR,
                )
            
            logger.info('BM25 sparse model loaded via FastEmbed.')
        except Exception as e:
            logger.warning('Failed to load sparse model: %s. Sparse search will be disabled.', e)
            _sparse_model = None
    return _sparse_model


def normalize_vector(vector: list) -> list:
    """L2 normalize a vector for cosine similarity."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def apply_mrl(embeddings: list, target_dim: int = MRL_EMBEDDING_DIM) -> list:
    """Apply Matryoshka Representation Learning by truncating and normalizing vectors.
    
    MRL-trained models produce embeddings where the first N dimensions capture
    the most important semantic information.
    """
    truncated = []
    for emb in embeddings:
        # Convert to list if numpy array
        emb_list = emb.tolist() if hasattr(emb, 'tolist') else list(emb)
        # Truncate to first target_dim dimensions
        truncated_emb = emb_list[:target_dim]
        # Re-normalize for cosine similarity
        normalized_emb = normalize_vector(truncated_emb)
        truncated.append(normalized_emb)
    return truncated


def embed_texts_dense(texts: list) -> list:
    """Generate dense embeddings for a list of texts using FastEmbed."""
    model = get_dense_model()
    
    # FastEmbed returns a generator, convert to list
    embeddings = list(model.embed(texts))
    
    if USE_MRL:
        return apply_mrl(embeddings, MRL_EMBEDDING_DIM)
    else:
        return [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]


def embed_texts_sparse(texts: list) -> list:
    """Generate sparse embeddings using BM25 via FastEmbed."""
    sparse_model = get_sparse_model()
    if sparse_model is None:
        return [None] * len(texts)
    
    sparse_vectors = []
    # FastEmbed SparseTextEmbedding returns SparseEmbedding objects
    embeddings = list(sparse_model.embed(texts))
    
    for emb in embeddings:
        # FastEmbed SparseEmbedding has .indices and .values attributes
        sparse_vectors.append({
            'indices': emb.indices.tolist() if hasattr(emb.indices, 'tolist') else list(emb.indices),
            'values': emb.values.tolist() if hasattr(emb.values, 'tolist') else list(emb.values),
        })
    
    return sparse_vectors


def embed_query_dense(query: str) -> list:
    """Generate dense embedding for a single query."""
    # nomic-embed-text recommends prefixing queries with "search_query: "
    # and documents with "search_document: " for better retrieval
    prefixed_query = f"search_query: {query}"
    embeddings = embed_texts_dense([prefixed_query])
    return embeddings[0]


def embed_query_sparse(query: str) -> Optional[dict]:
    """Generate sparse embedding for a single query."""
    sparse_vectors = embed_texts_sparse([query])
    return sparse_vectors[0]


def embed_document_dense(text: str) -> list:
    """Generate dense embedding for a document (with proper prefix)."""
    prefixed_text = f"search_document: {text}"
    embeddings = embed_texts_dense([prefixed_text])
    return embeddings[0]


def get_qdrant():
    """Get or create Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            check_compatibility=False,
        )
        logger.info('Connected to Qdrant at %s:%s', settings.QDRANT_HOST, settings.QDRANT_PORT)
    return _qdrant_client


def ensure_collection():
    """Create the Qdrant collection with hybrid search support (dense + sparse vectors).
    
    The collection uses:
    - Dense vectors: For semantic similarity (MRL-truncated nomic-embed-text)
    - Sparse vectors: For keyword matching (BM25)
    
    Both are combined using reciprocal rank fusion for hybrid search.
    """
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    collections = [c.name for c in client.get_collections().collections]
    
    sparse_model = get_sparse_model()
    use_sparse = sparse_model is not None

    if collection_name in collections:
        # Check if collection has correct configuration
        info = client.get_collection(collection_name)
        
        # Check dense vector config
        vectors_config = info.config.params.vectors
        if isinstance(vectors_config, dict):
            dense_config = vectors_config.get('dense', {})
            existing_size = dense_config.size if hasattr(dense_config, 'size') else EMBEDDING_DIM
        else:
            existing_size = vectors_config.size if hasattr(vectors_config, 'size') else EMBEDDING_DIM
        
        if existing_size != EMBEDDING_DIM:
            logger.warning(
                'Collection "%s" has vector size %d, expected %d. Recreating...',
                collection_name,
                existing_size,
                EMBEDDING_DIM,
            )
            client.delete_collection(collection_name)
        else:
            logger.info('Qdrant collection "%s" already exists with correct dimensions (%d).', 
                       collection_name, EMBEDDING_DIM)
            return

    # Create collection with named vectors for hybrid search
    vectors_config = {
        'dense': VectorParams(
            size=EMBEDDING_DIM,
            distance=Distance.COSINE,
        ),
    }
    
    sparse_vectors_config = None
    if use_sparse:
        sparse_vectors_config = {
            'sparse': SparseVectorParams(
                index=SparseIndexParams(on_disk=False),
            ),
        }
        logger.info('Creating collection with hybrid search (dense + BM25 sparse vectors)')
    else:
        logger.info('Creating collection with dense vectors only (sparse model not available)')

    client.create_collection(
        collection_name=collection_name,
        vectors_config=vectors_config,
        sparse_vectors_config=sparse_vectors_config,
    )
    logger.info('Created Qdrant collection: %s (dense_dim=%d, sparse=%s)', 
               collection_name, EMBEDDING_DIM, use_sparse)


def ingest_documents(documents: list):
    """Ingest documents with both dense and sparse embeddings.
    
    Each document should have:
      - id: unique int
      - title: str
      - content: str
      - metadata: dict
    """
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    
    # Prepare texts with document prefix for nomic-embed-text
    texts = [f"search_document: {d['content']}" for d in documents]
    
    # Generate embeddings
    dense_embeddings = embed_texts_dense(texts)
    
    # For sparse, we don't need the prefix
    sparse_texts = [d['content'] for d in documents]
    sparse_embeddings = embed_texts_sparse(sparse_texts)
    
    use_sparse = sparse_embeddings[0] is not None

    points = []
    for doc, dense_emb, sparse_emb in zip(documents, dense_embeddings, sparse_embeddings):
        vector_data = {
            'dense': dense_emb,
        }
        
        if use_sparse and sparse_emb:
            vector_data['sparse'] = SparseVector(
                indices=sparse_emb['indices'],
                values=sparse_emb['values'],
            )
        
        points.append(PointStruct(
            id=doc['id'],
            vector=vector_data,
            payload={
                'title': doc.get('title', ''),
                'content': doc['content'],
                **doc.get('metadata', {}),
            },
        ))

    client.upsert(collection_name=collection_name, points=points)
    logger.info('Ingested %d documents into Qdrant (hybrid=%s).', len(points), use_sparse)


def search_similar(query: str, top_k: int = 3) -> List[dict]:
    """Search using hybrid retrieval (dense + BM25 sparse) with reciprocal rank fusion.
    
    If sparse model is not available, falls back to dense-only search.
    """
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    
    # Generate query embeddings
    dense_vector = embed_query_dense(query)
    sparse_vector = embed_query_sparse(query)
    
    use_sparse = sparse_vector is not None and sparse_vector.get('indices')
    
    if use_sparse:
        # Hybrid search with reciprocal rank fusion
        results = client.query_points(
            collection_name=collection_name,
            prefetch=[
                Prefetch(
                    query=dense_vector,
                    using='dense',
                    limit=top_k * 2,
                ),
                Prefetch(
                    query=SparseVector(
                        indices=sparse_vector['indices'],
                        values=sparse_vector['values'],
                    ),
                    using='sparse',
                    limit=top_k * 2,
                ),
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
        )
    else:
        # Dense-only search
        results = client.query_points(
            collection_name=collection_name,
            query=dense_vector,
            using='dense',
            limit=top_k,
        )

    docs = []
    for hit in results.points:
        docs.append({
            'id': hit.id,
            'score': hit.score,
            'title': hit.payload.get('title', ''),
            'content': hit.payload.get('content', ''),
            'category': hit.payload.get('category', ''),
            'severity': hit.payload.get('severity', ''),
            'resolution': hit.payload.get('resolution', ''),
        })
    return docs
