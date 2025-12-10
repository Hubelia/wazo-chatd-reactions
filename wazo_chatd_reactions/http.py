# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from xivo.auth_verifier import required_acl
from xivo.tenant_flask_helpers import token

from wazo_chatd.http import AuthResource

from .schemas import (
    ReactionCreateSchema,
    MessageReactionsSchema,
    ReactionSchema,
    RoomReactionsSchema,
    ReplyCreateSchema,
    ReplyInfoSchema,
    MessageRepliesSchema,
    RoomReplyMetadataSchema,
)


# =============================================================================
# Reaction Resources
# =============================================================================

class MessageReactionsResource(AuthResource):
    """Resource for listing and adding reactions to a message."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.reactions.read')
    def get(self, room_uuid, message_uuid):
        """Get all reactions for a message.
        
        Returns reactions grouped by emoji with count and user list.
        """
        result = self._service.get_reactions(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            message_uuid=message_uuid,
            current_user_uuid=token.user_uuid,
        )
        return MessageReactionsSchema().dump(result), 200

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.reactions.create')
    def post(self, room_uuid, message_uuid):
        """Add a reaction to a message.
        
        Request body: {"emoji": "..."}
        """
        reaction_args = ReactionCreateSchema().load(request.get_json())
        
        reaction = self._service.add_reaction(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            message_uuid=message_uuid,
            user_uuid=token.user_uuid,
            emoji=reaction_args['emoji'],
        )
        return ReactionSchema().dump(reaction), 201


class MessageReactionResource(AuthResource):
    """Resource for deleting a specific reaction."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.reactions.delete')
    def delete(self, room_uuid, message_uuid, emoji):
        """Remove a reaction from a message.
        
        Only the user who created the reaction can remove it.
        """
        self._service.remove_reaction(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            message_uuid=message_uuid,
            user_uuid=token.user_uuid,
            emoji=emoji,
        )
        return '', 204


class RoomReactionsResource(AuthResource):
    """Resource for getting all reactions in a room (batch loading)."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.reactions.read')
    def get(self, room_uuid):
        """Get all reactions for all messages in a room.
        
        Returns a dict mapping message UUIDs to their reactions.
        Useful for batch loading reaction data for a room.
        """
        result = self._service.get_room_reactions(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            current_user_uuid=token.user_uuid,
        )
        return RoomReactionsSchema().dump(result), 200


# =============================================================================
# Reply Resources
# =============================================================================

class MessageReplyInfoResource(AuthResource):
    """Resource for getting reply info for a specific message."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.reply.read')
    def get(self, room_uuid, message_uuid):
        """Get reply info for a message (if it's a reply).
        
        Returns the parent message info and preview.
        """
        result = self._service.get_reply_info(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            message_uuid=message_uuid,
        )
        if result is None:
            return {'message': 'This message is not a reply'}, 404
        return ReplyInfoSchema().dump(result), 200

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.reply.create')
    def post(self, room_uuid, message_uuid):
        """Create a reply relationship for an existing message.
        
        This endpoint is called after creating a message to mark it as a reply.
        Request body: {"parent_message_uuid": "..."}
        
        Note: message_uuid in URL is the child (reply) message.
        """
        reply_args = ReplyCreateSchema().load(request.get_json())
        
        result = self._service.create_reply_relationship(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            child_message_uuid=message_uuid,
            parent_message_uuid=reply_args['parent_message_uuid'],
            user_uuid=token.user_uuid,
        )
        return ReplyInfoSchema().dump(result), 201


class MessageRepliesResource(AuthResource):
    """Resource for getting all replies to a message."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.messages.{message_uuid}.replies.read')
    def get(self, room_uuid, message_uuid):
        """Get all replies to a message.
        
        Returns a list of message UUIDs that are replies to this message.
        """
        result = self._service.get_replies_to_message(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
            message_uuid=message_uuid,
        )
        return MessageRepliesSchema().dump(result), 200


class RoomReplyMetadataResource(AuthResource):
    """Resource for getting all reply metadata in a room."""

    def __init__(self, service):
        self._service = service

    @required_acl('chatd.users.me.rooms.{room_uuid}.replies.read')
    def get(self, room_uuid):
        """Get all reply metadata for a room.
        
        Returns a dict mapping message UUIDs to their reply info.
        Useful for batch loading reply data for a room.
        """
        result = self._service.get_room_reply_metadata(
            tenant_uuid=token.tenant_uuid,
            room_uuid=room_uuid,
        )
        return RoomReplyMetadataSchema().dump(result), 200
