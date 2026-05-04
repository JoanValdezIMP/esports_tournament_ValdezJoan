from common import String, Integer, Mapped, mapped_column, relationship, List
from domain import Base, Tournament, Team, Player

class Region(Base):
    __tablename__ = "region"

    id_region: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(10), nullable=False)

    players: Mapped[List["Player"]] = relationship(back_populates="region")
    teams: Mapped[List["Team"]] = relationship(back_populates="region")
    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="region")

    @property
    def id(self):
        return self.id_region