# E-sports Tournament Back Office

This project manages players, teams, tournaments, matches, catalogs, and their
association records. The application is split into two programs:

* `server.py` handles requests, business validation, repositories, and
  SQLAlchemy persistence.
* `client.py` is an interactive command-line client. It only sends JSON
  protocol messages over blocking TCP sockets; it has no model or repository
  imports.

## Run

Install dependencies with `pip install -r requirements.txt`. Configure
`DB_URL_DEVELOPMENT` (or the matching URL for the configured `ENVIRONMENT`)
for the database. Start the server first:

```powershell
python server.py
```

Start a client in another terminal:

```powershell
python client.py
```

The default listener is `127.0.0.1:5000`. Set `SERVER_HOST` and `SERVER_PORT`
on both programs to change the connection address. The client supports
list/read/create/update/delete for every entity, including association
entities with composite keys, plus nickname search for players. Enter field
values and identifiers as JSON when prompted. See [docs/protocol.md](docs/protocol.md)
for the complete wire format and validation rules.

Run the unit tests with:

```powershell
pytest
```