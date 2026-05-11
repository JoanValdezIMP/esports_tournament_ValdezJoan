from sqlalchemy import select, desc, and_
from typing import Sequence, Optional
from datetime import date
from .abstract_repository import SqlAlchemyRepository
from models import PlayerTeam

class SqlAlchemyPlayerTeamRepository(SqlAlchemyRepository[PlayerTeam, tuple[int, int]]):
    
    def list(self):
        # Opción 1: Estilo clásico
        return self.session.query(PlayerTeam).all()


    def add_player_to_team(self, team_id: int, player_id: int, join_date: date) -> None:
        """
        Operación de dominio: Añade un jugador al equipo directamente
        creando el vínculo, sin necesidad de cargar y actualizar todo el objeto Team.
        """
        from models import PlayerTeam # Evita importaciones circulares arriba
        new_link = PlayerTeam(id_player=player_id, id_team=team_id, join_date=join_date)
        self.session.add(new_link)


    def get_current_team(self, player_id: int) -> Optional[PlayerTeam]:
        """
        Busca el último equipo al que se unió el jugador.
        Ordenamos por fecha de entrada de forma descendente y cogemos el primero.
        """
        statement = (
            select(PlayerTeam)
            .where(PlayerTeam.id_player == player_id)
            .order_by(desc(PlayerTeam.join_date))
            # limit(1) no es estrictamente necesario si usamos scalar(), 
            # pero a nivel de base de datos hace la consulta más eficiente.
            .limit(1) 
        )
        return self.session.scalar(statement)

    def list_players_in_team(self, team_id: int) -> Sequence[PlayerTeam]:
        """
        Saca el roster actual (e histórico) de un equipo.
        Devolvemos PlayerTeam para que en tu frontend puedas mostrar 
        no solo el jugador, sino también "Miembro desde: {join_date}".
        """
        statement = (
            select(PlayerTeam)
            .where(PlayerTeam.id_team == team_id)
            # Podríamos ordenarlos por los más veteranos primero
            .order_by(PlayerTeam.join_date.asc())
        )
        return self.session.scalars(statement).all()

    def is_player_in_team(self, player_id: int, team_id: int) -> bool:
        """
        Validador booleano rápido. Ideal para las reglas de negocio 
        antes de inscribir a alguien en un partido.
        """
        statement = (
            select(PlayerTeam)
            .where(
                and_(
                    PlayerTeam.id_player == player_id,
                    PlayerTeam.id_team == team_id
                )
            )
            .limit(1)
        )
        # Si scalar() devuelve algo, es que existe (True). Si devuelve None, es False.
        resultado = self.session.scalar(statement)
        return resultado is not None