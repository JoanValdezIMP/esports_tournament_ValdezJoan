'''
from common import String, Date, Integer, ForeignKey, Boolean, Numeric, DateTime, Text, Mapped, mapped_column, relationship, date, datetime, Optional, List
from domain import Base


# --- TABLAS DE APOYO (CATÁLOGOS) ---

class Region(Base):
    __tablename__ = "region"

    id_region: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(10), nullable=False)

    players: Mapped[List["Player"]] = relationship(back_populates="region")
    teams: Mapped[List["Team"]] = relationship(back_populates="region")
    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="region")

class VideoGameType(Base):
    __tablename__ = "video_game_type"

    id_video_game_type: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="video_game_type")

class TournamentMode(Base):
    __tablename__ = "tournament_mode"

    id_tournament_mode: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="tournament_mode")

class TournamentStatus(Base):
    __tablename__ = "tournament_status"

    id_tournament_status: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    tournaments: Mapped[List["Tournament"]] = relationship(back_populates="tournament_status")

# --- TABLAS PRINCIPALES ---

class Player(Base):
    __tablename__ = "player"

    id_player: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_date: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    id_region: Mapped[int] = mapped_column(ForeignKey("region.id_region"))

    # Relaciones
    region: Mapped["Region"] = relationship(back_populates="players")
    profile: Mapped[Optional["PlayerProfile"]] = relationship(back_populates="player", uselist=False)
    player_teams: Mapped[List["PlayerTeam"]] = relationship(back_populates="player")

class PlayerProfile(Base):
    __tablename__ = "player_profile"

    id_player_profile: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    total_wins: Mapped[int] = mapped_column(Integer, default=0)
    total_losses: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    ranking_position: Mapped[int] = mapped_column(Integer)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    id_player: Mapped[int] = mapped_column(ForeignKey("player.id_player"), unique=True)
    player: Mapped["Player"] = relationship(back_populates="profile")

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

# --- RELACIONES N:M CON ATRIBUTOS (Association Objects) ---

class PlayerTeam(Base):
    __tablename__ = "player_team"

    id_player: Mapped[int] = mapped_column(ForeignKey("player.id_player"), primary_key=True)
    id_team: Mapped[int] = mapped_column(ForeignKey("team.id_team"), primary_key=True)
    join_date: Mapped[date] = mapped_column(Date, nullable=False)

    player: Mapped["Player"] = relationship(back_populates="player_teams")
    team: Mapped["Team"] = relationship(back_populates="team_players")

class TeamTournament(Base):
    __tablename__ = "team_tournament"

    id_team: Mapped[int] = mapped_column(ForeignKey("team.id_team"), primary_key=True)
    id_tournament: Mapped[int] = mapped_column(ForeignKey("tournament.id_tournament"), primary_key=True)
    final_position: Mapped[Optional[int]] = mapped_column(Integer)
    points_obtained: Mapped[int] = mapped_column(Integer, default=0)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    team: Mapped["Team"] = relationship(back_populates="team_tournaments")
    tournament: Mapped["Tournament"] = relationship(back_populates="tournament_teams")

# --- TORNEO Y PARTIDAS ---

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

class Match(Base):
    __tablename__ = "match"

    id_match: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    score_team_one: Mapped[int] = mapped_column(Integer, default=0)
    score_team_two: Mapped[int] = mapped_column(Integer, default=0)
    round_number: Mapped[int] = mapped_column(Integer)
    duration_minutes: Mapped[int] = mapped_column(Integer)

    id_team_one: Mapped[int] = mapped_column(ForeignKey("team.id_team"))
    id_team_two: Mapped[int] = mapped_column(ForeignKey("team.id_team"))
    id_team_winner: Mapped[Optional[int]] = mapped_column(ForeignKey("team.id_team"))
    id_tournament: Mapped[int] = mapped_column(ForeignKey("tournament.id_tournament"))

    tournament: Mapped["Tournament"] = relationship(back_populates="matches")

'''