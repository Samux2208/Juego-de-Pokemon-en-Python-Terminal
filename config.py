from pathlib import Path

# ============================================================
# CONFIGURACIONES GENERALES Y RUTAS DEL PROYECTO
# ============================================================

VERSION = 2
RETRASO_TEXTO = 0.05       # Pausa en segundos entre caracteres al mostrar texto
NIVEL_MAXIMO = 100         # Nivel máximo permitido para un Pokémon
DINERO_INICIAL = 3000      # Dinero inicial del jugador al comenzar partida

# Carpeta raíz del proyecto (donde vive este config.py)
BASE_DIR = Path(__file__).resolve().parent

# Carpetas de datos y partidas guardadas
DATOS_DIR = BASE_DIR / "datos"
PARTIDAS_DIR = BASE_DIR / "partidas"
BACKUPS_DIR = PARTIDAS_DIR / "backups"

# Garantiza que existan las carpetas principales al iniciar
DATOS_DIR.mkdir(exist_ok=True)
PARTIDAS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

# Archivo principal de partida guardada
ARCHIVO_PARTIDA = PARTIDAS_DIR / "partida.json"

# Pokémon iniciales disponibles para elegir al empezar
INICIALES = {
    1: "Charmander",
    2: "Squirtle",
    3: "Bulbasaur",
}