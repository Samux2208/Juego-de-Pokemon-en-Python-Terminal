# ==================================================
# ARCHIVO: servicios/validador_datos.py
# ==================================================
from config import (
    TIPOS,
    _EFECTIVIDADES,
    _CLAVES_STATS,
    INICIALES,
    EVOLUCIONES_NIVEL,
    EVOLUCIONES_OBJETO,
)
from servicios.repositorio import (
    DICCIONARIO_MOVIMIENTOS,
    DICCIONARIO_POKEMON,
    TABLA_RATIOS,
    RUTAS,
)


def validar_datos():
    """Punto de entrada público: ejecuta todas las comprobaciones de integridad Gen III."""
    _validar_tipos()
    _validar_pokedex()
    _validar_rutas()
    _validar_evoluciones()


# ============================================================
# FUNCIONES INTERNAS PROTEGIDAS (USO EXCLUSIVO DEL MÓDULO)
# ============================================================

def _validar_tipos():
    """Verifica que todos los tipos y multiplicadores de la tabla elemental existan."""
    for tipo_ataque, grupos in _EFECTIVIDADES.items():
        if tipo_ataque not in TIPOS:
            raise ValueError(f"Tipo de ataque inválido en tabla elemental: '{tipo_ataque}'.")
        for defensores in grupos.values():
            for tipo_defensor in defensores:
                if tipo_defensor not in TIPOS:
                    raise ValueError(
                        f"Tipo defensor inválido '{tipo_defensor}' bajo ataque '{tipo_ataque}'."
                    )


def _validar_pokedex():
    """Verifica las 151 especies de Kanto, sus stats base, movimientos, learnset y ratios."""
    if len(DICCIONARIO_POKEMON) != 151:
        raise ValueError(
            f"Se esperaban 151 especies de Kanto y se cargaron {len(DICCIONARIO_POKEMON)}."
        )

    for nombre, datos in DICCIONARIO_POKEMON.items():
        tipos = datos.get("tipos", [])
        if not 1 <= len(tipos) <= 2:
            raise ValueError(f"{nombre} debe tener 1 o 2 tipos (tiene {len(tipos)}).")
        for tipo in tipos:
            if tipo not in TIPOS:
                raise ValueError(f"{nombre} tiene un tipo inválido: '{tipo}'.")

        stats = datos.get("stats_base", {})
        if set(stats.keys()) != set(_CLAVES_STATS):
            raise ValueError(f"{nombre} no tiene las 6 estadísticas base oficiales.")

        for mov in datos.get("movimientos", []):
            if mov not in DICCIONARIO_MOVIMIENTOS:
                raise ValueError(f"{nombre} referencia un movimiento inexistente: '{mov}'.")

        for entrada in datos.get("learnset", []):
            mov_nivel = entrada.get("movimiento")
            if mov_nivel not in DICCIONARIO_MOVIMIENTOS:
                raise ValueError(
                    f"{nombre} tiene un movimiento inválido en su learnset: '{mov_nivel}'."
                )

    if set(TABLA_RATIOS.keys()) != set(DICCIONARIO_POKEMON.keys()):
        raise ValueError("Desajuste entre las especies de la Pokédex y TABLA_RATIOS.")


def _validar_rutas():
    """Verifica que todas las especies salvajes configuradas en las rutas existan."""
    for ruta in RUTAS:
        for especie in ruta.get("pool", []):
            if especie not in DICCIONARIO_POKEMON:
                raise ValueError(
                    f"La ruta '{ruta.get('nombre', 'Sin nombre')}' incluye una especie inexistente: '{especie}'."
                )


def _validar_evoluciones():
    """Verifica que los iniciales y todas las cadenas evolutivas apunten a especies válidas."""
    for inicial in INICIALES.values():
        if inicial not in DICCIONARIO_POKEMON:
            raise ValueError(f"Pokémon inicial inexistente: '{inicial}'.")

    for base, (_, evolucion) in EVOLUCIONES_NIVEL.items():
        if base not in DICCIONARIO_POKEMON or evolucion not in DICCIONARIO_POKEMON:
            raise ValueError(f"Evolución por nivel inválida: '{base}' -> '{evolucion}'.")

    for piedra, pares in EVOLUCIONES_OBJETO.items():
        for base, evolucion in pares.items():
            if base not in DICCIONARIO_POKEMON or evolucion not in DICCIONARIO_POKEMON:
                raise ValueError(
                    f"Evolución con '{piedra}' inválida: '{base}' -> '{evolucion}'."
                )