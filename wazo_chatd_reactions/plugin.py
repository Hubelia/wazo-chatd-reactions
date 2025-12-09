# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""
wazo-chat-reactions plugin entry point.

This plugin adds message reactions to wazo-chatd.
"""

from .dao import ReactionDAO
from .http import (
    MessageReactionsResource,
    MessageReactionResource,
)
from .notifier import ReactionNotifier
from .services import ReactionService


class Plugin:
    """Chat reactions plugin for wazo-chatd."""
    
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

        # Create reaction-specific DAO using chatd's session
        # The dao object from chatd has a session property we can use
        reaction_dao = ReactionDAO(dao.session)
        
        # Create notifier for WebSocket events
        notifier = ReactionNotifier(bus_publisher)
        
        # Create service with both DAOs (room from chatd, reaction our own)
        service = ReactionService(dao, reaction_dao, notifier)

        # Register REST endpoints
        api.add_resource(
            MessageReactionsResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/reactions',
            resource_class_args=[service],
        )

        api.add_resource(
            MessageReactionResource,
            '/users/me/rooms/<uuid:room_uuid>/messages/<uuid:message_uuid>/reactions/<string:emoji>',
            resource_class_args=[service],
        )
