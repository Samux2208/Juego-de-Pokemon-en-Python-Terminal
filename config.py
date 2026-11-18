from pathlib import Path

# ============================================================
# CONSTANTES GENERALES
# ============================================================

VERSION = 2
RETRASO_TEXTO = 0.05      # Segundos entre letras en imprimir_con_retraso
NIVEL_MAXIMO = 100
DINERO_INICIAL = 3000

# Obtiene la ruta absoluta de la carpeta donde se encuentra este archivo game.py
BASE_DIR = Path(__file__).resolve().parent
DATOS_DIR = BASE_DIR / "datos"
PARTIDAS_DIR = BASE_DIR / "partidas"
BACKUPS_DIR = PARTIDAS_DIR / "backups"

# Crea ambas carpetas automáticamente si no existen
DATOS_DIR.mkdir(exist_ok=True)
PARTIDAS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

ARCHIVO_PARTIDA = PARTIDAS_DIR / "partida.json"

# ============================================================
# TIPOS, EMOJIS Y TABLA DE EFECTIVIDADES (GEN III: 17 TIPOS)
# Las claves se guardan en minúscula y sin tildes; para mostrarlos
# en pantalla se usa nombre_tipo().
# ============================================================

# Tipo de Pokémon dispoinibles
TIPOS = (
    "normal", "fuego", "agua", "electrico", "planta", "hielo", "lucha",
    "veneno", "tierra", "volador", "psiquico", "bicho", "roca", "fantasma",
    "dragon", "siniestro", "acero",
)

# Nombres corregidos con tilde y en Mayuscula la primera letra
NOMBRES_TIPO = {
    "electrico": "Eléctrico",
    "psiquico": "Psíquico",
    "dragon": "Dragón"
}

# Emojis que representan los tipos del pokémon
ICONOS_TIPO = {
    "normal": "⚪", "fuego": "🔥", "agua": "💧", "electrico": "⚡",
    "planta": "🌿", "hielo": "❄️", "lucha": "🥊", "veneno": "☠️ ",
    "tierra": "🏜️", "volador": "🕊️", "psiquico": "🔮", "bicho": "🐛",
    "roca": "🪨", "fantasma": "👻", "dragon": "🐉", "siniestro": "🌑",
    "acero": "⚙️",
}

def nombre_tipo(tipo, emoji=True):
    '''Devuelve el nombre del tipo formateado con emoji, tildes y mayúscula.'''
    texto = NOMBRES_TIPO.get(tipo, tipo.capitalize())
    if emoji:
        return f"{ICONOS_TIPO.get(tipo, '🔹')} {texto}"
    return texto

# Emojis que representan las categorías del pokémon
ICONOS_CATEGORIA = {
    "fisico": "💥 Fís",
    "especial": "✨ Esp",
    "estado": "🌀 Est",
}

# En la Gen III la categoría (físico/especial) de movimientos ofensivos depende del TIPO.
TIPOS_ESPECIALES = {"fuego", "agua", "planta", "electrico", "hielo", "psiquico", "dragon", "siniestro"}

# == TABLA DE EFECTIVIDADES DE TIPOS ========================
# _EFECTIVIDADES | Formato -> atacante: {multiplicador: (defensores...)}
#   - 2.0 (Súper eficaz)  |  0.5 (Poco eficaz)  |  0.0 (Inmune)
#
# TABLA_TIPOS | Formato -> atacante: {defensor: multiplicador}
#   - Solo almacena relaciones no neutras. Para consultar el daño en combate,
#     usa: TABLA_TIPOS[atacante].get(defensor, 1.0)
# ============================================================

_EFECTIVIDADES = {
    "normal":    {0.5: ("roca", "acero"), 0.0: ("fantasma",)},
    "fuego":     {2.0: ("planta", "hielo", "bicho", "acero"), 0.5: ("fuego", "agua", "roca", "dragon")},
    "agua":      {2.0: ("fuego", "tierra", "roca"), 0.5: ("agua", "planta", "dragon")},
    "electrico": {2.0: ("agua", "volador"), 0.5: ("electrico", "planta", "dragon"), 0.0: ("tierra",)},
    "planta":    {2.0: ("agua", "tierra", "roca"),
                  0.5: ("fuego", "planta", "veneno", "volador", "bicho", "dragon", "acero")},
    "hielo":     {2.0: ("planta", "tierra", "volador", "dragon"), 0.5: ("fuego", "agua", "hielo", "acero")},
    "lucha":     {2.0: ("normal", "hielo", "roca", "siniestro", "acero"),
                  0.5: ("veneno", "volador", "psiquico", "bicho"), 0.0: ("fantasma",)},
    "veneno":    {2.0: ("planta",), 0.5: ("veneno", "tierra", "roca", "fantasma"), 0.0: ("acero",)},
    "tierra":    {2.0: ("fuego", "electrico", "veneno", "roca", "acero"), 0.5: ("planta", "bicho"),
                  0.0: ("volador",)},
    "volador":   {2.0: ("planta", "lucha", "bicho"), 0.5: ("electrico", "roca", "acero")},
    "psiquico":  {2.0: ("lucha", "veneno"), 0.5: ("psiquico", "acero"), 0.0: ("siniestro",)},
    "bicho":     {2.0: ("planta", "psiquico", "siniestro"),
                  0.5: ("fuego", "lucha", "veneno", "volador", "fantasma", "acero")},
    "roca":      {2.0: ("fuego", "hielo", "volador", "bicho"), 0.5: ("lucha", "tierra", "acero")},
    "fantasma":  {2.0: ("psiquico", "fantasma"), 0.5: ("siniestro", "acero"), 0.0: ("normal",)},
    "dragon":    {2.0: ("dragon",), 0.5: ("acero",)},
    "siniestro": {2.0: ("psiquico", "fantasma"), 0.5: ("lucha", "siniestro", "acero")},
    "acero":     {2.0: ("hielo", "roca"), 0.5: ("fuego", "agua", "electrico", "acero")},
}

