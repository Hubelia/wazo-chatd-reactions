# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields
from xivo.mallow_helpers import Schema


# =============================================================================
# Reaction Schemas
# =============================================================================

class ReactionSchema(Schema):
    """Schema for a single reaction."""
    
    message_uuid = fields.UUID(dump_only=True)
    user_uuid = fields.UUID(dump_only=True)
    emoji = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)


class ReactionCreateSchema(Schema):
    """Schema for creating a reaction."""
    
    emoji = fields.String(required=True)


class ReactionDetailSchema(Schema):
    """Schema for detailed reaction info (user + timestamp)."""
    
    user_uuid = fields.UUID()
    created_at = fields.DateTime()


class ReactionSummarySchema(Schema):
    """Schema for reaction summary (emoji + count + users + details)."""
    
    emoji = fields.String()
    count = fields.Integer()
    user_uuids = fields.List(fields.UUID())
    reacted_by_me = fields.Boolean()
    # Detailed info for each user (for tooltip display)
    details = fields.Nested(ReactionDetailSchema, many=True)


class MessageReactionsSchema(Schema):
    """Schema for all reactions on a message."""
    
    message_uuid = fields.UUID()
    reactions = fields.Nested(ReactionSummarySchema, many=True)


class RoomReactionsSchema(Schema):
    """Schema for all reactions in a room (batch loading)."""
    
    room_uuid = fields.UUID()
    # Dict mapping message_uuid (string) to list of reaction summaries
    reactions = fields.Dict(
        keys=fields.String(),
        values=fields.Nested(ReactionSummarySchema, many=True)
    )


# =============================================================================
# Reply Schemas
# =============================================================================

class ParentPreviewSchema(Schema):
    """Schema for cached parent message preview."""
    
    content = fields.String()
    author_uuid = fields.UUID(allow_none=True)
    author_alias = fields.String(allow_none=True)
    created_at = fields.DateTime(allow_none=True)


class ReplyInfoSchema(Schema):
    """Schema for reply relationship info."""
    
    child_message_uuid = fields.UUID()
    parent_message_uuid = fields.UUID(allow_none=True)
    room_uuid = fields.UUID()
    parent_preview = fields.Nested(ParentPreviewSchema, allow_none=True)


class ReplyCreateSchema(Schema):
    """Schema for creating a reply relationship."""
    
    parent_message_uuid = fields.UUID(required=True)


class ReplyListItemSchema(Schema):
    """Schema for a reply in a list."""
    
    message_uuid = fields.UUID()
    created_at = fields.DateTime()


class MessageRepliesSchema(Schema):
    """Schema for all replies to a message."""
    
    parent_message_uuid = fields.UUID()
    reply_count = fields.Integer()
    replies = fields.Nested(ReplyListItemSchema, many=True)


class RoomReplyMetadataSchema(Schema):
    """Schema for room-wide reply metadata."""
    
    room_uuid = fields.UUID()
    replies = fields.Dict(keys=fields.String(), values=fields.Nested(ReplyInfoSchema))
