# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from .events import (
    UserRoomMessageReactionCreatedEvent,
    UserRoomMessageReactionDeletedEvent,
    UserRoomMessageReplyCreatedEvent,
)

logger = logging.getLogger(__name__)


class ReactionNotifier:
    """Notifier for reaction events via WebSocket/Bus."""

    def __init__(self, bus_publisher):
        self._bus_publisher = bus_publisher

    def reaction_created(self, room, message, reaction):
        """Notify all room users that a reaction was created."""
        logger.debug(
            'Notifying reaction created: message=%s, user=%s, emoji=%s',
            reaction.message_uuid,
            reaction.user_uuid,
            reaction.emoji,
        )
        
        # Include room_uuid and message_uuid in data for WebSocket clients
        reaction_data = {
            'emoji': reaction.emoji,
            'user_uuid': str(reaction.user_uuid),
            'created_at': reaction.created_at.isoformat() if reaction.created_at else None,
            'room_uuid': str(room.uuid),
            'message_uuid': str(reaction.message_uuid),
        }
        
        # Notify each user in the room
        for user in room.users:
            event = UserRoomMessageReactionCreatedEvent(
                reaction_data,
                room_uuid=str(room.uuid),
                message_uuid=str(reaction.message_uuid),
                tenant_uuid=str(room.tenant_uuid),
                user_uuid=str(user.uuid),
            )
            self._bus_publisher.publish(event)

    def reaction_deleted(self, room, message, user_uuid, emoji):
        """Notify all room users that a reaction was deleted."""
        logger.debug(
            'Notifying reaction deleted: message=%s, user=%s, emoji=%s',
            message.uuid,
            user_uuid,
            emoji,
        )
        
        # Include room_uuid and message_uuid in data for WebSocket clients
        reaction_data = {
            'emoji': emoji,
            'user_uuid': str(user_uuid),
            'room_uuid': str(room.uuid),
            'message_uuid': str(message.uuid),
        }
        
        # Notify each user in the room
        for user in room.users:
            event = UserRoomMessageReactionDeletedEvent(
                reaction_data,
                room_uuid=str(room.uuid),
                message_uuid=str(message.uuid),
                tenant_uuid=str(room.tenant_uuid),
                user_uuid=str(user.uuid),
            )
            self._bus_publisher.publish(event)

    def reply_created(self, room, child_message, parent_message, reply):
        """Notify all room users that a reply was created."""
        logger.debug(
            'Notifying reply created: parent=%s, child=%s',
            reply.parent_message_uuid,
            reply.child_message_uuid,
        )
        
        # Include all necessary data for WebSocket clients
        reply_data = {
            'room_uuid': str(room.uuid),
            'child_message_uuid': str(reply.child_message_uuid),
            'parent_message_uuid': str(reply.parent_message_uuid),
            'parent_preview': {
                'content': reply.parent_content_preview,
                'author_uuid': str(reply.parent_author_uuid) if reply.parent_author_uuid else None,
                'author_alias': reply.parent_author_alias,
                'created_at': reply.parent_created_at.isoformat() if reply.parent_created_at else None,
            },
            'created_at': reply.created_at.isoformat() if reply.created_at else None,
        }
        
        # Notify each user in the room
        for user in room.users:
            event = UserRoomMessageReplyCreatedEvent(
                reply_data,
                room_uuid=str(room.uuid),
                parent_message_uuid=str(reply.parent_message_uuid),
                child_message_uuid=str(reply.child_message_uuid),
                tenant_uuid=str(room.tenant_uuid),
                user_uuid=str(user.uuid),
            )
            self._bus_publisher.publish(event)
