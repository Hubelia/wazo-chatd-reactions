# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
wazo-chatd-reactions plugin entry point.

This plugin adds message reactions and threaded replies to wazo-chatd.
"""

from .dao import ReactionDAO
from .reply_dao import ReplyDAO
from .http import (
    MessageReactionsResource,
    MessageReactionResource,
    MessageReplyInfoResource,
    MessageRepliesResource,
    RoomReplyMetadataResource,
)
from .notifier import ReactionNotifier
from .services import ReactionService
from .reply_services import ReplyService


class Plugin:
    """Chat reactions and replies plugin for wazo-chatd."""
    
    def load(self, dependencies):
        """Load the plugin.
        
        Args:
            dependencies: Dict containing:
                - api: Flask-RESTful API instance
                - dao: wazo-chatd DAO (contains room and session access)
                - bus_publisher: Bus publisher for events
                - config: Configuration dict
        """
        api = dependencies['api']
        dao = dependencies['dao']
        bus_publisher = dependencies['bus_publisher']

        # Create notifier for WebSocket events (shared by both services)
        notifier = ReactionNotifier(bus_publisher)

        # =================================================================
        # Reactions
        # =================================================================
        reaction_dao = ReactionDAO()
        reaction_service = ReactionService(dao, reaction_dao, notifier)

        api.add_resource(
            MessageReactionsResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/reactions',
            resource_class_args=[reaction_service],
        )

        api.add_resource(
            MessageReactionResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/reactions/<string:emoji>',
            resource_class_args=[reaction_service],
        )

        # =================================================================
        # Replies
        # =================================================================
        reply_dao = ReplyDAO()
        reply_service = ReplyService(dao, reply_dao, notifier)

        # Get reply info for a message / Create reply relationship
        api.add_resource(
            MessageReplyInfoResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/reply',
            resource_class_args=[reply_service],
        )

        # Get all replies to a message
        api.add_resource(
            MessageRepliesResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/replies',
            resource_class_args=[reply_service],
        )

        # Get all reply metadata for a room (batch loading)
        api.add_resource(
            RoomReplyMetadataResource,
            '/users/me/rooms/<uuid:room_uuid>/replies',
            resource_class_args=[reply_service],
        )
