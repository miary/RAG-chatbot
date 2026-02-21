import logging
from typing import List

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Global instances (lazy loaded)
_embedder = None
_qdrant_client = None


def get_embedder():
    global _embedder
    if _embedder is None:
        logger.info('Loading sentence-transformers model...')
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info('Embedding model loaded.')
    return _embedder


def get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        logger.info('Connected to Qdrant at %s:%s', settings.QDRANT_HOST, settings.QDRANT_PORT)
    return _qdrant_client


def ensure_collection():
    """Create the Qdrant collection if it doesn't already exist."""
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    collections = [c.name for c in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  # all-MiniLM-L6-v2 output dimension
                distance=Distance.COSINE,
            ),
        )
        logger.info('Created Qdrant collection: %s', collection_name)
    else:
        logger.info('Qdrant collection "%s" already exists.', collection_name)


def ingest_documents(documents: list[dict]):
    """Ingest a list of documents into Qdrant.

    Each document should have:
      - id: unique int
      - title: str
      - content: str  (the text that will be embedded)
      - metadata: dict (extra payload stored alongside)
    """
    embedder = get_embedder()
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION

    texts = [d['content'] for d in documents]
    embeddings = embedder.encode(texts).tolist()

    points = [
        PointStruct(
            id=doc['id'],
            vector=emb,
            payload={
                'title': doc.get('title', ''),
                'content': doc['content'],
                **doc.get('metadata', {}),
            },
        )
        for doc, emb in zip(documents, embeddings)
    ]

    client.upsert(collection_name=collection_name, points=points)
    logger.info('Ingested %d documents into Qdrant.', len(points))


def search_similar(query: str, top_k: int = 3) -> List[dict]:
    """Return the top_k most relevant documents for the given query."""
    embedder = get_embedder()
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION

    query_vector = embedder.encode(query).tolist()

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
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
