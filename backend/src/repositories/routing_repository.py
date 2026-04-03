"""Routing repository.

Operations for logging and querying routing decisions.
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.agent_session import RoutingDecision


class RoutingRepository:
    """Repository for routing decision operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_routing_decision(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        message: str,
        intent: str,
        confidence: float,
        target_agent: str,
    ) -> RoutingDecision:
        """
        Log a routing decision.

        Args:
            session_id: UUID of the agent session
            user_id: UUID of the user
            message: Student's original message
            intent: Classified intent category
            confidence: Routing confidence score (0-1)
            target_agent: Selected specialist agent name

        Returns:
            Created RoutingDecision
        """
        decision = RoutingDecision(
            session_id=session_id,
            user_id=user_id,
            message=message,
            intent=intent,
            confidence=confidence,
            target_agent=target_agent,
        )
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def get_session_routing_decisions(self, session_id: uuid.UUID) -> list[RoutingDecision]:
        """
        Get all routing decisions for a session.

        Args:
            session_id: UUID of the agent session

        Returns:
            List of RoutingDecision objects
        """
        stmt = (
            select(RoutingDecision)
            .where(RoutingDecision.session_id == session_id)
            .order_by(RoutingDecision.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_routing_stats(self, user_id: uuid.UUID) -> dict[str, int]:
        """
        Get routing statistics for a user (count per intent).

        Args:
            user_id: UUID of the user

        Returns:
            Dict mapping intent to count
        """
        stmt = (
            select(RoutingDecision.intent, func.count(RoutingDecision.id))
            .where(RoutingDecision.user_id == user_id)
            .group_by(RoutingDecision.intent)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}
