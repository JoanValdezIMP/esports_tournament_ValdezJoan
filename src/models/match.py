from common import Integer, ForeignKey, DateTime, Mapped, mapped_column, relationship, datetime, Optional
from domain import Base

from .tournament import Tournament
from .team import Team

class Match(Base):
    __tablename__ = "match"

    id_match: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    score_team_one: Mapped[int] = mapped_column(Integer, default=0)
    score_team_two: Mapped[int] = mapped_column(Integer, default=0)
    round_number: Mapped[int] = mapped_column(Integer)
    duration_minutes: Mapped[int] = mapped_column(Integer)

    id_team_one: Mapped[int] = mapped_column(ForeignKey("team.id_team"))
    id_team_two: Mapped[int] = mapped_column(ForeignKey("team.id_team"))
    id_team_winner: Mapped[Optional[int]] = mapped_column(ForeignKey("team.id_team"))
    id_tournament: Mapped[int] = mapped_column(ForeignKey("tournament.id_tournament"))


# Relaciones con nombres explícitos para que el ORM no se pierda
    team_one: Mapped["Team"] = relationship(foreign_keys=[id_team_one])
    team_two: Mapped["Team"] = relationship(foreign_keys=[id_team_two])
    winner: Mapped[Optional["Team"]] = relationship(foreign_keys=[id_team_winner])


    tournament: Mapped["Tournament"] = relationship(back_populates="matches")

    @property
    def id(self):
        return self.id_match
