# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from xivo.auth_verifier import required_acl
from xivo.tenant_flask_helpers import token

from wazo_chatd.http import AuthResource

from .schemas import ReactionCreateSchema, MessageReactionsSchema, ReactionSchema


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
