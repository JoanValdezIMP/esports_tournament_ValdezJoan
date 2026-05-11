
from .common import Integer, ForeignKey, DateTime, Mapped, mapped_column, relationship, datetime, Optional
from domain.db import Base




class PlayerTeam(Base):
    __tablename__ = "player_team"

    id_player: Mapped[int] = mapped_column(ForeignKey("player.id_player"), primary_key=True)
    id_team: Mapped[int] = mapped_column(ForeignKey("team.id_team"), primary_key=True)
    final_position: Mapped[Optional[int]] = mapped_column(Integer)
    points_obtained: Mapped[int] = mapped_column(Integer, default=0)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    player: Mapped["Player"] = relationship(back_populates="player_teams")
    team: Mapped["Team"] = relationship(back_populates="team_players")
