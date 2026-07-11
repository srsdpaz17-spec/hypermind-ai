"""Authentication-related entities (per-tenant schema).

`RefreshToken` implements the rotation strategy described in ADR-005:
tokens are stored hashed (never plaintext), can be revoked, and carry an
explicit expiry.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.base import BaseEntity


class RefreshToken(BaseEntity):
    """A hashed refresh token issued to a user, supporting rotation/revocation."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RefreshToken id={self.id} user_id={self.user_id} revoked={self.is_revoked}>"
