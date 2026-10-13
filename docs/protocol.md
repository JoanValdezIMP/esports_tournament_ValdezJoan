# Protocol JSON sobre TCP

L'aplicació utilitza sockets TCP bloquejants i missatges JSON codificats en
UTF-8, delimitats per un salt de línia (`\n`). Cada petició i resposta és un
objecte JSON en una línia independent. Una connexió pot transportar diverses
peticions; el servidor atén un sol client cada vegada. La mida màxima del
contingut del missatge és de 65.536 bytes, sense comptar el delimitador.

## Format de petició i resposta

Les peticions tenen aquesta estructura:

```json
{"operation":"list","entity":"teams"}
```

Les respostes correctes contenen `ok: true` i un DTO compatible amb JSON al
camp `data`:

```json
{"ok":true,"data":[{"id_team":8,"name":"Blue Wolves","id_region":1}]}
```

Les respostes d'error contenen `ok: false` i un codi estable `code`, juntament
amb un missatge llegible al camp `message`:

```json
{"ok":false,"error":{"code":"not_found","message":"teams record was not found."}}
```

## Operacions

Totes les operacions CRUD requereixen una entitat inclosa a la llista
autoritzada. Les entitats disponibles són `regions`, `video_game_types`,
`tournament_modes`, `tournament_statuses`, `players`, `player_profiles`,
`player_teams`, `teams`, `tournaments`, `team_tournaments` i `matches`.

| Operació | Petició | `data` de la resposta correcta |
| --- | --- | --- |
| Llistar | `{"operation":"list","entity":"teams"}` | Llista de DTOs de l'entitat |
| Consultar | `{"operation":"get","entity":"teams","id":8}` | Un DTO de l'entitat |
| Crear | `{"operation":"create","entity":"teams","data":{"name":"Blue Wolves","id_region":1}}` | DTO de l'entitat creada |
| Actualitzar | `{"operation":"update","entity":"teams","id":8,"data":{"name":"Blue Wolves"}}` | DTO de l'entitat actualitzada |
| Eliminar | `{"operation":"delete","entity":"teams","id":8}` | `{"deleted":true,"id":8}` |
| Cercar jugadors | `{"operation":"player.search","nickname":"blue"}` | Llista de DTOs dels jugadors coincidents |

Els DTOs només contenen camps escalars mapejats a la base de dades; mai no
s'envien objectes de relació ni instàncies ORM. Les dates i les marques de
temps s'expressen com a cadenes ISO 8601, i els valors decimals s'envien com a
nombres JSON. Les dates i marques de temps proporcionades pel client també han
d'estar en format ISO 8601. El servidor genera les claus primàries d'una sola
columna autoincrementals. Per a les claus compostes, `id` ha de ser un objecte
que contingui tots els camps de la clau primària. Per exemple:

```json
{"operation":"get","entity":"player_teams","id":{"id_player":3,"id_team":8}}
```

Quan s'actualitza qualsevol de les puntuacions d'un partit, el servidor torna
a calcular el guanyador a partir de les puntuacions resultants. En cas
d'empat, el partit queda sense guanyador.

Les dades `data` d'una creació o actualització han de ser objectes no buits i
només poden contenir camps escalars mapejats. Les actualitzacions no poden
modificar les claus primàries. Les entitats o els camps desconeguts, els
valors no vàlids, les peticions mal formades i els registres inexistents
generen una resposta d'error, no pas una resposta correcta buida.

## Codis d'error

* `invalid_request`: operació, estructura de petició, entitat o valor de camp
  no vàlid.
* `not_found`: el registre sol·licitat no existeix.
* `protocol_error`: codificació UTF-8 o JSON incorrecta, missatge massa gran
  o manca del delimitador de salt de línia.
* `internal_error`: error inesperat del servidor o de persistència. El detall
  s'anota al registre del servidor i no s'exposa al client.
