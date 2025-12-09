# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Data Access Object for reactions.

This DAO provides database operations for the chatd_room_message_reaction table.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Import the scoped session directly from wazo-chatd
from wazo_chatd.database.helpers import Session

logger = logging.getLogger(__name__)


class ReactionDAO:
    """DAO for reaction database operations."""

    def __init__(self):
        # Use the shared Session from wazo-chatd
        pass
    
    @property
    def _session(self):
        """Get the current session."""
        return Session()

    def get(self, message_uuid, user_uuid, emoji):
        """Get a specific reaction."""
        query = text("""
            SELECT message_uuid, user_uuid, emoji, created_at
            FROM chatd_room_message_reaction
            WHERE message_uuid = :message_uuid
              AND user_uuid = :user_uuid
              AND emoji = :emoji
        """)
        result = self._session.execute(
            query,
            {
                'message_uuid': str(message_uuid),
                'user_uuid': str(user_uuid),
                'emoji': emoji,
            }
        ).fetchone()
        
        if result:
            return ReactionResult(
                message_uuid=result[0],
                user_uuid=result[1],
                emoji=result[2],
                created_at=result[3],
            )
        return None

    def get_by_message(self, message_uuid):
        """Get all reactions for a message."""
        query = text("""
            SELECT message_uuid, user_uuid, emoji, created_at
            FROM chatd_room_message_reaction
            WHERE message_uuid = :message_uuid
            ORDER BY created_at ASC
        """)
        results = self._session.execute(
            query,
            {'message_uuid': str(message_uuid)}
        ).fetchall()
        
        return [
            ReactionResult(
                message_uuid=row[0],
                user_uuid=row[1],
                emoji=row[2],
                created_at=row[3],
            )
            for row in results
        ]

    def create(self, message_uuid, user_uuid, emoji):
        """Create a new reaction."""
        now = datetime.now(timezone.utc)
        
        query = text("""
            INSERT INTO chatd_room_message_reaction 
                (message_uuid, user_uuid, emoji, created_at)
            VALUES 
                (:message_uuid, :user_uuid, :emoji, :created_at)
            RETURNING message_uuid, user_uuid, emoji, created_at
        """)
        
        try:
            result = self._session.execute(
                query,
                {
                    'message_uuid': str(message_uuid),
                    'user_uuid': str(user_uuid),
                    'emoji': emoji,
                    'created_at': now,
                }
            ).fetchone()
            self._session.commit()
            
            return ReactionResult(
                message_uuid=result[0],
                user_uuid=result[1],
                emoji=result[2],
                created_at=result[3],
            )
        except IntegrityError:
            self._session.rollback()
            raise

    def delete(self, message_uuid, user_uuid, emoji):
        """Delete a reaction."""
        query = text("""
            DELETE FROM chatd_room_message_reaction
            WHERE message_uuid = :message_uuid
              AND user_uuid = :user_uuid
              AND emoji = :emoji
        """)
        
        self._session.execute(
            query,
            {
                'message_uuid': str(message_uuid),
                'user_uuid': str(user_uuid),
                'emoji': emoji,
            }
        )
        self._session.commit()


class ReactionResult:
    """Simple result object for reaction data."""
    
    def __init__(self, message_uuid, user_uuid, emoji, created_at):
        self.message_uuid = message_uuid
        self.user_uuid = user_uuid
        self.emoji = emoji
        self.created_at = created_at
