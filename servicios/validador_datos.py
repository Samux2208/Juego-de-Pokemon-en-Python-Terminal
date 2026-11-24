'''Validador de integridad para los datos y catálogos del juego.

Comprueba que las tablas de tipos, especies de Pokémon, movimientos, rutas
y evoluciones sean coherentes entre sí antes de iniciar la partida.
'''

from config import INICIALES
from datos.tipos_evoluciones import (
    TIPOS,
    TABLA_TIPOS,
    CLAVES_STATS,
    EVOLUCIONES_NIVEL,
    EVOLUCIONES_OBJETO,
)
from servicios.catalogos import (
    DICCIONARIO_MOVIMIENTOS,
    DICCIONARIO_POKEMON,
    TABLA_RATIOS,
)
from mundo.rutas import RUTAS


def validar_datos() -> None:
    '''Ejecuta todas las validaciones de integridad de datos del juego.

    Centraliza las comprobaciones de tipos, Pokédex, rutas y evoluciones
    para detectar errores en los catálogos desde el arranque.

    Raises:
        ValueError: Si algún dato o referencia entre catálogos no es válido.
    '''
    _validar_tipos()
    _validar_pokedex()
    _validar_rutas()
    _validar_evoluciones()


# ============================================================
# FUNCIONES INTERNAS DE VALIDACIÓN
# ============================================================

def _validar_tipos() -> None:
    '''Valida que los tipos presentes en TABLA_TIPOS existan en TIPOS.

    Revisa tanto los tipos atacantes como los tipos defensores registrados
    en la tabla de efectividades[cite: 1, 4].

    Raises:
        ValueError: Si se encuentra algún tipo fuera de TIPOS[cite: 4].
    '''
    for tipo_ataque, defensores in TABLA_TIPOS.items():
        if tipo_ataque not in TIPOS:
            raise ValueError(
                f"Tipo de ataque inválido en TABLA_TIPOS: '{tipo_ataque}'."
            )
        for tipo_defensor in defensores:
            if tipo_defensor not in TIPOS:
                raise ValueError(
                    f"Tipo defensor inválido '{tipo_defensor}' "
                    f"bajo ataque '{tipo_ataque}'."
                )


def _validar_pokedex() -> None:
    '''Valida la integridad de las especies cargadas en DICCIONARIO_POKEMON.

    Comprueba la cantidad de especies de Kanto, la validez de sus tipos,
    las seis estadísticas base, los movimientos aprendibles, el learnset
    y la correspondencia con TABLA_RATIOS.

    Raises:
        ValueError: Si falta información o hay referencias inválidas en alguna especie.
    '''
    if len(DICCIONARIO_POKEMON) != 151:
        raise ValueError(
            f"Se esperaban 151 especies de Kanto y se cargaron {len(DICCIONARIO_POKEMON)}."
        )

    for nombre, datos in DICCIONARIO_POKEMON.items():
        tipos = datos.get("tipos", [])
        if not 1 <= len(tipos) <= 2:
            raise ValueError(
                f"{nombre} debe tener 1 o 2 tipos (tiene {len(tipos)})."
            )
        for tipo in tipos:
            if tipo not in TIPOS:
                raise ValueError(f"{nombre} tiene un tipo inválido: '{tipo}'.")

        stats = datos.get("stats_base", {})
        if set(stats.keys()) != set(CLAVES_STATS):
            raise ValueError(
                f"{nombre} no tiene las 6 estadísticas base oficiales."
            )

        for mov in datos.get("movimientos", []):
            if mov not in DICCIONARIO_MOVIMIENTOS:
                raise ValueError(
                    f"{nombre} referencia un movimiento inexistente: '{mov}'."
                )

        for entrada in datos.get("learnset", []):
            mov_nivel = entrada.get("movimiento")
            if mov_nivel not in DICCIONARIO_MOVIMIENTOS:
                raise ValueError(
                    f"{nombre} tiene un movimiento inválido en su learnset: '{mov_nivel}'."
                )

    if set(TABLA_RATIOS.keys()) != set(DICCIONARIO_POKEMON.keys()):
        raise ValueError(
            "Desajuste entre las especies de la Pokédex y TABLA_RATIOS."
        )


def _validar_rutas() -> None:
    '''Valida que todas las especies en las rutas existan en la Pokédex.

    Recorre cada ruta definida en RUTAS y verifica que cada especie del
    pool salvaje esté presente en DICCIONARIO_POKEMON.

    Raises:
        ValueError: Si alguna ruta contiene una especie inexistente.
    '''
    for ruta in RUTAS:
        for especie in ruta.get("pool", []):
            if especie not in DICCIONARIO_POKEMON:
                raise ValueError(
                    f"La ruta '{ruta.get('nombre', 'Sin nombre')}' "
                    f"incluye una especie inexistente: '{especie}'."
                )


def _validar_evoluciones() -> None:
    '''Valida que iniciales y cadenas evolutivas apunten a especies válidas.

    Comprueba los Pokémon iniciales configurados, las evoluciones por nivel
    y las evoluciones mediante objetos o piedras evolutivas.

    Raises:
        ValueError: Si algún inicial o evolución referencia una especie inexistente.
    '''
    for inicial in INICIALES.values():
        if inicial not in DICCIONARIO_POKEMON:
            raise ValueError(f"Pokémon inicial inexistente: '{inicial}'.")

    for base, (_, evolucion) in EVOLUCIONES_NIVEL.items():
        if base not in DICCIONARIO_POKEMON or evolucion not in DICCIONARIO_POKEMON:
            raise ValueError(
                f"Evolución por nivel inválida: '{base}' -> '{evolucion}'."
            )

    for piedra, pares in EVOLUCIONES_OBJETO.items():
        for base, evolucion in pares.items():
            if base not in DICCIONARIO_POKEMON or evolucion not in DICCIONARIO_POKEMON:
                raise ValueError(
                    f"Evolución con '{piedra}' inválida: '{base}' -> '{evolucion}'."
                )