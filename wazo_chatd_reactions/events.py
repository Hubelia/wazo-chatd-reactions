# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Custom bus events for chat reactions and replies.

These events follow the same pattern as wazo-bus events.
"""

from wazo_bus.resources.common.event import UserEvent


class UserRoomMessageReactionCreatedEvent(UserEvent):
    """Event fired when a user adds a reaction to a message."""
    
    service = 'chatd'
    name = 'chatd_user_room_message_reaction_created'
    routing_key_fmt = 'chatd.users.{user_uuid}.rooms.{room_uuid}.messages.{message_uuid}.reactions.created'

    def __init__(
        self,
        reaction_data: dict,
        room_uuid: str,
        message_uuid: str,
        tenant_uuid: str,
        user_uuid: str,
    ):
        super().__init__(reaction_data, tenant_uuid, user_uuid)
        if room_uuid is None:
            raise ValueError('room_uuid must have a value')
        if message_uuid is None:
            raise ValueError('message_uuid must have a value')
        self.room_uuid = str(room_uuid)
        self.message_uuid = str(message_uuid)


class UserRoomMessageReactionDeletedEvent(UserEvent):
    """Event fired when a user removes a reaction from a message."""
    
    service = 'chatd'
    name = 'chatd_user_room_message_reaction_deleted'
    routing_key_fmt = 'chatd.users.{user_uuid}.rooms.{room_uuid}.messages.{message_uuid}.reactions.deleted'

    def __init__(
        self,
        reaction_data: dict,
        room_uuid: str,
        message_uuid: str,
        tenant_uuid: str,
        user_uuid: str,
    ):
        super().__init__(reaction_data, tenant_uuid, user_uuid)
        if room_uuid is None:
            raise ValueError('room_uuid must have a value')
        if message_uuid is None:
            raise ValueError('message_uuid must have a value')
        self.room_uuid = str(room_uuid)
        self.message_uuid = str(message_uuid)


class UserRoomMessageReplyCreatedEvent(UserEvent):
    """Event fired when a user creates a reply to a message."""
    
    service = 'chatd'
    name = 'chatd_user_room_message_reply_created'
    routing_key_fmt = 'chatd.users.{user_uuid}.rooms.{room_uuid}.messages.{message_uuid}.replies.created'

    def __init__(
        self,
        reply_data: dict,
        room_uuid: str,
        parent_message_uuid: str,
        child_message_uuid: str,
        tenant_uuid: str,
        user_uuid: str,
    ):
        super().__init__(reply_data, tenant_uuid, user_uuid)
        if room_uuid is None:
            raise ValueError('room_uuid must have a value')
        if parent_message_uuid is None:
            raise ValueError('parent_message_uuid must have a value')
        if child_message_uuid is None:
            raise ValueError('child_message_uuid must have a value')
        self.room_uuid = str(room_uuid)
        self.message_uuid = str(parent_message_uuid)  # For routing key compatibility
        self.parent_message_uuid = str(parent_message_uuid)
        self.child_message_uuid = str(child_message_uuid)
