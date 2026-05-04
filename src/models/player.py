from common import String, Date, Integer, ForeignKey, Boolean, Numeric, DateTime, Text, Mapped, mapped_column, relationship, date, datetime, Optional, List
from domain import Base

from .region import Region
from .playerprofile import PlayerProfile
from .playerteam import PlayerTeam

class Player(Base):
    id_player:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname:Mapped[str] = mapped_column(String(100), nullable=False)
    email:Mapped[str] = mapped_column(String(100),nullable=False)
    birth_date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    registration_date:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active:Mapped[bool] = mapped_column(Boolean, default=True)

    id_region:Mapped[int] = mapped_column(ForeignKey("region.id_region"))

    region: Mapped["Region"] = relationship(back_populates="players")
    profile: Mapped["PlayerProfile"] = relationship(back_populates="players", uselist=False)
    player_teams: Mapped[List["PlayerTeam"]] = relationship(back_populates="player")