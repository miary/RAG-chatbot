import logging
import math
import os
from typing import List

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    NamedVector,
    NamedSparseVector,
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
DENSE_MODEL_PATH = os.path.join(MODELS_DIR, 'dense')   # e.g., all-MiniLM-L6-v2 or nomic-embed-text
SPARSE_MODEL_PATH = os.path.join(MODELS_DIR, 'sparse')  # e.g., splade-cocondenser-ensembledistil

# Embedding dimensions
DENSE_EMBEDDING_DIM = int(os.environ.get('DENSE_EMBEDDING_DIM', '384'))  # Default for all-MiniLM-L6-v2
MRL_EMBEDDING_DIM = int(os.environ.get('MRL_EMBEDDING_DIM', '256'))      # MRL truncation target
USE_MRL = os.environ.get('USE_MRL', 'true').lower() == 'true'

# Final dimension used in Qdrant
EMBEDDING_DIM = MRL_EMBEDDING_DIM if USE_MRL else DENSE_EMBEDDING_DIM


def get_dense_model():
    """Load the dense embedding model from local directory."""
    global _dense_model
    if _dense_model is None:
        from sentence_transformers import SentenceTransformer
        
        if os.path.exists(DENSE_MODEL_PATH):
            logger.info('Loading dense model from local path: %s', DENSE_MODEL_PATH)
            _dense_model = SentenceTransformer(DENSE_MODEL_PATH)
        else:
            # Fallback: try to load by name (will download if not exists)
            model_name = os.environ.get('DENSE_MODEL_NAME', 'all-MiniLM-L6-v2')
            logger.warning('Local dense model not found at %s, loading: %s', DENSE_MODEL_PATH, model_name)
            _dense_model = SentenceTransformer(model_name)
        
        logger.info('Dense model loaded. Embedding dimension: %d', _dense_model.get_sentence_embedding_dimension())
    return _dense_model


def get_sparse_model():
    """Load the sparse embedding model (SPLADE) from local directory."""
    global _sparse_model
    if _sparse_model is None:
        try:
            from transformers import AutoModelForMaskedLM, AutoTokenizer
            import torch
            
            if os.path.exists(SPARSE_MODEL_PATH):
                logger.info('Loading sparse model from local path: %s', SPARSE_MODEL_PATH)
                tokenizer = AutoTokenizer.from_pretrained(SPARSE_MODEL_PATH)
                model = AutoModelForMaskedLM.from_pretrained(SPARSE_MODEL_PATH)
                _sparse_model = {'tokenizer': tokenizer, 'model': model}
            else:
                # Fallback: try to load by name
                model_name = os.environ.get('SPARSE_MODEL_NAME', 'naver/splade-cocondenser-ensembledistil')
                logger.warning('Local sparse model not found at %s, loading: %s', SPARSE_MODEL_PATH, model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForMaskedLM.from_pretrained(model_name)
                _sparse_model = {'tokenizer': tokenizer, 'model': model}
            
            logger.info('Sparse model (SPLADE) loaded successfully.')
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
    """Generate dense embeddings for a list of texts using local model."""
    model = get_dense_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    if USE_MRL:
        return apply_mrl(embeddings, MRL_EMBEDDING_DIM)
    else:
        return [emb.tolist() for emb in embeddings]


def embed_texts_sparse(texts: list) -> list:
    """Generate sparse embeddings using SPLADE model."""
    sparse_model = get_sparse_model()
    if sparse_model is None:
        return [None] * len(texts)
    
    import torch
    
    tokenizer = sparse_model['tokenizer']
    model = sparse_model['model']
    model.eval()
    
    sparse_vectors = []
    with torch.no_grad():
        for text in texts:
            inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            outputs = model(**inputs)
            
            # SPLADE: log(1 + ReLU(logits)) * attention_mask
            logits = outputs.logits
            relu_log = torch.log1p(torch.relu(logits))
            weighted = relu_log * inputs['attention_mask'].unsqueeze(-1)
            
            # Max pooling over sequence length
            sparse_vec, _ = torch.max(weighted, dim=1)
            sparse_vec = sparse_vec.squeeze()
            
            # Get non-zero indices and values
            non_zero_mask = sparse_vec > 0
            indices = torch.where(non_zero_mask)[0].tolist()
            values = sparse_vec[non_zero_mask].tolist()
            
            sparse_vectors.append({'indices': indices, 'values': values})
    
    return sparse_vectors


def embed_query_dense(query: str) -> list:
    """Generate dense embedding for a single query."""
    embeddings = embed_texts_dense([query])
    return embeddings[0]


def embed_query_sparse(query: str) -> dict:
    """Generate sparse embedding for a single query."""
    sparse_vectors = embed_texts_sparse([query])
    return sparse_vectors[0]


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
    - Dense vectors: For semantic similarity (MRL-truncated if enabled)
    - Sparse vectors: For keyword matching (SPLADE)
    
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
        logger.info('Creating collection with hybrid search (dense + sparse vectors)')
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
    
    texts = [d['content'] for d in documents]
    
    # Generate embeddings
    dense_embeddings = embed_texts_dense(texts)
    sparse_embeddings = embed_texts_sparse(texts)
    
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
    """Search using hybrid retrieval (dense + sparse) with reciprocal rank fusion.
    
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
