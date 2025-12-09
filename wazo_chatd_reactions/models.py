# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, text
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


@generic_repr
class RoomMessageReply(Base):
    """Model for message reply relationships.
    
    This table tracks parent-child relationships between messages for threading.
    It also caches a preview of the parent message for efficient display.
    
    Note: The actual reply message is stored in chatd_room_message table.
    This table only tracks the relationship and cached preview.
    """
    
    __tablename__ = 'chatd_room_message_reply'
    __table_args__ = (
        Index('idx_chatd_reply_parent_uuid', 'parent_message_uuid'),
        Index('idx_chatd_reply_child_uuid', 'child_message_uuid'),
        Index('idx_chatd_reply_room_uuid', 'room_uuid'),
    )

    # The reply message UUID (child)
    child_message_uuid = Column(
        UUIDType(),
        ForeignKey('chatd_room_message.uuid', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )

    # The original message UUID (parent)
    parent_message_uuid = Column(
        UUIDType(),
        ForeignKey('chatd_room_message.uuid', ondelete='SET NULL'),
        nullable=True,  # Nullable in case parent is deleted
    )

    # Room UUID for efficient querying
    room_uuid = Column(
        UUIDType(),
        ForeignKey('chatd_room.uuid', ondelete='CASCADE'),
        nullable=False,
    )

    # Cached preview of parent message (for display when parent exists or was deleted)
    parent_content_preview = Column(
        String(200),  # First 200 chars of parent content
        nullable=True,
    )

    parent_author_uuid = Column(
        UUIDType(),
        nullable=True,
    )

    parent_author_alias = Column(
        String(256),
        nullable=True,
    )

    parent_created_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # When this reply relationship was created
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("(now() at time zone 'utc')"),
        nullable=False,
    )
