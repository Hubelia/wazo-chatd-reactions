# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from .exceptions import (
    MessageNotFoundException,
    RoomNotFoundException,
)

logger = logging.getLogger(__name__)


class ReplyService:
    """Service for managing message replies/threading."""

    def __init__(self, chatd_dao, reply_dao, notifier):
        """Initialize the reply service.
        
        Args:
            chatd_dao: The main chatd DAO (for room/message access)
            reply_dao: Our reply-specific DAO
            notifier: ReplyNotifier for WebSocket events
        """
        self._chatd_dao = chatd_dao
        self._reply_dao = reply_dao
        self._notifier = notifier

    def get_reply_info(self, tenant_uuid, room_uuid, message_uuid):
        """Get reply info for a specific message.
        
        Returns the parent message info if this message is a reply.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        
        # Verify message exists in room
        self._get_message(room, message_uuid)
        
        # Get reply relationship
        reply = self._reply_dao.get_by_child(message_uuid)
        
        if not reply:
            return None
        
        return {
            'child_message_uuid': str(reply.child_message_uuid),
            'parent_message_uuid': str(reply.parent_message_uuid) if reply.parent_message_uuid else None,
            'room_uuid': str(reply.room_uuid),
            'parent_preview': {
                'content': reply.parent_content_preview,
                'author_uuid': str(reply.parent_author_uuid) if reply.parent_author_uuid else None,
                'author_alias': reply.parent_author_alias,
                'created_at': reply.parent_created_at.isoformat() if reply.parent_created_at else None,
            } if reply.parent_content_preview else None,
        }

    def get_replies_to_message(self, tenant_uuid, room_uuid, message_uuid):
        """Get all replies to a specific message.
        
        Returns a list of message UUIDs that are replies to this message.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        
        # Verify message exists in room
        self._get_message(room, message_uuid)
        
        # Get replies
        replies = self._reply_dao.get_replies_to_message(message_uuid)
        
        return {
            'parent_message_uuid': str(message_uuid),
            'reply_count': len(replies),
            'replies': [
                {
                    'message_uuid': str(r.child_message_uuid),
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in replies
            ],
        }

    def get_room_reply_metadata(self, tenant_uuid, room_uuid):
        """Get all reply metadata for a room (for batch loading).
        
        Returns a dict mapping message UUIDs to their reply info.
        """
        # Verify room exists
        self._get_room(tenant_uuid, room_uuid)
        
        # Get all replies in room
        replies = self._reply_dao.get_replies_in_room(room_uuid)
        
        result = {}
        for reply in replies:
            result[str(reply.child_message_uuid)] = {
                'parent_message_uuid': str(reply.parent_message_uuid) if reply.parent_message_uuid else None,
                'parent_preview': {
                    'content': reply.parent_content_preview,
                    'author_uuid': str(reply.parent_author_uuid) if reply.parent_author_uuid else None,
                    'author_alias': reply.parent_author_alias,
                    'created_at': reply.parent_created_at.isoformat() if reply.parent_created_at else None,
                } if reply.parent_content_preview else None,
            }
        
        return {
            'room_uuid': str(room_uuid),
            'replies': result,
        }

    def create_reply_relationship(self, tenant_uuid, room_uuid, child_message_uuid,
                                   parent_message_uuid, user_uuid):
        """Create a reply relationship between messages.
        
        This is called after the child message is created to establish the link.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        self._verify_user_in_room(room, user_uuid)
        
        # Verify child message exists
        child_message = self._get_message(room, child_message_uuid)
        
        # Get parent message for preview
        parent_message = self._get_message(room, parent_message_uuid)
        
        # Create the relationship with cached preview
        reply = self._reply_dao.create(
            child_message_uuid=child_message_uuid,
            parent_message_uuid=parent_message_uuid,
            room_uuid=room_uuid,
            parent_content_preview=parent_message.content[:200] if parent_message.content else None,
            parent_author_uuid=parent_message.user_uuid,
            parent_author_alias=parent_message.alias,
            parent_created_at=parent_message.created_at,
        )
        
        # Notify via WebSocket
        self._notifier.reply_created(room, child_message, parent_message, reply)
        
        return {
            'child_message_uuid': str(reply.child_message_uuid),
            'parent_message_uuid': str(reply.parent_message_uuid),
            'room_uuid': str(reply.room_uuid),
            'parent_preview': {
                'content': reply.parent_content_preview,
                'author_uuid': str(reply.parent_author_uuid) if reply.parent_author_uuid else None,
                'author_alias': reply.parent_author_alias,
                'created_at': reply.parent_created_at.isoformat() if reply.parent_created_at else None,
            },
        }

    def _get_room(self, tenant_uuid, room_uuid):
        """Get room by UUID, verifying tenant access."""
        room = self._chatd_dao.room.get([tenant_uuid], room_uuid)
        if not room:
            raise RoomNotFoundException(room_uuid)
        return room

    def _get_message(self, room, message_uuid):
        """Get message by UUID, verifying it belongs to room."""
        for message in room.messages:
            if str(message.uuid) == str(message_uuid):
                return message
        raise MessageNotFoundException(message_uuid)

    def _verify_user_in_room(self, room, user_uuid):
        """Verify user is a member of the room."""
        user_uuids = {str(user.uuid) for user in room.users}
        if str(user_uuid) not in user_uuids:
            raise RoomNotFoundException(room.uuid)
