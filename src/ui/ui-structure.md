
The application is split into independent TCP client and server programs:

```text
client.py
└── src/client/
    ├── cli.py              # Interactive UI; sends DTOs through TCP sockets
    └── tcp_client.py       # Blocking socket client

server.py
└── src/server/
    ├── tcp_server.py       # Blocking listener; serves one client at a time
    ├── router.py           # Request validation and operation dispatch
    ├── services.py         # Business logic, validation, and DTO conversion
    └── entities.py         # Server-only SQLAlchemy model allowlist

src/
├── shared/
│   └── protocol.py         # Newline-delimited JSON serialization
├── repositories/           # Server-side persistence layer
├── models/                 # Server-side SQLAlchemy models
└── domain/                 # Database configuration and unit of work
```

The client imports only the client UI, the TCP transport, and shared protocol.
See `docs/protocol.md` for the wire contract.
