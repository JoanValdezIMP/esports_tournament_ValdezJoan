from .common import String, Integer, ForeignKey, Boolean, DateTime, Mapped, mapped_column, relationship, datetime, List
from domain.db import Base

class Player(Base):
    __tablename__ = "player"

    id_player: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100),nullable=False)
    birth_date: Mapped[datetime] = mapped_column(DateTime,nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    id_region: Mapped[int] = mapped_column(ForeignKey("region.id_region"))

    region: Mapped["Region"] = relationship(back_populates="players")
    profile: Mapped["PlayerProfile"] = relationship(back_populates="player", uselist=False)
    player_teams: Mapped[List["PlayerTeam"]] = relationship(back_populates="player")
