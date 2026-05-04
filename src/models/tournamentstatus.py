from common import String, Integer, Text, Mapped, mapped_column, relationship, Optional, List
from domain import Base, Tournament

class TournamentStatus(Base):
    __tablename__ = "tournament_status"

    id_tournament_status: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="tournament_status")

    @property
    def id(self):
        return self.id_tournament_status