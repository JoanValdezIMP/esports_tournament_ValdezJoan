from sqlalchemy import create_engine
from src.domain.models import Base
import sqlalchemy

# CAMBIO CRÍTICO: postgresql+psycopg2://
# Cambia esta línea:
URL_AIVEN = "postgresql+psycopg2://avnadmin:AVNS_RbP8a8oY-xsdJz4LhUc@pg-250affac-joan1234.d.aivencloud.com:14173/esports_torunament?sslmode=require"

try:
    print("Intentando conectar a Aiven con el driver psycopg2...")
    engine = create_engine(URL_AIVEN)
    
    # Intentamos una conexión real
    with engine.connect() as conn:
        print("✅ ¡Conexión física exitosa!")
        
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas en el esquema public.")

except Exception as e:
    print(f"❌ Error: {e}")