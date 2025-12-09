# wazo-chatd-reactions

Add emoji reactions to chat messages in Wazo.

## Features

- Add emoji reactions to messages
- Remove reactions
- Real-time WebSocket notifications when reactions are added/removed
- Reactions grouped by emoji with user counts

## Installation

### Via wazo-plugind CLI

```bash
wazo-plugind-cli -c "install git https://github.com/Hubelia/wazo-chatd-reactions"
```

### Via API

```bash
curl -X POST "https://{wazo-host}/api/plugind/0.2/plugins" \
  -H "X-Auth-Token: {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "git",
    "options": {
      "url": "https://github.com/Hubelia/wazo-chatd-reactions"
    }
  }'
```

## API Endpoints

All endpoints are under `/api/chatd/1.0`:

### Get Reactions

```http
GET /users/me/rooms/{room_uuid}/messages/{message_uuid}/reactions
```

Response:
```json
{
  "message_uuid": "a0e7dc92-92a3-485b-b8dd-09a909a1f5a0",
  "reactions": [
    {
      "emoji": "👍",
      "count": 3,
      "user_uuids": ["uuid1", "uuid2", "uuid3"],
      "reacted_by_me": true
    },
    {
      "emoji": "❤️",
      "count": 1,
      "user_uuids": ["uuid4"],
      "reacted_by_me": false
    }
  ]
}
```

### Add Reaction

```http
POST /users/me/rooms/{room_uuid}/messages/{message_uuid}/reactions
Content-Type: application/json

{
  "emoji": "👍"
}
```

Response (201):
```json
{
  "message_uuid": "a0e7dc92-92a3-485b-b8dd-09a909a1f5a0",
  "user_uuid": "8040ec9d-1a61-4ca3-abe5-ad7c2f192e03",
  "emoji": "👍",
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Remove Reaction

```http
DELETE /users/me/rooms/{room_uuid}/messages/{message_uuid}/reactions/{emoji}
```

Response: 204 No Content

## WebSocket Events

Subscribe to these events via wazo-websocketd:

### Reaction Created

Event name: `chatd_user_room_message_reaction_created`

```json
{
  "room_uuid": "697a35a6-534c-461d-9466-6f77d0181e80",
  "message_uuid": "a0e7dc92-92a3-485b-b8dd-09a909a1f5a0",
  "user_uuid": "8040ec9d-1a61-4ca3-abe5-ad7c2f192e03",
  "emoji": "👍",
  "created_at": "2024-01-15T10:30:00+00:00"
}
```

### Reaction Deleted

Event name: `chatd_user_room_message_reaction_deleted`

```json
{
  "room_uuid": "697a35a6-534c-461d-9466-6f77d0181e80",
  "message_uuid": "a0e7dc92-92a3-485b-b8dd-09a909a1f5a0",
  "user_uuid": "8040ec9d-1a61-4ca3-abe5-ad7c2f192e03",
  "emoji": "👍"
}
```

## Database Schema

The plugin creates the following table on install:

```sql
CREATE TABLE chatd_room_message_reaction (
    message_uuid UUID NOT NULL REFERENCES chatd_room_message(uuid) ON DELETE CASCADE,
    user_uuid UUID NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (message_uuid, user_uuid, emoji)
);
```

The table is dropped on full uninstallation.

## Uninstallation

```bash
wazo-plugind-cli -c "uninstall community/wazo-chatd-reactions"
```

This will:
1. Restart wazo-chatd without the plugin
2. Drop the `chatd_room_message_reaction` table (on full removal)

## Requirements

- Wazo Platform >= 23.01 (for group chat support)

## License

GPL-3.0-or-later
