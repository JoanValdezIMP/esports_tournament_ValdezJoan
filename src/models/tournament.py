from common import String, Date, Integer, ForeignKey, Numeric, Mapped, mapped_column, relationship, date, List
from domain import Base, Region, VideoGameType, TournamentMode, TournamentStatus, TeamTournament, Match

class Tournament(Base):
    __tablename__ = "tournament"

    id_tournament: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date)
    prize_pool: Mapped[float] = mapped_column(Numeric(12, 2))
    max_teams: Mapped[int] = mapped_column(Integer)

    id_region: Mapped[int] = mapped_column(ForeignKey("region.id_region"))
    id_video_game_type: Mapped[int] = mapped_column(ForeignKey("video_game_type.id_video_game_type"))
    id_tournament_mode: Mapped[int] = mapped_column(ForeignKey("tournament_mode.id_tournament_mode"))
    id_tournament_status: Mapped[int] = mapped_column(ForeignKey("tournament_status.id_tournament_status"))

    # Relaciones
    region: Mapped["Region"] = relationship(back_populates="tournaments")
    video_game_type: Mapped["VideoGameType"] = relationship(back_populates="tournaments")
    tournament_mode: Mapped["TournamentMode"] = relationship(back_populates="tournaments")
    tournament_status: Mapped["TournamentStatus"] = relationship(back_populates="tournaments")
    
    tournament_teams: Mapped[List["TeamTournament"]] = relationship(back_populates="tournament")
    matches: Mapped[List["Match"]] = relationship(back_populates="tournament")
    
    @property
    def id(self):
        return self.id_tournament