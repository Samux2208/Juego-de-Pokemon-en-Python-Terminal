# ==================================================
# ARCHIVO: sistemas/efectos.py
# ==================================================
import random

# Diccionario de etiquetas y nombres legibles para los 5 estados principales
ESTADOS_INFO = {
    "burn":      {"codigo": "🔥 QUEM", "nombre": "quemado"},
    "paralysis": {"codigo": "⚡ PAR",  "nombre": "paralizado"},
    "poison":    {"codigo": "☠️ ENV",  "nombre": "envenenado"},
    "sleep":     {"codigo": "💤 DOR",  "nombre": "dormido"},
    "freeze":    {"codigo": "❄️ CONG", "nombre": "congelado"},
}

NOMBRES_STATS_ES = {
    "ataque": "Ataque",
    "defensa": "Defensa",
    "atq_esp": "Ataque Especial",
    "def_esp": "Defensa Especial",
    "velocidad": "Velocidad",
    "precision": "Precisión",
    "evasion": "Evasión",
}


def evaluar_estado_pre_turno(pokemon):
    '''Evalúa antes de atacar si un estado alterado o confusión impide moverse.

    Retorna:
        tuple[bool, list[str]]: (puede_atacar, lista_de_mensajes_narrativos)
    '''
    mensajes = []
    estado = pokemon.estado_alterado

    # 1) Sueño (dura de 1 a 3 turnos en Gen III)
    if estado == "sleep":
        if pokemon.turnos_estado > 0:
            pokemon.turnos_estado -= 1
            mensajes.append(f"💤 {pokemon.nombre_visible} está dormido como un tronco.")
            return False, mensajes
        pokemon.estado_alterado = None
        mensajes.append(f"☀️ ¡{pokemon.nombre_visible} se despertó!")

    # 2) Congelación (20% de probabilidad de descongelarse al intentar moverse)
    elif estado == "freeze":
        if random.random() < 0.20:
            pokemon.estado_alterado = None
            mensajes.append(f"🔥 ¡{pokemon.nombre_visible} se descongeló!")
        else:
            mensajes.append(f"❄️ {pokemon.nombre_visible} está congelado y no puede moverse.")
            return False, mensajes

    # 3) Parálisis (25% de probabilidad de parálisis total en el turno)
    elif estado == "paralysis":
        if random.random() < 0.25:
            mensajes.append(f"⚡ ¡{pokemon.nombre_visible} está paralizado y no se puede mover!")
            return False, mensajes

    # 4) Confusión (estado volátil: dura 2-5 turnos, 50% de autolesionarse)
    if pokemon.confuso:
        if pokemon.turnos_confusion <= 0:
            pokemon.confuso = False
            mensajes.append(f"💫 ¡{pokemon.nombre_visible} ya no está confuso!")
        else:
            pokemon.turnos_confusion -= 1
            mensajes.append(f"💫 ¡{pokemon.nombre_visible} está confuso!")
            if random.random() < 0.50:
                # Fórmula oficial de daño por confusión: ataque físico de potencia 40 contra sí mismo
                factor_nivel = (2 * pokemon.nivel) // 5 + 2
                danio_auto = max(
                    1,
                    ((factor_nivel * pokemon.ataque * 40) // max(1, pokemon.defensa)) // 50 + 2
                )
                pokemon.recibir_danio(danio_auto)
                mensajes.append(f"💥 ¡Está tan confuso que se hirió a sí mismo! (-{danio_auto} PS)")
                return False, mensajes

    return True, mensajes


def aplicar_efectos_movimiento(atacante, defensor, movimiento):
    '''Aplica cambios de estadísticas y estados alterados tras impactar un movimiento.

    Retorna:
        list[str]: Lista de mensajes narrativos con los efectos ocurridos.
    '''
    mensajes = []

    # Modificadores de estadísticas (-6 a +6 niveles)
    if movimiento.cambios_stats:
        prob_stat = (
            movimiento.prob_stat
            if movimiento.prob_stat > 0
            else (100 if movimiento.categoria == "estado" else 0)
        )
        if random.randint(1, 100) <= prob_stat:
            objetivo = atacante if movimiento.objetivo == "user" else defensor
            for cambio in movimiento.cambios_stats:
                stat = cambio["stat"]
                delta = cambio["niveles"]
                variacion_real = objetivo.modificar_estado(stat, delta)
                nombre_stat = NOMBRES_STATS_ES.get(stat, stat)

                if variacion_real == 0:
                    tope = "subir más" if delta > 0 else "bajar más"
                    mensajes.append(f"🚫 ¡{nombre_stat} de {objetivo.nombre_visible} no puede {tope}!")
                else:
                    if delta > 0:
                        emoji = "⏫" if abs(delta) >= 2 else "🔺"
                        accion = "subió"
                    else:
                        emoji = "⏬" if abs(delta) >= 2 else "🔻"
                        accion = "bajó"

                    grado = " mucho" if abs(delta) >= 2 else ""
                    mensajes.append(f"{emoji} ¡{nombre_stat} de {objetivo.nombre_visible} {accion}{grado}!")

    # Estados alterados (Burn, Paralysis, Poison, Sleep, Freeze, Confusion)
    efecto = movimiento.efecto_estado
    if efecto and efecto != "none":
        prob = movimiento.prob_estado if movimiento.prob_estado > 0 else (100 if movimiento.categoria == "estado" else 0)
        if random.randint(1, 100) <= prob:
            if efecto == "confusion":
                if not defensor.confuso:
                    defensor.confuso = True
                    defensor.turnos_confusion = random.randint(2, 5)
                    mensajes.append(f"💫 ¡{defensor.nombre_visible} está confuso!")
                elif movimiento.categoria == "estado":
                    mensajes.append(f"⚠️ ¡{defensor.nombre_visible} ya está confuso!")
            elif efecto in ESTADOS_INFO:
                if defensor.aplicar_estado(efecto, movimiento.tipo):
                    mensajes.append(f"✨ ¡{defensor.nombre_visible} quedó {ESTADOS_INFO[efecto]['nombre']}!")
                elif movimiento.categoria == "estado":
                    mensajes.append(f"⚠️ No afecta a {defensor.nombre_visible}...")

    return mensajes


def aplicar_danio_fin_turno(pokemon):
    '''Aplica el daño residual al final de cada ronda por Quemadura o Veneno (1/8 de PS máx).'''
    if pokemon.salud_actual <= 0:
        return []

    if pokemon.estado_alterado == "burn":
        danio = max(1, pokemon.salud_maxima // 8)
        pokemon.recibir_danio(danio)
        return [f"🔥 {pokemon.nombre_visible} se resiente de su quemadura (-{danio} PS)."]

    if pokemon.estado_alterado == "poison":
        danio = max(1, pokemon.salud_maxima // 8)
        pokemon.recibir_danio(danio)
        return [f"☠️ El veneno resta PS a {pokemon.nombre_visible} (-{danio} PS)."]

    return []