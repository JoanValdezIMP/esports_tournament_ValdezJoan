src/
├── domain/
├── models/
├── repositories/
└── ui/
    ├── __init__.py
    ├── cli.py              # El orquestador: contiene el bucle principal y el Menú General (Command Line Interface)
    ├── context.py          # Gestiona de forma limpia el Unit of Work y la consola de Rich
    ├── components.py       # Diseños reutilizables de Rich (cabeceras, tablas estándar, spinners)
    └── views/              # Los submenús específicos divididos por lógica
        ├── __init__.py
        ├── catalog_views.py   # CRUDs simples: Regiones, Modos, Estados, Tipos de Juego
        ├── player_views.py    # CRUD de Jgadorues + Perfil (Relación 1:1)
        ├── team_views.py      # CRUD de Equipos + Fichajes (Relación N:M con atributos)
        ├── tournament_views.py# CRUD de Torneos (Relación 1:N)
        └── match_views.py     # CRUD de Partidos y gestión de resultados
