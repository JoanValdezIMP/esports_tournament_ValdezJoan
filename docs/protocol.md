# TCP JSON protocol

The application uses blocking TCP sockets and UTF-8 JSON messages delimited by
a newline (`\n`). Each request and response is one JSON object on a separate
line. A connection may carry multiple requests; the server processes one
connected client at a time. Messages are limited to 65,536 bytes, excluding
the delimiter.

## Request and response format

Requests use the following shape:

```json
{"operation":"list","entity":"teams"}
```

Successful responses contain `ok: true` and a JSON-compatible DTO in `data`:

```json
{"ok":true,"data":[{"id_team":8,"name":"Blue Wolves","id_region":1}]}
```

Errors contain `ok: false` and a stable error `code` with a human-readable
`message`:

```json
{"ok":false,"error":{"code":"not_found","message":"teams record was not found."}}
```

## Operations

All CRUD operations require an allowlisted `entity`. Available entities are
`regions`, `video_game_types`, `tournament_modes`, `tournament_statuses`,
`players`, `player_profiles`, `player_teams`, `teams`, `tournaments`,
`team_tournaments`, and `matches`.

| Operation | Request | Successful `data` |
| --- | --- | --- |
| List | `{"operation":"list","entity":"teams"}` | Array of entity DTOs |
| Read | `{"operation":"get","entity":"teams","id":8}` | One entity DTO |
| Create | `{"operation":"create","entity":"teams","data":{"name":"Blue Wolves","id_region":1}}` | Created entity DTO |
| Update | `{"operation":"update","entity":"teams","id":8,"data":{"name":"Blue Wolves"}}` | Updated entity DTO |
| Delete | `{"operation":"delete","entity":"teams","id":8}` | `{"deleted":true,"id":8}` |
| Search players | `{"operation":"player.search","nickname":"blue"}` | Matching player DTO array |

DTOs contain mapped scalar database fields only; relationship objects and ORM
instances are never sent. Dates and datetimes are ISO 8601 strings, and
decimal values are JSON numbers. Client-supplied date and datetime values must
also be ISO 8601 strings. The server generates single-column auto-increment
primary keys. For composite keys, `id` must be an object containing every
primary-key field, for example:

```json
{"operation":"get","entity":"player_teams","id":{"id_player":3,"id_team":8}}
```

When either match score is updated, the server recalculates the winner from
the resulting scores; tied scores have no winner.

Create and update `data` must be non-empty objects containing mapped scalar
fields only. Updates cannot change primary keys. Unknown entities, fields,
invalid values, malformed requests, and missing records produce an error
response rather than a successful empty result.

## Error codes

* `invalid_request`: unsupported operation, invalid request shape, entity, or
  field value.
* `not_found`: a requested record does not exist.
* `protocol_error`: invalid UTF-8/JSON framing, an oversized message, or a
  missing newline delimiter.
* `internal_error`: unexpected persistence or server-side failure. Details are
  logged on the server and not exposed to the client.
