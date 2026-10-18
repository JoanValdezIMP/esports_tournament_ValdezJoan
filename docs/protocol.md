# Protocolo de comunicación cliente-servidor

## Transporte y framing

El cliente y el servidor se comunican mediante sockets TCP bloqueantes. Sobre TCP se envían mensajes JSON codificados en UTF-8, con un mensaje por línea (JSON Lines). Cada solicitud y respuesta termina con un salto de línea (`\n`); el receptor lee hasta ese separador para reconstruir el mensaje completo.

TCP es un flujo de bytes y no conserva los límites de los mensajes. Por ello, el salto de línea forma parte del protocolo y no se debe asumir que una llamada a `recv()` equivale a un mensaje completo.

**Archivos relacionados**

- `src/client/tcp_client.py`: codifica solicitudes JSONL y envía/recibe por TCP.
- `src/server/tcp_server.py`: reconstruye mensajes por línea y escribe respuestas JSONL.
- `tests/test_tcp_client.py`, `tests/test_tcp_server.py`: comprueban framing, intercambio y mensajes inválidos.

## Formato de solicitud

Cada solicitud tendrá un nombre de operación y un objeto `data`:

```json
{"operation":"players.list","data":{}}
```

Las operaciones siguen el patrón `<recurso>.<acción>`. Las que están implementadas actualmente son:

- `players.list`
- `players.search`
- `players.read`
- `players.create`
- `players.update`
- `players.delete`
- `teams.list`
- `teams.read`
- `teams.create`
- `teams.update`
- `teams.delete`
- `teams.assign_player`
- `regions.list`
- `regions.create`
- `tournament_statuses.list`
- `tournament_statuses.create`
- `tournament_modes.list`
- `tournament_modes.create`
- `tournament_modes.update`
- `tournament_modes.delete`
- `video_game_types.list`
- `video_game_types.create`
- `video_game_types.update`
- `video_game_types.delete`
- `player_profiles.list`
- `matches.list`
- `matches.create`
- `matches.update_result`
- `matches.delete`
- `tournaments.list`
- `tournaments.read`
- `tournaments.create`
- `tournaments.update`
- `tournaments.delete`
- `tournaments.register_team`

Las operaciones no incluidas en esta lista responderán `unknown_operation`. `data` contendrá los campos necesarios para la operación; el servidor validará su estructura y valores antes de llamar al servicio correspondiente.

Campos de `data` para las operaciones implementadas:

| Operación | Campos |
| --- | --- |
| `players.list` | Ninguno (`{}`) |
| `players.search` | `nickname` (texto no vacío) |
| `players.read` | `id` (entero positivo) |
| `players.create` | `nickname`, `email` (texto no vacío), `region_id` (entero positivo); opcional `ranking_position` (entero no negativo) |
| `players.update` | `id` (entero positivo), `nickname` (texto no vacío) |
| `players.delete` | `id` (entero positivo) |
| `teams.list` | Ninguno (`{}`) |
| `teams.read` | `id` (entero positivo) |
| `teams.create` | `name` (texto no vacío), `region_id` (entero positivo) |
| `teams.update` | `id` (entero positivo), `name` (texto no vacío) |
| `teams.delete` | `id` (entero positivo) |
| `teams.assign_player` | `team_id`, `player_id` (enteros positivos), `points_obtained` (entero no negativo) |
| `regions.list` | Ninguno (`{}`) |
| `regions.create` | `name`, `country_code` (texto no vacío) |
| `tournament_statuses.list` | Ninguno (`{}`) |
| `tournament_statuses.create` | `name` (texto no vacío); opcional `description` |
| `tournament_modes.list` | Ninguno (`{}`) |
| `tournament_modes.create` | `name` (texto no vacío); opcional `description` |
| `tournament_modes.update` | `id` (entero positivo), `name` (texto no vacío); opcional `description` |
| `tournament_modes.delete` | `id` (entero positivo) |
| `video_game_types.list` | Ninguno (`{}`) |
| `video_game_types.create` | `name` (texto no vacío); opcional `description` |
| `video_game_types.update` | `id` (entero positivo), `name` (texto no vacío); opcional `description` |
| `video_game_types.delete` | `id` (entero positivo) |
| `player_profiles.list` | Ninguno (`{}`) |
| `matches.list` | Ninguno (`{}`) |
| `matches.create` | `tournament_id`, `team_one_id`, `team_two_id` (enteros positivos; equipos distintos), `round_number`, `duration_minutes` (enteros positivos) |
| `matches.update_result` | `id` (entero positivo), `score_team_one`, `score_team_two` (enteros no negativos) |
| `matches.delete` | `id` (entero positivo) |
| `tournaments.list` | Ninguno (`{}`) |
| `tournaments.read` | `id` (entero positivo) |
| `tournaments.create` | `name`, `start_date` (`YYYY-MM-DD`), `end_date` (fecha o `null`), `prize_pool` (número no negativo con hasta dos decimales), `max_teams` y `region_id`, `video_game_type_id`, `tournament_mode_id`, `tournament_status_id` (enteros positivos) |
| `tournaments.update` | `id` (entero positivo), `name`, `start_date`, `end_date`, `prize_pool`, `max_teams` con las validaciones de creación |
| `tournaments.delete` | `id` (entero positivo); no se elimina si tiene partidos o equipos inscritos |
| `tournaments.register_team` | `tournament_id`, `team_id` (enteros positivos); rechaza duplicados o superar `max_teams` |

