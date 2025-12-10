# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from collections import defaultdict

from .exceptions import (
    ReactionAlreadyExistsException,
    ReactionNotFoundException,
    MessageNotFoundException,
    RoomNotFoundException,
)

logger = logging.getLogger(__name__)


class ReactionService:
    """Service for managing message reactions."""

    def __init__(self, chatd_dao, reaction_dao, notifier):
        """Initialize the reaction service.
        
        Args:
            chatd_dao: The main chatd DAO (for room access)
            reaction_dao: Our reaction-specific DAO
            notifier: ReactionNotifier for WebSocket events
        """
        self._chatd_dao = chatd_dao
        self._reaction_dao = reaction_dao
        self._notifier = notifier

    def get_reactions(self, tenant_uuid, room_uuid, message_uuid, current_user_uuid):
        """Get all reactions for a message, grouped by emoji.
        
        Returns a dict with message_uuid and reactions list.
        Each reaction has emoji, count, user_uuids, reacted_by_me, and details.
        Details contains user_uuid + created_at for each reaction (for tooltip display).
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        
        # Verify message exists in room
        message = self._get_message(room, message_uuid)
        
        # Get raw reactions from database
        reactions = self._reaction_dao.get_by_message(message_uuid)
        
        # Group by emoji, keeping full reaction details
        grouped = defaultdict(list)
        for reaction in reactions:
            grouped[reaction.emoji].append({
                'user_uuid': str(reaction.user_uuid),
                'created_at': reaction.created_at,
            })
        
        # Build summary with details
        result = []
        for emoji, details in grouped.items():
            user_uuids = [d['user_uuid'] for d in details]
            result.append({
                'emoji': emoji,
                'count': len(details),
                'user_uuids': user_uuids,
                'reacted_by_me': str(current_user_uuid) in user_uuids,
                'details': details,
            })
        
        return {
            'message_uuid': str(message_uuid),
            'reactions': result,
        }

    def add_reaction(self, tenant_uuid, room_uuid, message_uuid, user_uuid, emoji):
        """Add a reaction to a message.
        
        Raises ReactionAlreadyExistsException if user already reacted with this emoji.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        self._verify_user_in_room(room, user_uuid)
        
        # Verify message exists in room
        message = self._get_message(room, message_uuid)
        
        # Check if reaction already exists
        existing = self._reaction_dao.get(message_uuid, user_uuid, emoji)
        if existing:
            raise ReactionAlreadyExistsException(message_uuid, user_uuid, emoji)
        
        # Create reaction
        reaction = self._reaction_dao.create(message_uuid, user_uuid, emoji)
        
        # Notify via WebSocket
        self._notifier.reaction_created(room, message, reaction)
        
        return reaction

    def remove_reaction(self, tenant_uuid, room_uuid, message_uuid, user_uuid, emoji):
        """Remove a reaction from a message.
        
        Raises ReactionNotFoundException if reaction doesn't exist.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        self._verify_user_in_room(room, user_uuid)
        
        # Verify message exists in room
        message = self._get_message(room, message_uuid)
        
        # Get reaction
        reaction = self._reaction_dao.get(message_uuid, user_uuid, emoji)
        if not reaction:
            raise ReactionNotFoundException(message_uuid, user_uuid, emoji)
        
        # Delete reaction
        self._reaction_dao.delete(message_uuid, user_uuid, emoji)
        
        # Notify via WebSocket
        self._notifier.reaction_deleted(room, message, user_uuid, emoji)

    def get_room_reactions(self, tenant_uuid, room_uuid, current_user_uuid):
        """Get all reactions for all messages in a room.
        
        Returns a dict mapping message_uuid to grouped reactions.
        This is for batch loading to avoid N+1 queries.
        """
        # Verify room exists and user has access
        room = self._get_room(tenant_uuid, room_uuid)
        
        # Get all message UUIDs in the room
        message_uuids = [msg.uuid for msg in room.messages]
        
        if not message_uuids:
            return {
                'room_uuid': str(room_uuid),
                'reactions': {},
            }
        
        # Get all reactions for these messages in one query
        reactions = self._reaction_dao.get_by_room(room_uuid, message_uuids)
        
        # Group by message, then by emoji
        by_message = defaultdict(lambda: defaultdict(list))
        for reaction in reactions:
            by_message[str(reaction.message_uuid)][reaction.emoji].append({
                'user_uuid': str(reaction.user_uuid),
                'created_at': reaction.created_at,
            })
        
        # Build result structure
        result = {}
        for message_uuid, emoji_groups in by_message.items():
            message_reactions = []
            for emoji, details in emoji_groups.items():
                user_uuids = [d['user_uuid'] for d in details]
                message_reactions.append({
                    'emoji': emoji,
                    'count': len(details),
                    'user_uuids': user_uuids,
                    'reacted_by_me': str(current_user_uuid) in user_uuids,
                    'details': details,
                })
            result[message_uuid] = message_reactions
        
        return {
            'room_uuid': str(room_uuid),
            'reactions': result,
        }

    def _get_room(self, tenant_uuid, room_uuid):
        """Get room by UUID, verifying tenant access."""
        # Use chatd's room DAO
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
