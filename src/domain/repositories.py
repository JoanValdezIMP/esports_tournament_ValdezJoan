# class VideoGameType(Base):
#     __tablename__ = "video_game_type"

#     id_video_game_type: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(Text)

#     tournaments: Mapped[List["Tournament"]] = relationship(back_populates="video_game_type")
from sqlalchemy.orm import Session


# from .db import Session
from .models import (
    VideoGameType,
    Region
)
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):

    def __init__(self, session: Session):
        self.session = session

    def save(self, t: T):
        if t.id == None:
            self.session.add(t)
        else:
            # self.update(t)
            raise NotImplementedError("Update method not implemented yet")

    def get(self, id:int):
        ... 





class VideoGameTypeRepository(Repository[VideoGameType]):
    ...

class RegionRepository(Repository[Region]):
    ...