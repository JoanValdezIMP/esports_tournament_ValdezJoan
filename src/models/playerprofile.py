from .common import Integer, ForeignKey, DateTime, Mapped, mapped_column, relationship, datetime
from domain.db import Base


class PlayerProfile(Base):
    __tablename__ = "player_profile"

    id_player_profile: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    total_wins: Mapped[int] = mapped_column(Integer, default=0)
    total_losses: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    ranking_position: Mapped[int] = mapped_column(Integer)
    # last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    id_player: Mapped[int] = mapped_column(ForeignKey("player.id_player"), unique=True)
    player: Mapped["Player"] = relationship(back_populates="profile")


    @property
    def id(self):
        return self.id_player_profile