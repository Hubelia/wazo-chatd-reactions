# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Data Access Object for message replies.

This DAO provides database operations for the chatd_room_message_reply table.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Import the scoped session directly from wazo-chatd
from wazo_chatd.database.helpers import Session

logger = logging.getLogger(__name__)


class ReplyDAO:
    """DAO for reply database operations."""

    def __init__(self):
        pass
    
    @property
    def _session(self):
        """Get the current session."""
        return Session()

    def get_by_child(self, child_message_uuid):
        """Get reply info for a specific message (if it's a reply)."""
        query = text("""
            SELECT child_message_uuid, parent_message_uuid, room_uuid,
                   parent_content_preview, parent_author_uuid, parent_author_alias,
                   parent_created_at, created_at
            FROM chatd_room_message_reply
            WHERE child_message_uuid = :child_message_uuid
        """)
        result = self._session.execute(
            query,
            {'child_message_uuid': str(child_message_uuid)}
        ).fetchone()
        
        if result:
            return ReplyResult(
                child_message_uuid=result[0],
                parent_message_uuid=result[1],
                room_uuid=result[2],
                parent_content_preview=result[3],
                parent_author_uuid=result[4],
                parent_author_alias=result[5],
                parent_created_at=result[6],
                created_at=result[7],
            )
        return None

    def get_replies_to_message(self, parent_message_uuid):
        """Get all messages that are replies to a specific message."""
        query = text("""
            SELECT child_message_uuid, parent_message_uuid, room_uuid,
                   parent_content_preview, parent_author_uuid, parent_author_alias,
                   parent_created_at, created_at
            FROM chatd_room_message_reply
            WHERE parent_message_uuid = :parent_message_uuid
            ORDER BY created_at ASC
        """)
        results = self._session.execute(
            query,
            {'parent_message_uuid': str(parent_message_uuid)}
        ).fetchall()
        
        return [
            ReplyResult(
                child_message_uuid=row[0],
                parent_message_uuid=row[1],
                room_uuid=row[2],
                parent_content_preview=row[3],
                parent_author_uuid=row[4],
                parent_author_alias=row[5],
                parent_created_at=row[6],
                created_at=row[7],
            )
            for row in results
        ]

    def get_reply_count(self, parent_message_uuid):
        """Get the count of replies to a message."""
        query = text("""
            SELECT COUNT(*)
            FROM chatd_room_message_reply
            WHERE parent_message_uuid = :parent_message_uuid
        """)
        result = self._session.execute(
            query,
            {'parent_message_uuid': str(parent_message_uuid)}
        ).fetchone()
        return result[0] if result else 0

    def get_replies_in_room(self, room_uuid):
        """Get all reply relationships in a room (for batch loading)."""
        query = text("""
            SELECT child_message_uuid, parent_message_uuid, room_uuid,
                   parent_content_preview, parent_author_uuid, parent_author_alias,
                   parent_created_at, created_at
            FROM chatd_room_message_reply
            WHERE room_uuid = :room_uuid
            ORDER BY created_at ASC
        """)
        results = self._session.execute(
            query,
            {'room_uuid': str(room_uuid)}
        ).fetchall()
        
        return [
            ReplyResult(
                child_message_uuid=row[0],
                parent_message_uuid=row[1],
                room_uuid=row[2],
                parent_content_preview=row[3],
                parent_author_uuid=row[4],
                parent_author_alias=row[5],
                parent_created_at=row[6],
                created_at=row[7],
            )
            for row in results
        ]

    def create(self, child_message_uuid, parent_message_uuid, room_uuid,
               parent_content_preview, parent_author_uuid, parent_author_alias,
               parent_created_at):
        """Create a new reply relationship."""
        now = datetime.now(timezone.utc)
        
        query = text("""
            INSERT INTO chatd_room_message_reply 
                (child_message_uuid, parent_message_uuid, room_uuid,
                 parent_content_preview, parent_author_uuid, parent_author_alias,
                 parent_created_at, created_at)
            VALUES 
                (:child_message_uuid, :parent_message_uuid, :room_uuid,
                 :parent_content_preview, :parent_author_uuid, :parent_author_alias,
                 :parent_created_at, :created_at)
            RETURNING child_message_uuid, parent_message_uuid, room_uuid,
                      parent_content_preview, parent_author_uuid, parent_author_alias,
                      parent_created_at, created_at
        """)
        
        try:
            result = self._session.execute(
                query,
                {
                    'child_message_uuid': str(child_message_uuid),
                    'parent_message_uuid': str(parent_message_uuid) if parent_message_uuid else None,
                    'room_uuid': str(room_uuid),
                    'parent_content_preview': parent_content_preview[:200] if parent_content_preview else None,
                    'parent_author_uuid': str(parent_author_uuid) if parent_author_uuid else None,
                    'parent_author_alias': parent_author_alias,
                    'parent_created_at': parent_created_at,
                    'created_at': now,
                }
            ).fetchone()
            self._session.commit()
            
            return ReplyResult(
                child_message_uuid=result[0],
                parent_message_uuid=result[1],
                room_uuid=result[2],
                parent_content_preview=result[3],
                parent_author_uuid=result[4],
                parent_author_alias=result[5],
                parent_created_at=result[6],
                created_at=result[7],
            )
        except IntegrityError:
            self._session.rollback()
            raise

    def delete(self, child_message_uuid):
        """Delete a reply relationship."""
        query = text("""
            DELETE FROM chatd_room_message_reply
            WHERE child_message_uuid = :child_message_uuid
        """)
        
        self._session.execute(
            query,
            {'child_message_uuid': str(child_message_uuid)}
        )
        self._session.commit()


class ReplyResult:
    """Simple result object for reply data."""
    
    def __init__(self, child_message_uuid, parent_message_uuid, room_uuid,
                 parent_content_preview, parent_author_uuid, parent_author_alias,
                 parent_created_at, created_at):
        self.child_message_uuid = child_message_uuid
        self.parent_message_uuid = parent_message_uuid
        self.room_uuid = room_uuid
        self.parent_content_preview = parent_content_preview
        self.parent_author_uuid = parent_author_uuid
        self.parent_author_alias = parent_author_alias
        self.parent_created_at = parent_created_at
        self.created_at = created_at
