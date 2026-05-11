from .common import String, Date, Integer, ForeignKey, Boolean, Mapped, mapped_column, relationship, date, Optional, List
from domain.db import Base


class Team(Base):
    __tablename__ = "team"

    id_team: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    creation_date: Mapped[date] = mapped_column(Date, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    id_region: Mapped[int] = mapped_column(ForeignKey("region.id_region"))

    # Relaciones
    region: Mapped["Region"] = relationship(back_populates="teams")
    team_players: Mapped[List["PlayerTeam"]] = relationship(back_populates="team")
    team_tournaments: Mapped[List["TeamTournament"]] = relationship(back_populates="team")

    @property
    def id(self):
        return self.id_team