**Archivos relacionados**

- `src/server/router.py`: valida la estructura y despacha cada nombre de operación.
- `src/services/player_service.py`, `team_service.py`, `catalog_service.py`, `match_service.py`, `tournament_service.py`: implementan operaciones de negocio y construyen DTOs.
- `src/ui/views/player_views.py`, `team_views.py`, `catalog_views.py`, `match_views.py`, `tournament_views.py`: envían las operaciones desde los menús.
- `tests/test_request_router.py`, `tests/test_*_service.py`: cubren el despacho y la lógica de servicio.

## Formato de respuesta

Una respuesta correcta tendrá `ok: true`, el resultado en `data` y `error: null`:

```json
{"ok":true,"data":[{"id":1,"nickname":"PlayerOne","region":"Europe","has_profile":true}],"error":null}
```

Una respuesta fallida tendrá `ok: false`, `data: null` y un error con código estable y mensaje:

```json
{"ok":false,"data":null,"error":{"code":"not_found","message":"Player not found"}}
```

Los códigos previstos incluyen `invalid_request`, `unknown_operation`, `validation_error`, `not_found` e `internal_error`. El servidor no enviará trazas internas ni objetos SQLAlchemy al cliente.

**Archivos relacionados**

- `src/server/router.py`: crea la respuesta estándar de éxito o error.
- `src/server/tcp_server.py`: serializa la respuesta y la termina en `\n`.
- `src/client/tcp_client.py`: valida la forma recibida y expone errores de protocolo o conexión.

## Validación y errores

El servidor comprobará que la solicitud sea un objeto JSON, que incluya una cadena no vacía en `operation` y que `data` sea un objeto. Cada mensaje debe terminar en `\n`; los mensajes incompletos al cerrar la conexión reciben `invalid_request`. El JSON inválido o el texto que no sea UTF-8 recibe `invalid_request`; el servidor responde y continúa leyendo mensajes de esa conexión. Las solicitudes mal formadas recibirán `invalid_request`; una operación no reconocida recibirá `unknown_operation`; y los campos no admitidos por una operación recibirán `validation_error`. Los errores internos se registrarán en el servidor y se responderán con `internal_error`, sin exponer detalles de implementación.

**Archivos relacionados**

- `src/server/router.py`, `src/server/tcp_server.py`: validan solicitudes y responden a errores de protocolo y negocio.
- `src/services/errors.py`: define los errores de validación y de recursos inexistentes.
- `tests/test_request_router.py`, `tests/test_tcp_server.py`, `tests/test_tcp_client.py`: verifican errores y sus respuestas.

## Persistencia del servidor

SQLAlchemy y sus modelos y repositorios se ejecutan exclusivamente en el servidor. El cliente usa `TcpClient` y solo intercambia estructuras serializables (JSON/diccionarios/DTOs); su contexto no crea ni conserva unidades de trabajo ni inicializa una base local.

La base de datos elegida es SQLite en memoria (`sqlite://`). El servidor utiliza un único `Engine` compartido para crear el esquema y para todas las sesiones de las unidades de trabajo. `StaticPool` mantiene una única conexión compartida, necesaria para que las sesiones vean la misma base de datos en memoria. `check_same_thread=False` permite reutilizar esa conexión si el código del servidor llega a atenderla desde otro hilo.

Las tablas deben crearse al iniciar el servidor, después de importar los modelos. Los datos existen solo durante la ejecución del servidor y se pierden al cerrarlo; no se leen ni escriben las variables `DB_URL_DEVELOPMENT`, `DB_URL_TEST` o `DB_URL_PRODUCTION`.

**Archivos relacionados**

- `src/domain/db.py`, `src/repositories/unit_of_work.py`: configuran el engine SQLite en memoria y las unidades de trabajo del servidor.
- `server_main.py`: importa los modelos, crea las tablas e inyecta los servicios.
- `main.py`, `src/ui/context.py`: construyen la CLI y el cliente TCP sin inicializar ni usar la base de datos.
- `tests/test_in_memory_database.py`: comprueba la persistencia compartida durante la vida del servidor.

## Implementación actual

La arquitectura queda dividida en dos programas. `server_main.py` importa los modelos y crea las tablas; configura los servicios de jugadores, equipos, catálogos, partidos y torneos; y arranca el servidor TCP. `main.py` construye la CLI y `TcpClient`, sin importar SQLAlchemy, modelos, repositorios ni configuración de base de datos. `UIContext` conserva solo los elementos de interfaz y el cliente TCP.

`RequestRouter` valida las solicitudes y delega cada operación a su servicio. Los servicios acceden a los repositorios y devuelven diccionarios/DTOs serializables, nunca modelos ORM. Para jugadores, la creación fija las fechas de alta y nacimiento a la hora actual, marca el registro activo y crea perfil si se proporciona `ranking_position`. Los equipos validan la región y las asignaciones de jugadores; no se eliminan equipos con asociaciones. Los catálogos proporcionan las operaciones enumeradas arriba; no se eliminan modos ni tipos de videojuego utilizados por torneos. Los partidos calculan el ganador al guardar el resultado y consideran empate cuando ambos marcadores coinciden. Los torneos validan referencias a catálogos, fechas, premio y máximo de equipos; se impiden las inscripciones duplicadas o por encima del límite y no se elimina un torneo con partidos o equipos inscritos.

`TcpClient` utiliza un socket bloqueante por solicitud y un timeout predeterminado de cinco segundos. Los fallos de transporte producen `ServerConnectionError`; las respuestas con formato inválido producen `ProtocolError`. Los errores de negocio del servidor se devuelven con la estructura estándar y las vistas muestran el mensaje al usuario.

El servidor solo atiende un cliente a la vez. Se inicia desde la raíz del proyecto con `python server_main.py`; a continuación, en otra terminal, se inicia la interfaz con `python main.py`. `SERVER_HOST` y `SERVER_PORT` permiten configurar host y puerto; los valores predeterminados son `127.0.0.1` y `5000`.

La cobertura automática incluye pruebas unitarias de servicios, validación y despacho del router, framing TCP, cliente y vistas. `tests/test_server_process_e2e.py` levanta `server_main.py` como subproceso independiente, espera a que escuche en un puerto local libre y utiliza `TcpClient` para recorrer operaciones reales de catálogos, equipos, torneos y partidos, además de comprobar un error de negocio. También ejecuta `main.py` como proceso independiente con entradas de menú automatizadas para crear y listar una región a través de TCP, comprobando la navegación y el mensaje de éxito de la CLI.

Ejecuta las comprobaciones de integración con:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_server_process_e2e.py
```

Para una prueba visual manual, inicia primero `python server_main.py` y luego, en otra terminal, `python main.py`. En la CLI, elige Catálogos, crea una región, vuelve al menú de catálogos, lista las regiones y regresa al menú principal. Comprueba el mensaje de éxito y que aparezca la región recién creada. El servidor es secuencial y atiende un cliente a la vez.

**Archivos relacionados**

- Arranque: `server_main.py` (servidor), `main.py` (cliente) y `src/ui/cli.py` (menú principal).
- Red: `src/client/tcp_client.py`, `src/server/tcp_server.py`, `src/server/router.py`.
- Negocio: `src/services/` contiene servicios y DTOs; `src/repositories/` contiene acceso a datos del servidor.
- Interfaz: `src/ui/context.py`, `src/ui/views/` contiene las vistas de cada recurso.
- Pruebas: `tests/test_request_router.py`, `tests/test_tcp_client.py`, `tests/test_tcp_server.py`, pruebas de servicios/vistas y `tests/test_server_process_e2e.py`.

## Calidad del código y nombres

Se aplicó el formato PEP 8 al código Python y se renombraron a inglés los identificadores internos de las vistas y sus pruebas relacionadas. Los textos que se muestran al usuario se mantienen en el idioma original de la interfaz. No se añadieron dependencias de formato o lint al manifiesto de la aplicación.

La validación realizada incluye:

```powershell
.\.venv\Scripts\python.exe -m pycodestyle src server_main.py main.py tests
.\.venv\Scripts\python.exe -m compileall -q src tests main.py server_main.py
.\.venv\Scripts\python.exe -m pytest
```

**Archivos relacionados**

- `src/ui/views/player_views.py`, `team_views.py`, `catalog_views.py`, `match_views.py` y `tournament_views.py`: formato y nombres internos en inglés.
- `tests/`: formato y actualización de referencias a las vistas.
- `main.py`, `server_main.py` y el resto de módulos Python: formato PEP 8.
- `docs/protocol.md`: documenta el paso de calidad y sus comprobaciones.
