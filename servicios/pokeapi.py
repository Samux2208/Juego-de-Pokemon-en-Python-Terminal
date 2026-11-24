'''Cliente HTTP para descargar y adaptar datos de PokéAPI a Gen III.

Obtiene especies de Kanto, sus habilidades en español (tipo Mar Llamas,
Espesura, Torrente, etc.), descripciones en español y movimientos
compatibles con Pokémon Rojo Fuego y Verde Hoja.
'''

import json
import time
import urllib.error
import urllib.request
from datos.tipos_evoluciones import TIPOS_ESPECIALES

BASE_URL = "https://pokeapi.co/api/v2"

MAPA_TIPOS_ES = {
    "normal": "normal", "fire": "fuego", "water": "agua",
    "electric": "electrico", "grass": "planta", "ice": "hielo",
    "fighting": "lucha", "poison": "veneno", "ground": "tierra",
    "flying": "volador", "psychic": "psiquico", "bug": "bicho",
    "rock": "roca", "ghost": "fantasma", "dragon": "dragon",
    "dark": "siniestro", "steel": "acero",
}

MAPA_STATS = {
    "hp": "vida",
    "attack": "ataque",
    "defense": "defensa",
    "special-attack": "atq_esp",
    "special-defense": "def_esp",
    "speed": "velocidad",
    "accuracy": "precision",
    "evasion": "evasion",
}

# Grupos de versiones posteriores a Gen III (ordenados del más antiguo al más reciente)
VERSIONES_POST_GEN3 = (
    "diamond-pearl", "platinum", "heartgold-soulsilver",
    "black-white", "black-2-white-2",
    "x-y", "omega-ruby-alpha-sapphire",
    "sun-moon", "ultra-sun-ultra-moon",
    "sword-shield", "scarlet-violet",
)

# Tabla oficial de experiencia base (exp_base) de los 151 Pokémon en Rojo Fuego / Verde Hoja
EXP_BASE_GEN3 = {
    1: 64, 2: 141, 3: 208, 4: 65, 5: 142, 6: 209, 7: 66, 8: 143, 9: 210,
    10: 53, 11: 72, 12: 160, 13: 52, 14: 71, 15: 159, 16: 55, 17: 113, 18: 172,
    19: 57, 20: 116, 21: 58, 22: 162, 23: 62, 24: 147, 25: 82, 26: 122,
    27: 93, 28: 163, 29: 59, 30: 117, 31: 194, 32: 60, 33: 118, 34: 195,
    35: 68, 36: 129, 37: 63, 38: 178, 39: 76, 40: 109, 41: 54, 42: 171,
    43: 78, 44: 132, 45: 184, 46: 70, 47: 128, 48: 75, 49: 138, 50: 81,
    51: 153, 52: 69, 53: 148, 54: 80, 55: 174, 56: 74, 57: 149, 58: 91,
    59: 213, 60: 77, 61: 131, 62: 185, 63: 73, 64: 145, 65: 186, 66: 75,
    67: 146, 68: 193, 69: 84, 70: 151, 71: 191, 72: 105, 73: 205, 74: 86,
    75: 134, 76: 177, 77: 152, 78: 192, 79: 99, 80: 164, 81: 89, 82: 161,
    83: 94, 84: 96, 85: 158, 86: 100, 87: 176, 88: 90, 89: 157, 90: 97,
    91: 203, 92: 95, 93: 126, 94: 190, 95: 108, 96: 102, 97: 165, 98: 115,
    99: 206, 100: 103, 101: 150, 102: 98, 103: 212, 104: 87, 105: 124,
    106: 139, 107: 140, 108: 127, 109: 114, 110: 173, 111: 135, 112: 204,
    113: 255, 114: 166, 115: 175, 116: 83, 117: 155, 118: 111, 119: 170,
    120: 106, 121: 207, 122: 136, 123: 187, 124: 137, 125: 156, 126: 167,
    127: 200, 128: 211, 129: 20, 130: 214, 131: 219, 132: 61, 133: 92,
    134: 196, 135: 197, 136: 198, 137: 130, 138: 120, 139: 199, 140: 119,
    141: 201, 142: 202, 143: 154, 144: 215, 145: 216, 146: 217, 147: 67,
    148: 144, 149: 218, 150: 220, 151: 64,
}


