from .common import String, Integer, Text, Mapped, mapped_column, relationship, Optional, List
from domain.db import Base


class TournamentMode(Base):
    __tablename__ = "tournament_mode"

    id_tournament_mode: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="tournament_mode")


    @property
    def id(self):
        return self.id_tournament_mode