# Invertimos la estructura para permitir búsquedas directas por [atacante][defensor]
TABLA_TIPOS = {
    atacante: {
        defensor: multiplicador
        for multiplicador, defensores in grupos.items()
        for defensor in defensores
    }
    for atacante, grupos in _EFECTIVIDADES.items()
}

# _CLAVES_STATS | Orden de las estadísticas base de cada Pokémon.
_CLAVES_STATS = ("vida", "ataque", "defensa", "atq_esp", "def_esp", "velocidad")

# Opciones de Pokémon iniciales disponibles al comenzar la partida
INICIALES = {
    1: "Charmander",
    2: "Squirtle",
    3: "Bulbasaur"
}

# == DICCIONARIOS DE EVOLUCIÓN (KANTO) ======================
# EVOLUCIONES_NIVEL  | Formato -> nombre: (nivel, evolucion)
# EVOLUCIONES_OBJETO | Formato -> piedra: {nombre: evolucion}
# ============================================================

# Evoluciones activadas al alcanzar el nivel indicado
EVOLUCIONES_NIVEL = {
    "Bulbasaur": (16, "Ivysaur"), "Ivysaur": (32, "Venusaur"),
    "Charmander": (16, "Charmeleon"), "Charmeleon": (36, "Charizard"),
    "Squirtle": (16, "Wartortle"), "Wartortle": (36, "Blastoise"),
    "Caterpie": (7, "Metapod"), "Metapod": (10, "Butterfree"),
    "Weedle": (7, "Kakuna"), "Kakuna": (10, "Beedrill"),
    "Pidgey": (18, "Pidgeotto"), "Pidgeotto": (36, "Pidgeot"),
    "Rattata": (20, "Raticate"),
    "Spearow": (20, "Fearow"),
    "Ekans": (22, "Arbok"),
    "Sandshrew": (22, "Sandslash"),
    "Nidoran♀": (16, "Nidorina"),
    "Nidoran♂": (16, "Nidorino"),
    "Zubat": (22, "Golbat"),
    "Oddish": (21, "Gloom"),
    "Paras": (24, "Parasect"),
    "Venonat": (31, "Venomoth"),
    "Diglett": (26, "Dugtrio"),
    "Meowth": (28, "Persian"),
    "Psyduck": (33, "Golduck"),
    "Mankey": (28, "Primeape"),
    "Poliwag": (25, "Poliwhirl"),
    "Abra": (16, "Kadabra"), "Kadabra": (36, "Alakazam"),
    "Machop": (28, "Machoke"), "Machoke": (36, "Machamp"),
    "Bellsprout": (21, "Weepinbell"),
    "Tentacool": (30, "Tentacruel"),
    "Geodude": (25, "Graveler"), "Graveler": (36, "Golem"),
    "Ponyta": (40, "Rapidash"),
    "Slowpoke": (37, "Slowbro"),
    "Doduo": (31, "Dodrio"),
    "Seel": (34, "Dewgong"),
    "Grimer": (38, "Muk"),
    "Gastly": (25, "Haunter"), "Haunter": (36, "Gengar"),
    "Drowzee": (26, "Hypno"),
    "Krabby": (28, "Kingler"),
    "Voltorb": (30, "Electrode"),
    "Cubone": (28, "Marowak"),
    "Koffing": (35, "Weezing"),
    "Rhyhorn": (42, "Rhydon"),
    "Horsea": (32, "Seadra"),
    "Goldeen": (33, "Seaking"),
    "Magikarp": (20, "Gyarados"),
    "Dratini": (30, "Dragonair"), "Dragonair": (55, "Dragonite"),
}

# Evoluciones activadas al usar una piedra evolutiva sobre el Pokémon
EVOLUCIONES_OBJETO = {
    "Piedra Fuego": {
        "Vulpix": "Ninetales",
        "Growlithe": "Arcanine",
        "Eevee": "Flareon"
    },
    "Piedra Agua": {
        "Poliwhirl": "Poliwrath",
        "Shellder": "Cloyster",
        "Staryu": "Starmie",
        "Eevee": "Vaporeon"
    },
    "Piedra Trueno": {
        "Pikachu": "Raichu",
        "Eevee": "Jolteon"
    },
    "Piedra Hoja": {
        "Gloom": "Vileplume",
        "Weepinbell": "Victreebel",
        "Exeggcute": "Exeggutor"
    },
    "Piedra Lunar": {
        "Nidorina": "Nidoqueen",
        "Nidorino": "Nidoking",
        "Clefairy": "Clefable",
        "Jigglypuff": "Wigglytuff"
    },
}