# class VideoGameType(Base):
#     __tablename__ = "video_game_type"

#     id_video_game_type: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(Text)

#     tournaments: Mapped[List["Tournament"]] = relationship(back_populates="video_game_type")
from sqlalchemy.orm import Session


# from .db import Session
from .models import (
    Region, 
    VideoGameType, 
    TournamentMode, 
    TournamentStatus,
    Player, 
    PlayerProfile, 
    Team, 
    PlayerTeam, 
    Tournament, 
    TeamTournament, 
    Match
)
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):

    def __init__(self, session: Session):
        self.session = session

    def save(self, t: T):
        self._validate(t)  # 👈 VALIDACIÓN

        if t.id is None:
            self.session.add(t)
        else:
            raise NotImplementedError("Update method not implemented yet")

    def get(self, id: int):
        raise NotImplementedError()

    def _validate(self, t: T) -> None:
        pass




class VideoGameTypeRepository(Repository[VideoGameType]):

    def _validate(self, v: VideoGameType):
        if not v.name or v.name.strip() == "":
            raise ValueError("Name vacío")



class RegionRepository(Repository[Region]):

    def _validate(self, r: Region):
        if not r.name or r.name.strip() == "":
            raise ValueError("Name vacío")

        if not r.country_code:
            raise ValueError("Country code obligatorio")

        if len(r.country_code) > 10:
            raise ValueError("Country code demasiado largo")



class PlayerRepository(Repository[Player]):

    def _validate(self, p: Player):

        if not p.nickname or p.nickname.strip() == "":
            raise ValueError("Nickname obligatorio")

        if not p.email or "@" not in p.email:
            raise ValueError("Email inválido")

        if not p.birth_date:
            raise ValueError("Fecha de nacimiento obligatoria")

        if not p.registration_date:
            raise ValueError("Fecha de registro obligatoria")

        if p.birth_date > p.registration_date:
            raise ValueError("Birth date no puede ser mayor que registration date")

        if p.id_region is None:
            raise ValueError("Region obligatoria")



class PlayerProfileRepository(Repository[PlayerProfile]):

    def _validate(self, p: PlayerProfile):

        if p.total_matches < 0:
            raise ValueError("Matches no puede ser negativo")

        if p.total_wins < 0 or p.total_losses < 0:
            raise ValueError("Wins/Losses no pueden ser negativos")

        if p.total_points < 0:
            raise ValueError("Points no puede ser negativo")

        if p.ranking_position <= 0:
            raise ValueError("Ranking debe ser mayor que 0")

        if p.id_player is None:
            raise ValueError("Player obligatorio")



class TeamRepository(Repository[Team]):

    def _validate(self, t: Team):

        if not t.name or t.name.strip() == "":
            raise ValueError("Nombre obligatorio")

        if not t.creation_date:
            raise ValueError("Fecha de creación obligatoria")

        if t.id_region is None:
            raise ValueError("Region obligatoria")



class TournamentModeRepository(Repository[TournamentMode]):

    def _validate(self, t: TournamentMode):

        if not t.name or t.name.strip() == "":
            raise ValueError("Nombre obligatorio")



class TournamentStatusRepository(Repository[TournamentStatus]):

    def _validate(self, t: TournamentStatus):

        if not t.name or t.name.strip() == "":
            raise ValueError("Nombre obligatorio")




class TournamentRepository(Repository[Tournament]):

    def _validate(self, t: Tournament):

        if not t.name or t.name.strip() == "":
            raise ValueError("Nombre obligatorio")

        if not t.start_date:
            raise ValueError("Start date obligatoria")

        if t.end_date and t.end_date < t.start_date:
            raise ValueError("End date no puede ser menor que start date")

        if t.prize_pool is not None and t.prize_pool < 0:
            raise ValueError("Prize pool no puede ser negativo")

        if t.max_teams is not None and t.max_teams <= 0:
            raise ValueError("Max teams debe ser mayor que 0")

        if t.id_region is None:
            raise ValueError("Region obligatoria")

        if t.id_video_game_type is None:
            raise ValueError("VideoGameType obligatorio")

        if t.id_tournament_mode is None:
            raise ValueError("Mode obligatorio")

        if t.id_tournament_status is None:
            raise ValueError("Status obligatorio")



class MatchRepository(Repository[Match]):

    def _validate(self, m: Match):

        if not m.match_date:
            raise ValueError("Fecha obligatoria")

        if m.score_team_one < 0 or m.score_team_two < 0:
            raise ValueError("Scores no pueden ser negativos")

        if m.id_team_one == m.id_team_two:
            raise ValueError("Un equipo no puede jugar contra sí mismo")

        if m.id_tournament is None:
            raise ValueError("Tournament obligatorio")



class PlayerTeamRepository(Repository[PlayerTeam]):

    def _validate(self, pt: PlayerTeam):

        if pt.id_player is None or pt.id_team is None:
            raise ValueError("Player y Team obligatorios")

        if not pt.join_date:
            raise ValueError("Join date obligatoria")



class TeamTournamentRepository(Repository[TeamTournament]):

    def _validate(self, tt: TeamTournament):

        if tt.id_team is None or tt.id_tournament is None:
            raise ValueError("Team y Tournament obligatorios")

        if tt.points_obtained < 0:
            raise ValueError("Points no pueden ser negativos")

        if tt.final_position is not None and tt.final_position <= 0:
            raise ValueError("Posición debe ser mayor que 0")


