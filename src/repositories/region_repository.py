from sqlalchemy import select, func
from typing import Sequence, Optional
from .abstract_repository import SqlAlchemyRepository
from models import Region
from models import Tournament
from models import Player

class SqlAlchemyRegionRepository(SqlAlchemyRepository[Region, int]):
    
    def get_by_country_code(self, code: str) -> Optional[Region]:
        """
        Busca rápidamente una región por su código (ej: 'ES', 'MX').
        """
        # Puedes añadir .ilike() si quieres que la búsqueda sea insensible 
        # a mayúsculas/minúsculas, ej: Region.country_code.ilike(code)
        statement = select(Region).where(Region.country_code == code)
        return self.session.scalar(statement)

    def list_with_tournaments(self) -> Sequence[Region]:
        """
        Devuelve solo las regiones que tienen al menos un torneo.
        Ideal para poblar selectores (dropdowns) y no mostrar regiones vacías.
        """
        statement = (
            select(Region)
            # Al hacer JOIN con Tournament, SQLAlchemy solo se queda con las regiones
            # que tienen coincidencias en esa tabla (Inner Join por defecto).
            .join(Tournament)
            # Usamos distinct() porque si una región tiene 5 torneos, 
            # el JOIN nos devolvería la misma región 5 veces.
            .distinct()
        )
        return self.session.scalars(statement).all()

    def count_players(self, region_id: int) -> int:
        """
        Un conteo súper optimizado de cuántos jugadores pertenecen a la región.
        """
        statement = (
            # func.count() delega el trabajo pesado a la base de datos.
            # Es muchísimo más rápido que traerse todos los jugadores 
            # con un select() normal y hacer un len(lista) en Python.
            select(func.count(Player.id_player))
            .where(Player.id_region == region_id)
        )
        # scalar() ejecutará la consulta y devolverá el número entero directamente
        resultado = self.session.scalar(statement)
        
        # Por seguridad, si por algún motivo la consulta devuelve None, retornamos 0
        return resultado or 0