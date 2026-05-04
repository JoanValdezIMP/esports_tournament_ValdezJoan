from common import Integer, ForeignKey, DateTime, Mapped, mapped_column, relationship, datetime, Optional
from domain import Base, Team, Tournament


class PlayerTeam(Base):
    __tablename__ = "team_tournament"

    id_team: Mapped[int] = mapped_column(ForeignKey("team.id_team"), primary_key=True)
    id_tournament: Mapped[int] = mapped_column(ForeignKey("tournament.id_tournament"), primary_key=True)
    final_position: Mapped[Optional[int]] = mapped_column(Integer)
    points_obtained: Mapped[int] = mapped_column(Integer, default=0)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    team: Mapped["Team"] = relationship(back_populates="team_tournaments")
    tournament: Mapped["Tournament"] = relationship(back_populates="tournament_teams")
