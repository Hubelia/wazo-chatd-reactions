# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from .events import (
    UserRoomMessageReactionCreatedEvent,
    UserRoomMessageReactionDeletedEvent,
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
        
        reaction_data = {
            'emoji': reaction.emoji,
            'user_uuid': str(reaction.user_uuid),
            'created_at': reaction.created_at.isoformat() if reaction.created_at else None,
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
        
        reaction_data = {
            'emoji': emoji,
            'user_uuid': str(user_uuid),
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
