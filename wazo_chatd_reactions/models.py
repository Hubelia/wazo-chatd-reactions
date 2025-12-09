# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType, generic_repr

# We use the same Base as wazo-chatd
# This will be imported from wazo_chatd.database.models at runtime
Base = declarative_base()


@generic_repr
class RoomMessageReaction(Base):
    """Model for message reactions.
    
    Each row represents one user's reaction (emoji) to a message.
    A user can add multiple different emojis to a message, but not the same emoji twice.
    """
    
    __tablename__ = 'chatd_room_message_reaction'
    __table_args__ = (
        Index('idx_chatd_reaction_message_uuid', 'message_uuid'),
        Index('idx_chatd_reaction_user_uuid', 'user_uuid'),
    )

    message_uuid = Column(
        UUIDType(),
        ForeignKey('chatd_room_message.uuid', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )

    user_uuid = Column(
        UUIDType(),
        primary_key=True,
        nullable=False,
    )

    emoji = Column(
        String(10),
        primary_key=True,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("(now() at time zone 'utc')"),
        nullable=False,
    )
