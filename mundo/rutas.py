'''Definición de rutas y zonas explorables de Kanto.

Cada elemento de `RUTAS` describe una zona con su rango de niveles,
mensaje narrativo de entrada y lista de especies salvajes disponibles.
'''

# == KANTO (PROGRESIÓN Y ENCUENTROS SALVAJES) ==============
# RUTAS | Lista de zonas ordenadas por dificultad progresiva.
#   - nombre (str): Nombre de la ruta o zona explorada.
#   - niveles (tuple): Rango de nivel (mínimo, máximo) de los salvajes.
#   - mensaje (str): Texto narrativo al entrar a explorar la zona.
#   - pool (list): Especies de Pokémon que pueden aparecer en la zona.
# ============================================================

RUTAS = [
    {
        "nombre": "Ruta 1 - Pueblo Paleta",
        "niveles": (2, 5),
        "mensaje": "\n🚶 Caminando en la hierba baja de la Ruta 1...\n",
        "pool": ["Pidgey", "Rattata"],
    },
    {
        "nombre": "Bosque Verde",
        "niveles": (3, 7),
        "mensaje": "\n🌲 Adentrándote entre los árboles del Bosque Verde...\n",
        "pool": ["Caterpie", "Weedle", "Metapod", "Kakuna", "Pidgey", "Rattata", "Pikachu"],
    },
    {
        "nombre": "Monte Moon (cueva)",
        "niveles": (10, 16),
        "mensaje": "\n🌙 Tus pasos resuenan en la oscuridad del Monte Moon...\n",
        "pool": ["Zubat", "Geodude", "Paras", "Clefairy", "Sandshrew", "Jigglypuff"],
    },
    {
        "nombre": "Praderas de Kanto (Rutas 5-8)",
        "niveles": (10, 18),
        "mensaje": "\n🌾 Cruzando las amplias praderas entre ciudades...\n",
        "pool": [
            "Oddish", "Bellsprout", "Meowth", "Mankey", "Growlithe", "Vulpix", "Abra",
            "Ekans", "Nidoran♀", "Nidoran♂", "Venonat", "Pidgeotto",
        ],
    },
    {
        "nombre": "Costa Marina (Rutas 12-19)",
        "niveles": (14, 22),
        "mensaje": "\n🌊 Cruzando las corrientes de la costa...\n",
        "pool": [
            "Psyduck", "Poliwag", "Krabby", "Tentacool", "Goldeen", "Horsea", "Staryu",
            "Shellder", "Slowpoke", "Seel", "Magikarp",
        ],
    },
    {
        "nombre": "Túnel Roca (cueva)",
        "niveles": (16, 24),
        "mensaje": "\n🔦 Avanzas a ciegas por el Túnel Roca...\n",
        "pool": ["Zubat", "Golbat", "Geodude", "Graveler", "Machop", "Onix"],
    },
    {
        "nombre": "Central de Energía",
        "niveles": (18, 25),
        "mensaje": "\n⚡ Las chispas saltan por la abandonada Central de Energía...\n",
        "pool": ["Pikachu", "Magnemite", "Voltorb", "Electabuzz", "Electrode", "Magneton"],
    },
    {
        "nombre": "Torre Pokémon",
        "niveles": (18, 25),
        "mensaje": "\n👻 Un escalofrío te recorre al subir por la Torre Pokémon...\n",
        "pool": ["Gastly", "Haunter", "Cubone", "Drowzee"],
    },
    {
        "nombre": "Mansión Pokémon",
        "niveles": (22, 30),
        "mensaje": "\n🔥 Recorres las ruinas calcinadas de la Mansión Pokémon...\n",
        "pool": ["Growlithe", "Vulpix", "Koffing", "Grimer", "Ponyta", "Magmar", "Weezing", "Muk"],
    },
    {
        "nombre": "Camino Victoria (cueva)",
        "niveles": (30, 38),
        "mensaje": "\n⛰️ Subes el peligroso Camino Victoria...\n",
        "pool": ["Machoke", "Golem", "Golbat", "Onix", "Marowak", "Arbok", "Primeape", "Dugtrio"],
    },
    {
        "nombre": "Meseta Índigo (Liga Pokémon)",
        "niveles": (38, 45),
        "mensaje": "\n🏆 ¡Llegando a la Meseta épica de la Liga Pokémon!\n",
        "pool": [
            "Charizard", "Blastoise", "Venusaur", "Arcanine", "Alakazam", "Gengar", "Machamp",
            "Gyarados", "Dragonite", "Rhydon", "Nidoking", "Nidoqueen", "Starmie", "Lapras",
            "Ninetales", "Snorlax",
        ],
    },
]