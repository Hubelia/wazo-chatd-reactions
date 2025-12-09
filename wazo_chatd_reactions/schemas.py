# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields
from xivo.mallow_helpers import Schema


class ReactionSchema(Schema):
    """Schema for a single reaction."""
    
    message_uuid = fields.UUID(dump_only=True)
    user_uuid = fields.UUID(dump_only=True)
    emoji = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)


class ReactionCreateSchema(Schema):
    """Schema for creating a reaction."""
    
    emoji = fields.String(required=True)


class ReactionSummarySchema(Schema):
    """Schema for reaction summary (emoji + count + users)."""
    
    emoji = fields.String()
    count = fields.Integer()
    user_uuids = fields.List(fields.UUID())
    reacted_by_me = fields.Boolean()


class MessageReactionsSchema(Schema):
    """Schema for all reactions on a message."""
    
    message_uuid = fields.UUID()
    reactions = fields.Nested(ReactionSummarySchema, many=True)
