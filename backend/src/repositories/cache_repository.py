"""Cache repository - operations for LLMCache."""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cache import LLMCache


class CacheRepository:
    """Repository for LLM cache operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def generate_cache_key(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 600
    ) -> str:
        """
        Generate SHA-256 cache key from normalized prompt and parameters.

        Args:
            prompt: The prompt text
            model: Model identifier
            temperature: Temperature parameter
            max_tokens: Max tokens parameter

        Returns:
            64-character hex string (SHA-256 hash)
        """
        # Normalize prompt (strip whitespace, lowercase)
        normalized_prompt = " ".join(prompt.lower().split())

        # Create stable JSON representation
        cache_input = {
            "prompt": normalized_prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Generate SHA-256 hash
        cache_str = json.dumps(cache_input, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def get_cached_response(
        self,
        cache_key_hash: str
    ) -> Optional[str]:
        """
        Get cached response and update last_accessed_at.

        Returns None if cache miss or expired.
        """
        stmt = select(LLMCache).where(LLMCache.cache_key_hash == cache_key_hash)
        result = await self.session.execute(stmt)
        cache_entry = result.scalar_one_or_none()

        if not cache_entry:
            return None

        # Check expiration
        if cache_entry.expires_at and cache_entry.expires_at < datetime.utcnow():
            return None

        # Update last_accessed_at
        cache_entry.last_accessed_at = datetime.utcnow()
        await self.session.commit()

        return cache_entry.response_text

    async def set_cached_response(
        self,
        prompt: str,
        response: str,
        model: str,
        token_count: int,
        temperature: float = 0.7,
        max_tokens: int = 600,
        ttl_days: Optional[int] = None
    ) -> LLMCache:
        """
        Cache an LLM response with optional TTL.

        Args:
            prompt: Original prompt text
            response: LLM response text
            model: Model identifier
            token_count: Total tokens (prompt + response)
            temperature: Temperature parameter
            max_tokens: Max tokens parameter
            ttl_days: Time-to-live in days (None = indefinite)

        Returns:
            Created cache entry
        """
        cache_key_hash = self.generate_cache_key(prompt, model, temperature, max_tokens)

        expires_at = None
        if ttl_days:
            expires_at = datetime.utcnow() + timedelta(days=ttl_days)

        cache_entry = LLMCache(
            cache_key_hash=cache_key_hash,
            prompt_text=prompt,
            response_text=response,
            model=model,
            token_count=token_count,
            expires_at=expires_at
        )

        # Use merge to handle duplicate key (upsert behavior)
        self.session.add(cache_entry)
        await self.session.commit()
        await self.session.refresh(cache_entry)

        return cache_entry

    async def purge_expired_cache(self, days_inactive: int = 60) -> int:
        """
        Purge cache entries not accessed in specified days.

        Args:
            days_inactive: Delete entries not accessed in this many days

        Returns:
            Number of entries deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

        stmt = delete(LLMCache).where(LLMCache.last_accessed_at < cutoff_date)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount
