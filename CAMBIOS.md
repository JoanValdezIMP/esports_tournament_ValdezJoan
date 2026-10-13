# Guía de cambios: arquitectura cliente/servidor

Este documento explica la refactorización del backoffice de torneos de
esports: qué cambió, por qué se hizo así, cómo se procesa una petición y cómo
ejecutar y probar la aplicación.

## 1. Antes y después

Antes, `main.py` iniciaba una única aplicación de consola. Los menús y vistas
accedían directamente al `Unit of Work`, a los repositorios y a los modelos
SQLAlchemy. La interfaz, las operaciones del negocio y la persistencia estaban
en el mismo proceso.

Ahora existen dos programas independientes:

* **Cliente** (`client.py`): presenta una interfaz de texto sencilla y se
  comunica con el servidor mediante sockets TCP bloqueantes. Solo conoce
  nombres de entidades, operaciones y objetos JSON.
* **Servidor** (`server.py`): recibe las peticiones, valida sus datos, ejecuta
  las operaciones contra la base de datos y devuelve resultados JSON. Es el
  único programa que importa modelos y repositorios.

La base de datos y los modelos existentes se conservan en el lado servidor.
El cliente no comparte ni recibe instancias ORM; recibe diccionarios de
campos escalares (DTOs).

## 2. Organización del código

```text
client.py                         Punto de entrada del cliente
server.py                         Punto de entrada del servidor
main.py                           Alias compatible para iniciar el cliente
src/
├── client/
│   ├── cli.py                    Interfaz interactiva y construcción de peticiones
│   └── tcp_client.py             Conexión y envío/recepción TCP
├── server/
│   ├── entities.py               Lista de entidades permitidas, solo en servidor
│   ├── router.py                 Validación de forma y despacho de peticiones
│   ├── services.py               CRUD, conversiones, validaciones y DTOs
│   └── tcp_server.py             Servidor TCP bloqueante
├── shared/
│   └── protocol.py               Serialización JSON y framing por línea
├── domain/                       Configuración de base de datos y Unit of Work
├── models/                       Modelos SQLAlchemy
└── repositories/                 Repositorios de persistencia
docs/
└── protocol.md                   Especificación detallada del protocolo
tests/
├── test_protocol.py
├── test_router.py
├── test_services.py
└── test_tcp_server.py
```

Los menús/vistas anteriores de `src/ui/views/` y su contexto acoplado a la base
de datos se retiraron. La nueva interfaz es deliberadamente más genérica:
ofrece operaciones CRUD sobre cualquier entidad permitida en vez de mantener
un menú especializado por cada pantalla del backoffice anterior.

## 3. Responsabilidad de cada capa

### Cliente

`src/client/cli.py` pregunta al usuario qué entidad y operación desea ejecutar.
Cuando necesita valores o identificadores, los pide como JSON. Después
construye una petición y la pasa a `TcpClient`.

`src/client/tcp_client.py` abre una conexión TCP, la mantiene durante la
sesión interactiva y utiliza el protocolo compartido para enviar una petición
y esperar su respuesta. No importa SQLAlchemy, modelos ni repositorios. Si no
se puede conectar, informa el error en la consola.

### Protocolo compartido

`src/shared/protocol.py` convierte diccionarios Python a JSON UTF-8 y viceversa.
Cada mensaje termina en un salto de línea (`\n`), por lo que el receptor puede
identificar el final de una petición aunque TCP entregue los datos en varios
fragmentos. El tamaño máximo del contenido es 65.536 bytes.

### Servidor TCP y router

`src/server/tcp_server.py` usa `socket.socket`, `accept()` y operaciones de
lectura/escritura bloqueantes. Atiende **un cliente a la vez**. Para cada
conexión, acepta varias peticiones hasta que el cliente se desconecta o el
protocolo se invalida.

`src/server/router.py` comprueba el tipo de petición, el nombre de la
operación y que las claves del JSON sean exactamente las permitidas para esa
operación. Luego delega en `CrudService`; no realiza consultas SQL por sí
mismo.

### Servicio y persistencia

`src/server/services.py` valida entidad, identificador, campos y tipos.
Después abre un `Unit of Work`, usa el repositorio apropiado y convierte el
resultado en un DTO con columnas escalares.

`src/server/entities.py` define el allowlist servidor-entidad-modelo. Un
cliente no puede enviar un nombre arbitrario de clase ni elegir una tabla que
no esté en esa lista.

Los repositorios existentes y el `Unit of Work` siguen siendo la capa de
persistencia. Se hizo perezosa la carga de las exportaciones de
`src/repositories/__init__.py`: así importar una utilidad de repositorios no
importa automáticamente todos los modelos ni exige configurar la base de
datos. Esto permite probar el router/protocolo de forma aislada y reduce
dependencias accidentales.

## 4. Flujo completo de una petición

1. El cliente solicita, por ejemplo, listar los equipos.
2. El cliente crea `{"operation":"list","entity":"teams"}`.
3. El cliente serializa el objeto a JSON UTF-8 y añade `\n`.
4. El servidor lee una línea completa y la deserializa.
5. El router valida la forma de la petición y llama al método del servicio.
6. El servicio valida la entidad y accede al repositorio mediante el `Unit of
   Work`.
7. Los resultados ORM se convierten en diccionarios de campos escalares.
8. El servidor serializa la respuesta como JSON con salto de línea.
9. El cliente la lee y la muestra en la consola.

En una operación fallida el servidor devuelve un objeto de error con
`"ok": false`; los detalles de fallos inesperados se registran en el servidor
y no se revelan al cliente.

## 5. Protocolo y operaciones

El formato, ejemplos y códigos de error están completos en
[docs/protocol.md](docs/protocol.md). En resumen, cada petición es un objeto
JSON con `operation` y, salvo la búsqueda, `entity`.

Operaciones admitidas:

| Operación | Campos adicionales | Uso |
| --- | --- | --- |
| `list` | ninguno | Devuelve una lista de DTOs. |
| `get` | `id` | Devuelve un DTO o el error `not_found`. |
| `create` | `data` | Crea y devuelve un DTO. |
| `update` | `id`, `data` | Actualiza y devuelve el DTO resultante. |
| `delete` | `id` | Elimina y devuelve `{"deleted":true,"id":...}`. |
| `player.search` | `nickname` | Busca jugadores cuyo nickname contiene el texto indicado. |

Entidades permitidas: `regions`, `video_game_types`, `tournament_modes`,
`tournament_statuses`, `players`, `player_profiles`, `player_teams`, `teams`,
`tournaments`, `team_tournaments` y `matches`.

`player_teams` y `team_tournaments` representan asociaciones. Para crear,
consultar o borrar una asociación se usa su entidad y sus columnas de clave.
Por ejemplo:

```json
{
  "operation": "create",
  "entity": "player_teams",
  "data": {"id_player": 3, "id_team": 8, "points_obtained": 0}
}
```

Para una entidad con clave compuesta, el `id` debe contener todos los campos
de clave primaria:

```json
{
  "operation": "get",
  "entity": "player_teams",
  "id": {"id_player": 3, "id_team": 8}
}
```

## 6. Validación y reglas de datos

El servicio aplica, entre otras, estas reglas:

* Solo acepta entidades y columnas que estén mapeadas y permitidas.
* Rechaza campos desconocidos, peticiones incompletas y claves extra.
* No permite cambiar la clave primaria al actualizar ni enviar una clave
  autoincremental al crear.
* Comprueba tipos de campos: booleanos, enteros, cadenas, fechas, datetimes y
  números decimales. Las fechas y horas viajan en formato ISO 8601.
* Comprueba nulabilidad y longitud máxima de cadenas definida por la columna.
* Las actualizaciones deben incluir al menos un campo.
* Si se modifica una puntuación de partido, vuelve a calcular el ganador:
  mayor puntuación gana y un empate deja `id_team_winner` vacío.
* Acepta IDs sencillos como números y claves compuestas como objetos JSON.

Los DTOs incluyen columnas escalares, no relaciones ORM. Las fechas y horas
se serializan como texto ISO 8601, y los decimales se convierten a números
JSON.

## 7. Errores

Las respuestas de error tienen el formato:

```json
{
  "ok": false,
  "error": {
    "code": "invalid_request",
    "message": "Request fields must be exactly: entity, operation."
  }
}
```

Los códigos estables son:

* `invalid_request`: operación o datos no válidos.
* `not_found`: registro inexistente.
* `protocol_error`: mensaje inválido, demasiado grande o sin delimitador.
* `internal_error`: error inesperado en el servidor. El cliente recibe un
  mensaje genérico; los detalles se registran del lado servidor.

Si el cliente se desconecta, el servidor cierra esa sesión y vuelve a esperar
una conexión.

## 8. Instalación y ejecución

Instala las dependencias existentes:

```powershell
pip install -r requirements.txt
```

Configura `DB_URL_DEVELOPMENT` (o el valor correspondiente al `ENVIRONMENT`
seleccionado) para que el servidor pueda abrir la base de datos. El servidor
crea las tablas mapeadas que falten al arrancar.

En una terminal, inicia el servidor:

```powershell
python server.py
```

En otra terminal, inicia el cliente:

```powershell
python client.py
```

Por defecto se usa `127.0.0.1:5000`. Se puede cambiar mediante las variables
de entorno `SERVER_HOST` y `SERVER_PORT` en cada proceso.

La interfaz pide primero una entidad (o `search` para buscar jugadores), luego
una operación. Para `get`, `update` y `delete` solicita un identificador JSON;
para `create` y `update` solicita los campos como objeto JSON. Ejemplo de
datos de creación para un equipo:

```json
{"name":"Blue Wolves","id_region":1}
```

Ejemplo de actualización:

```json
{"name":"Blue Wolves Academy"}
```

`main.py` se conserva como punto de entrada compatible para iniciar el
cliente; los puntos de entrada recomendados son `client.py` y `server.py`.

## 9. Pruebas

Ejecuta todas las pruebas desde la raíz:

```powershell
pytest -q
```

La suite cubre:

* Codificación/decodificación JSON, UTF-8, framing, tamaño máximo y mensajes
  malformados.
* Despacho del router, forma de las peticiones, operaciones no válidas y
  respuestas de error.
* CRUD del servicio, validación de valores, claves compuestas y cálculo del
  ganador.
* Intercambio de una petición y una respuesta usando un socket conectado en
  una prueba local.

La persistencia de las pruebas del servicio usa SQLite en memoria. Así las
pruebas no modifican la base de datos configurada para la aplicación. La
última ejecución durante esta refactorización terminó con **23 pruebas
correctas**.

## 10. Commit de referencia

La versión entregada de la refactorización está en el commit
`c544bf4447fa814e737eec373a263a66f6e3bad1`, señalado por la etiqueta
`v2.0.0`. Este documento explica esa implementación; al añadirse ahora, será
un commit posterior al commit originalmente etiquetado.
