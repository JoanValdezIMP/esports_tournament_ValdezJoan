from .common import String, Integer, Text, Mapped, mapped_column, relationship, Optional, List
from domain.db import Base


class VideoGameType(Base):
    __tablename__ = "video_game_type"

    id_video_game_type: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="video_game_type")

    @property
    def id(self):
        return self.id_video_game_type