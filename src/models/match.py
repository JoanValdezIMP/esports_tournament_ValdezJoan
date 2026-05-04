from common import String, Date, Integer, ForeignKey, Boolean, Numeric, DateTime, Text, Mapped, mapped_column, relationship, date, datetime, Optional, List
from domain import Base

from .tournament import Tournament

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

    tournament: Mapped["Tournament"] = relationship(back_populates="matches")

    @property
    def id(self):
        return self.id_match
