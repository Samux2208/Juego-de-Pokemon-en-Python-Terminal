# ============================================================
# REGLAS DE GEN III: TIPOS, EFECTIVIDADES Y EVOLUCIONES
# ============================================================

# 17 tipos elementales de la Tercera Generación (claves internas sin tildes)
TIPOS = (
    "normal", "fuego", "agua", "electrico", "planta", "hielo", "lucha",
    "veneno", "tierra", "volador", "psiquico", "bicho", "roca", "fantasma",
    "dragon", "siniestro", "acero",
)

# Nombres visibles con tilde y capitalización correcta
NOMBRES_TIPO = {
    "electrico": "Eléctrico",
    "psiquico": "Psíquico",
    "dragon": "Dragón",
}

# Iconos de consola por tipo
ICONOS_TIPO = {
    "normal": "⚪",
    "fuego": "🔥",
    "agua": "💧",
    "electrico": "⚡",
    "planta": "🌿",
    "hielo": "❄️",
    "lucha": "🥊",
    "veneno": "☠️",
    "tierra": "🏔️",
    "volador": "🪽",
    "psiquico": "🔮",
    "bicho": "🐛",
    "roca": "🪨",
    "fantasma": "👻",
    "dragon": "🐉",
    "siniestro": "🌑",
    "acero": "⚙️",
}

# Etiquetas de categoría para mostrar en consola
ICONOS_CATEGORIA = {
    "fisico": "💥 Fís",
    "especial": "✨ Esp",
    "estado": "🌀 Est",
}

# En Gen III, la categoría física o especial depende del tipo del movimiento
TIPOS_ESPECIALES = {
    "fuego", "agua", "planta", "electrico",
    "hielo", "psiquico", "dragon", "siniestro",
}

# Orden estándar de las 6 estadísticas base
CLAVES_STATS = ("vida", "ataque", "defensa", "atq_esp", "def_esp", "velocidad")


def nombre_tipo(tipo: str, emoji: bool = True) -> str:
    '''Devuelve el nombre del tipo formateado y, opcionalmente, con su emoji.'''
    texto = NOMBRES_TIPO.get(tipo, tipo.capitalize())
    if emoji:
        return f"{ICONOS_TIPO.get(tipo, '🔹')} {texto}"
    return texto


# Tabla base de efectividades: atacante -> {multiplicador: (defensores...)}
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

# Consulta directa: TABLA_TIPOS[atacante].get(defensor, 1.0)
TABLA_TIPOS = {
    atacante: {
        defensor: multiplicador
        for multiplicador, defensores in grupos.items()
        for defensor in defensores
    }
    for atacante, grupos in _EFECTIVIDADES.items()
}

# Evolución por nivel: especie -> (nivel_requerido, evolucion)
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

# Evolución por objeto: objeto -> {especie_actual: evolucion}
EVOLUCIONES_OBJETO = {
    "Piedra Fuego": {
        "Vulpix": "Ninetales",
        "Growlithe": "Arcanine",
        "Eevee": "Flareon",
    },
    "Piedra Agua": {
        "Poliwhirl": "Poliwrath",
        "Shellder": "Cloyster",
        "Staryu": "Starmie",
        "Eevee": "Vaporeon",
    },
    "Piedra Trueno": {
        "Pikachu": "Raichu",
        "Eevee": "Jolteon",
    },
    "Piedra Hoja": {
        "Gloom": "Vileplume",
        "Weepinbell": "Victreebel",
        "Exeggcute": "Exeggutor",
    },
    "Piedra Lunar": {
        "Nidorina": "Nidoqueen",
        "Nidorino": "Nidoking",
        "Clefairy": "Clefable",
        "Jigglypuff": "Wigglytuff",
    },
}