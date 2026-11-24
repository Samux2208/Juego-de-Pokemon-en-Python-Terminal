import random
import copy
from datos.tipos_evoluciones import TABLA_TIPOS, CLAVES_STATS
from servicios.catalogos import DICCIONARIO_MOVIMIENTOS, DICCIONARIO_POKEMON

# 25 Naturalezas Oficiales de Gen III: (estadistica_sube_10%, estadistica_baja_10%)
NATURALEZAS = {
    "Fuerte": (None, None), "Osada": ("defensa", "ataque"), "Modesta": ("atq_esp", "ataque"),
    "Serena": ("def_esp", "ataque"), "Miedosa": ("velocidad", "ataque"),
    "Huraña": ("ataque", "defensa"), "Dócil": (None, None), "Afable": ("atq_esp", "defensa"),
    "Amable": ("def_esp", "defensa"), "Activa": ("velocidad", "defensa"),
    "Firme": ("ataque", "atq_esp"), "Agitada": ("defensa", "atq_esp"), "Tímida": (None, None),
    "Cauta": ("def_esp", "atq_esp"), "Alegre": ("velocidad", "atq_esp"),
    "Pícara": ("ataque", "def_esp"), "Floja": ("defensa", "def_esp"), "Alocada": ("atq_esp", "def_esp"),
    "Rara": (None, None), "Ingenua": ("velocidad", "def_esp"),
    "Audaz": ("ataque", "velocidad"), "Plácida": ("defensa", "velocidad"),
    "Mansa": ("atq_esp", "velocidad"), "Grosera": ("def_esp", "velocidad"), "Seria": (None, None),
}


def naturaleza_aleatoria():
    return random.choice(list(NATURALEZAS.keys()))


def multiplicador_etapa(etapa, es_precision_evasion=False):
    '''Calcula el multiplicador oficial por etapas de cambio en combate (-6 a +6).'''
    etapa = max(-6, min(6, etapa))
    base = 3 if es_precision_evasion else 2
    if etapa >= 0:
        return (base + etapa) / base
    return base / (base + abs(etapa))

# == CÁLCULO DE EFECTIVIDAD DE TIPOS =========================
# efectividad_tipos() | Obtiene el multiplicador de daño elemental (0x a 4x).
# ============================================================

def efectividad_tipos(tipo_movimiento, tipos_defensor):
    '''Multiplicador total de un movimiento contra uno o dos tipos defensores.'''
    mult_total = 1.0
    for tipo_def in tipos_defensor:
        # Busca el multiplicador del tipo defensor en la tabla; si no existe, usa 1.0 (neutro)
        mult_total *= TABLA_TIPOS.get(tipo_movimiento, {}).get(tipo_def, 1.0)
    return mult_total

# == FUNCIONES DE UTILIDAD Y VISUALIZACIÓN ===================
# exp_para_nivel()        | Calcula la experiencia total requerida para un nivel.
# calcular_estadisticas() | Escala los stats base de la especie al nivel actual.
# generar_movimientos()   | Asigna los últimos 4 ataques desbloqueados por nivel.
# ============================================================

def exp_para_nivel(nivel):
    '''Devuelve la experiencia acumulada necesaria para alcanzar un nivel.'''
    return int((nivel ** 3) * 0.8)


def calcular_estadisticas(base, nivel, naturaleza="Fuerte", ivs=None, evs=None):
    '''Fórmula oficial de Gen III para calcular PS y las 5 estadísticas de combate.'''
    ivs = ivs or {k: 15 for k in CLAVES_STATS}
    evs = evs or {k: 0 for k in CLAVES_STATS}
    sube, baja = NATURALEZAS.get(naturaleza, (None, None))
    stats = {}

    # Calculamos primero todas las estadísticas estándar
    # (Ataque, Defensa, Ataque Especial, Defensa Especial, Velocidad)
    for clave in CLAVES_STATS:
        if clave == "vida":
            stats["vida"] = (((2 * base["vida"] + ivs["vida"] + (evs["vida"] // 4)) * nivel) // 100) + nivel + 10
        else:
            val = (((2 * base[clave] + ivs[clave] + (evs[clave] // 4)) * nivel) // 100) + 5
            if clave == sube:
                val = int(val * 1.1)
            elif clave == baja:
                val = int(val * 0.9)
            stats[clave] = val
    return stats


def generar_movimientos(especie, nivel):
    '''Asigna los últimos 4 movimientos aprendidos hasta el nivel actual según Rojo Fuego.'''
    # OBTENEMOS TODOS LOS MOVIMIENTOS APRENDIBLES POR LA ESPECIE
    datos = DICCIONARIO_POKEMON[especie]
    movimientos_por_nivel = datos.get("learnset", [])

    if movimientos_por_nivel:
        aprendidos = [
            item["movimiento"] for item in movimientos_por_nivel
            if item["nivel"] <= nivel and item["movimiento"] in DICCIONARIO_MOVIMIENTOS
        ]
        unicos = list(dict.fromkeys(aprendidos))
        if not unicos:
            unicos = [movimientos_por_nivel[0]["movimiento"]]
        # Conservamos solo los 4 más recientes
        ultimos_cuatro_nombres = unicos[-4:]
    else:
        lista_completa = datos.get("movimientos", [])
        # Empieza con 2 movimientos y desbloquea uno nuevo cada 7 niveles
        ultimos_cuatro_nombres = lista_completa[:max(1, 2 + nivel // 7)][-4:]

    # Convertimos los nombres en instancias reales de la clase Movimiento
    return [copy.copy(DICCIONARIO_MOVIMIENTOS[nombre]) for nombre in ultimos_cuatro_nombres]