def _get_json(url: str, reintentos: int = 4) -> dict:
    '''Realiza una petición GET a PokéAPI y devuelve el JSON con reintentos.'''
    req = urllib.request.Request(url, headers={"User-Agent": "POOkemon-Gen3/1.0"})
    for intento in range(1, reintentos + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (TimeoutError, urllib.error.URLError):
            if intento == reintentos:
                raise
            print(f" ⏳ Conexión lenta en {url} (intento {intento}/{reintentos}), reintentando...")
            time.sleep(2 * intento)


def obtener_nombre_es(nombres_lista: list[dict], fallback: str) -> str:
    '''Devuelve el nombre en español de una lista `names` o un respaldo.'''
    for entrada in nombres_lista:
        if entrada["language"]["name"] == "es":
            return entrada["name"]
    return fallback.capitalize()


def _limpiar_texto_es(flavor_entries: list[dict]) -> str:
    '''Extrae una descripción limpia en español, priorizando Rojo Fuego / Verde Hoja.'''
    respaldo = ""
    for entry in flavor_entries:
        if entry["language"]["name"] == "es":
            texto = " ".join(entry["flavor_text"].replace("\f", " ").split())
            version = (
                entry.get("version", {}).get("name")
                or entry.get("version_group", {}).get("name")
            )
            if version in ("firered", "leafgreen", "firered-leafgreen"):
                return texto
            if not respaldo:
                respaldo = texto
    return respaldo


def _obtener_habilidad_es(url_habilidad: str, cache: dict[str, dict]) -> dict:
    '''Descarga y cachea el nombre y descripción en español de una habilidad.'''
    if url_habilidad in cache:
        return cache[url_habilidad]

    data_hab = _get_json(url_habilidad)
    nombre_es = obtener_nombre_es(data_hab["names"], data_hab["name"])
    descripcion_es = _limpiar_texto_es(data_hab.get("flavor_text_entries", []))

    habilidad = {
        "nombre": nombre_es,
        "descripcion": descripcion_es,
    }
    cache[url_habilidad] = habilidad
    return habilidad


def _extraer_habilidades_gen3(data_poke: dict, cache_habilidades: dict[str, dict]) -> list[dict]:
    '''Obtiene las habilidades normales (no ocultas) en español de un Pokémon.'''
    slots = {
        ab["slot"]: ab["ability"]["url"]
        for ab in data_poke.get("abilities", [])
        if not ab.get("is_hidden", False) and ab.get("ability")
    }

    for past in data_poke.get("past_abilities", []):
        for ab in past.get("abilities", []):
            if ab.get("is_hidden", False):
                continue
            slot = ab["slot"]
            if ab.get("ability") is None:
                slots.pop(slot, None)
            else:
                slots[slot] = ab["ability"]["url"]

    return [
        _obtener_habilidad_es(slots[slot], cache_habilidades)
        for slot in sorted(slots)
    ]


def _aplicar_valores_gen3(data_mov: dict) -> tuple[int, int, int, str]:
    '''Revierte potencia, precisión, PP y tipo de un movimiento a Gen III.'''
    potencia = data_mov["power"]
    precision = data_mov["accuracy"]
    pp = data_mov["pp"]
    tipo_en = data_mov["type"]["name"]

    past_values = data_mov.get("past_values", [])
    orden_versiones = {v: i for i, v in enumerate(VERSIONES_POST_GEN3)}
    cambios_ordenados = sorted(
        past_values,
        key=lambda pv: orden_versiones.get(pv["version_group"]["name"], 999),
        reverse=True,
    )

    for pv in cambios_ordenados:
        vg = pv["version_group"]["name"]
        if vg in orden_versiones:
            if pv.get("power") is not None:
                potencia = pv["power"]
            if pv.get("accuracy") is not None:
                precision = pv["accuracy"]
            if pv.get("pp") is not None:
                pp = pv["pp"]
            if pv.get("type") is not None:
                tipo_en = pv["type"]["name"]

    return potencia or 0, precision or 100, pp or 15, tipo_en


def descargar_pokemon_kanto(limite: int = 151) -> tuple[dict, set[str]]:
    '''Descarga los Pokémon de Kanto con habilidades y descripción en español.'''
    pokedex = {}
    movimientos_ids = set()
    cache_habilidades = {}

    for poke_id in range(1, limite + 1):
        data_poke = _get_json(f"{BASE_URL}/pokemon/{poke_id}")
        data_spec = _get_json(f"{BASE_URL}/pokemon-species/{poke_id}")

        nombre_es = obtener_nombre_es(data_spec["names"], data_poke["name"])
        tipos = [
            MAPA_TIPOS_ES[t["type"]["name"]]
            for t in data_poke["types"]
            if t["type"]["name"] in MAPA_TIPOS_ES
        ]
        if not tipos:
            tipos = ["normal"]

        stats_base = {
            MAPA_STATS[s["stat"]["name"]]: s["base_stat"]
            for s in data_poke["stats"]
        }

        habilidades = _extraer_habilidades_gen3(data_poke, cache_habilidades)

        movs_nivel = []
        for m in data_poke["moves"]:
            for detalle in m["version_group_details"]:
                if (
                    detalle["version_group"]["name"] == "firered-leafgreen"
                    and detalle["move_learn_method"]["name"] == "level-up"
                ):
                    movs_nivel.append((detalle["level_learned_at"], m["move"]["url"]))
                    movimientos_ids.add(m["move"]["url"])
                    break

        movs_nivel.sort(key=lambda x: x[0])
        descripcion = _limpiar_texto_es(data_spec.get("flavor_text_entries", []))

        pokedex[nombre_es] = {
            "id": poke_id,
            "nombre": nombre_es,
            "tipos": tipos,
            "habilidades": habilidades,
            "stats_base": stats_base,
            "exp_base": EXP_BASE_GEN3.get(poke_id, data_poke["base_experience"] or 60),
            "ratio_captura": data_spec["capture_rate"],
            "crecimiento": data_spec["growth_rate"]["name"],
            "movimientos_url": [url for _, url in movs_nivel],
            "movimientos_nivel": [(lvl, url) for lvl, url in movs_nivel],
            "descripcion": descripcion,
        }
        print(f"[{poke_id:03d}/{limite}] Descargado: {nombre_es}")
        time.sleep(.1)

    return pokedex, movimientos_ids


def descargar_movimientos(urls_movimientos: set[str]) -> tuple[dict, dict]:
    '''Descarga los movimientos con sus valores Gen III y descripción en español.'''
    catalogo_movs = {}
    mapa_url_nombre = {}

    for url in sorted(urls_movimientos):
        data_mov = _get_json(url)
        potencia, precision, pp, tipo_en = _aplicar_valores_gen3(data_mov)

        if tipo_en not in MAPA_TIPOS_ES:
            continue

        tipo_es = MAPA_TIPOS_ES[tipo_en]
        nombre_es = obtener_nombre_es(data_mov["names"], data_mov["name"])
        descripcion_es = _limpiar_texto_es(data_mov.get("flavor_text_entries", []))
        clase_dano = data_mov["damage_class"]["name"]

        if clase_dano == "status":
            categoria = "estado"
        else:
            categoria = "especial" if tipo_es in TIPOS_ESPECIALES else "fisico"

        meta = data_mov.get("meta") or {}
        estado_ailment = (meta.get("ailment") or {}).get("name", "none")
        prob_estado = meta.get("ailment_chance", 0)
        cambios_stats = [
            {"stat": MAPA_STATS[sc["stat"]["name"]], "niveles": sc["change"]}
            for sc in data_mov.get("stat_changes", [])
            if sc["stat"]["name"] in MAPA_STATS
        ]
        prob_stat = meta.get("stat_chance", 0) or (100 if cambios_stats and potencia == 0 else 0)

        if data_mov["name"] == "rapid-spin":
            cambios_stats = []
            prob_stat = 0

        catalogo_movs[nombre_es] = {
            "id": data_mov["id"],
            "nombre": nombre_es,
            "tipo": tipo_es,
            "categoria": categoria,
            "potencia": potencia,
            "precision": precision,
            "pp": pp,
            "prioridad": data_mov["priority"],
            "objetivo": data_mov["target"]["name"],
            "efecto_estado": estado_ailment,
            "prob_estado": prob_estado,
            "cambios_stats": cambios_stats,
            "prob_stat": prob_stat,
            "descripcion": descripcion_es,
        }
        mapa_url_nombre[url] = nombre_es
        print(f"Movimiento descargado: {nombre_es} ({tipo_es} | {categoria})")

    return catalogo_movs, mapa_url_nombre