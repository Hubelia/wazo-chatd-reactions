# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.rest_api_helpers import APIException


class ReactionAlreadyExistsException(APIException):
    def __init__(self, message_uuid, user_uuid, emoji):
        msg = f'Reaction already exists: user {user_uuid} already reacted with {emoji} to message {message_uuid}'
        details = {
            'message_uuid': str(message_uuid),
            'user_uuid': str(user_uuid),
            'emoji': emoji,
        }
        super().__init__(
            status_code=409,
            message=msg,
            error_id='reaction-already-exists',
            details=details,
        )


class ReactionNotFoundException(APIException):
    def __init__(self, message_uuid, user_uuid, emoji):
        msg = f'Reaction not found: user {user_uuid} has not reacted with {emoji} to message {message_uuid}'
        details = {
            'message_uuid': str(message_uuid),
            'user_uuid': str(user_uuid),
            'emoji': emoji,
        }
        super().__init__(
            status_code=404,
            message=msg,
            error_id='reaction-not-found',
            details=details,
        )


class MessageNotFoundException(APIException):
    def __init__(self, message_uuid):
        msg = f'Message not found: {message_uuid}'
        details = {'message_uuid': str(message_uuid)}
        super().__init__(
            status_code=404,
            message=msg,
            error_id='message-not-found',
            details=details,
        )


class RoomNotFoundException(APIException):
    def __init__(self, room_uuid):
        msg = f'Room not found: {room_uuid}'
        details = {'room_uuid': str(room_uuid)}
        super().__init__(
            status_code=404,
            message=msg,
            error_id='room-not-found',
            details=details,
        )
