import sys
import os

# Agregamos la raíz al path
sys.path.append(os.path.abspath(os.path.join('.')))

from src.domain.db import Session, engine
from esports_tournament_ValdezJoan.src.domain._old_models import (
    Region, VideoGameType, TournamentMode, TournamentStatus,
    Player, PlayerProfile, Team, PlayerTeam, 
    Tournament, TeamTournament, Match
)

def verify_population():
    db = Session()
    
    # Lista de modelos para auditar
    models = [
        Region, VideoGameType, TournamentMode, TournamentStatus,
        Player, PlayerProfile, Team, PlayerTeam, 
        Tournament, TeamTournament, Match
    ]
    
    print("\n=== AUDITORÍA DE BASE DE DATOS ===")
    print(f"{'Tabla':<20} | {'Registros':<10}")
    print("-" * 35)
    
    total_general = 0
    
    try:
        for model in models:
            # Consultamos el conteo de cada tabla
            count = db.query(model).count()
            print(f"{model.__tablename__:<20} | {count:<10}")
            total_general += count
            
        print("-" * 35)
        print(f"{'TOTAL GENERAL':<20} | {total_general:<10}")
        
    except Exception as e:
        print(f"❌ Error al consultar las tablas: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_population()