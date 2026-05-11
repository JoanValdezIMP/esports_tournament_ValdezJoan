import sys
import os
import random
from datetime import date, datetime, timedelta
from faker import Faker

# Configuración de rutas
sys.path.append(os.path.abspath(os.path.join('.')))

from src.domain.db import Session, engine, Base
from esports_tournament_ValdezJoan.src.domain._old_models import (
    Region, VideoGameType, TournamentMode, TournamentStatus,
    Player, PlayerProfile, Team, PlayerTeam, 
    Tournament, TeamTournament, Match
)

fake = Faker()
db = Session()

def populate_database(n=150):
    try:
        print(f"--- Iniciando población de {n} registros por tabla ---")
        
        # 1. Catálogos Básicos - Creamos exactamente N de cada uno
        regions = [Region(name=fake.country()[:100], country_code=fake.country_code()) for _ in range(n)]
        game_types = [VideoGameType(name=fake.word().capitalize() + " Game", description=fake.sentence()) for _ in range(n)]
        modes = [TournamentMode(name=fake.word().capitalize(), description=fake.sentence()) for _ in range(n)]
        
        status_names = ["Upcoming", "Ongoing", "Finished", "Cancelled"]
        statuses = [TournamentStatus(name=status_names[i % 4], description=fake.sentence()) for i in range(n)]
        
        # Guardamos y flusheamos para obtener IDs
        db.add_all(regions + game_types + modes + statuses)
        db.flush() 

        # 2. Players & Teams
        players = []
        teams = []
        for _ in range(n):
            p = Player(
                nickname=fake.user_name()[:100],
                email=fake.unique.email()[:100],
                birth_date=fake.date_of_birth(minimum_age=15, maximum_age=40),
                registration_date=fake.date_between(start_date='-2y', end_date='today'),
                active=True,
                id_region=random.choice(regions).id_region
            )
            players.append(p)
            
            t = Team(
                name=fake.company()[:100] + " Esports",
                creation_date=fake.date_between(start_date='-3y', end_date='-1y'),
                logo_url=fake.image_url()[:255],
                active=True,
                id_region=random.choice(regions).id_region
            )
            teams.append(t)

        db.add_all(players + teams)
        db.flush()

        # 3. PlayerProfiles & PlayerTeam
        profiles = []
        player_teams = []
        for i in range(n):
            profiles.append(PlayerProfile(
                total_matches=random.randint(0, 100),
                total_wins=random.randint(0, 50),
                total_losses=random.randint(0, 50),
                total_points=random.randint(0, 1000),
                ranking_position=i + 1,
                id_player=players[i].id_player
            ))
            
            player_teams.append(PlayerTeam(
                id_player=players[i].id_player,
                id_team=random.choice(teams).id_team,
                join_date=fake.date_between(start_date='-1y', end_date='today')
            ))

        db.add_all(profiles + player_teams)
        db.flush()

        # 4. Tournaments
        tournaments = []
        for i in range(n):
            tournaments.append(Tournament(
                name=f"{fake.word().capitalize()} Cup {i}",
                start_date=fake.date_between(start_date='today', end_date='+30d'),
                end_date=fake.date_between(start_date='+31d', end_date='+60d'),
                prize_pool=random.uniform(1000, 50000),
                max_teams=random.choice([8, 16, 32, 64]),
                id_region=random.choice(regions).id_region,
                id_video_game_type=random.choice(game_types).id_video_game_type,
                id_tournament_mode=random.choice(modes).id_tournament_mode,
                id_tournament_status=random.choice(statuses).id_tournament_status
            ))
        
        db.add_all(tournaments)
        db.flush()

        # 5. TeamTournament & Matches
        for i in range(n):
            db.add(TeamTournament(
                id_team=random.choice(teams).id_team,
                id_tournament=tournaments[i].id_tournament,
                registered_at=datetime.now()
            ))

            db.add(Match(
                match_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                score_team_one=random.randint(0, 5),
                score_team_two=random.randint(0, 5),
                round_number=random.randint(1, 3),
                duration_minutes=random.randint(15, 45),
                id_team_one=random.choice(teams).id_team,
                id_team_two=random.choice(teams).id_team,
                id_tournament=tournaments[i].id_tournament
            ))

        db.commit()
        print(f"✅ ¡Población completada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error poblando la base de datos: {e}")
    finally:
        db.close()
if __name__ == "__main__":
    # Asegúrate de que las tablas existan antes de poblar
    Base.metadata.create_all(bind=engine)
    populate_database(150)