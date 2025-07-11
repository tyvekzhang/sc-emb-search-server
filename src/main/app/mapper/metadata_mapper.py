"""Metadata mapper"""

from typing import List, Optional, Tuple

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from src.main.app.mapper.mapper_base_impl import SqlModelMapper
from src.main.app.model.metadata_model import MetadataEntity


class MetadataMapper(SqlModelMapper[MetadataEntity]):
    async def get_docs_by_vector(
            self,
            embedding: List[float],
            db_session: Optional[AsyncSession] = None,
            top_k: int = 5,
            similarity_threshold: Optional[float] = None
    ) -> List[Tuple[MetadataEntity, float]]:
        """
        Search for documents based on vector similarity and return with similarity scores.

        Args:
            embedding: The query vector.
            db_session: The database session. If None, uses self.db.session.
            top_k: Return the top K most similar results. Defaults to 5.
            similarity_threshold: The minimum similarity score (0-1). Defaults to None.

        Returns:
            List of tuples containing (MetadataEntity, similarity_score)
        """
        db_session = db_session or self.db.session

        # Calculate cosine similarity (1 - normalized L2 distance)
        # Using raw SQL for better performance with pgvector
        query = text("""
            SELECT *, 
                   1 - (cell_embedding <=> :embedding) AS similarity_score
            FROM metadata
            ORDER BY cell_embedding <=> :embedding
            LIMIT :limit
        """)

        # Execute the query with parameters
        result = await db_session.execute(
            query,
            {"embedding": str(embedding), "limit": top_k}
        )

        # Fetch all results with similarity scores
        results_with_scores = [
            (MetadataEntity(**dict(row)), row.similarity_score)
            for row in result.mappings()
        ]

        # Apply similarity threshold if provided
        if similarity_threshold is not None:
            results_with_scores = [
                doc for doc, score in results_with_scores
                if score >= similarity_threshold
            ]

        return results_with_scores


metadataMapper = MetadataMapper(MetadataEntity)