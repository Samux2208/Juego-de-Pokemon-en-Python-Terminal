'''Registro de migraciones del formato de guardado para Pokémon Gen III.

Cada migración transforma un diccionario de la versión N a la N+1 como una
función pura (no accede a disco ni muta el diccionario original recibido).

Para añadir una versión futura (ejemplo, v3):
  1. Incrementar `VERSION_ACTUAL` a 3 (y alinear `VERSION` en `config.py`).
  2. Escribir `_migrar_v2_a_v3(datos)` y registrarla en `MIGRACIONES` como `2: _migrar_v2_a_v3`.
  3. Actualizar `validacion.py` y añadir pruebas en `tests/test_guardado.py`.
'''

import copy

# Versión más reciente del esquema de partida soportada por este módulo
VERSION_ACTUAL: int = 2

# Clases válidas de Pokémon en el modelo multinivel actual
_CLASES_POKEMON_VALIDAS = {
    "Pokemon",
    "PokemonCapturable",
    "PokemonSalvaje",
    "PokemonAtrapado",
}


def _normalizar_entrada_pokemon(entrada: dict) -> dict:
    '''Normaliza la `"clase"` de un diccionario de Pokémon al migrar a v2.

    Mantiene compatibilidad con partidas antiguas donde el Pokémon venía sin
    `"clase"` o usaba `"PokemonJugador"` antes de la jerarquía
    `Pokemon` -> `PokemonCapturable` -> `PokemonSalvaje` / `PokemonAtrapado`.

    Args:
        entrada: Diccionario serializado de un Pokémon.

    Returns:
        dict: Copia del diccionario con `"clase"` normalizada si era un `dict`.
    '''
    if not isinstance(entrada, dict):
        return entrada

    poke = dict(entrada)
    clase_actual = poke.get("clase")

    if clase_actual == "PokemonJugador":
        poke["clase"] = "PokemonAtrapado"
    elif clase_actual not in _CLASES_POKEMON_VALIDAS:
        # Si tiene datos de entrenador o apodo, corresponde a un Pokémon atrapado
        if "apodo" in poke or "entrenador" in poke:
            poke["clase"] = "PokemonAtrapado"
        else:
            poke["clase"] = "Pokemon"

    return poke


def _migrar_v1_a_v2(datos: dict) -> dict:
    '''Transforma una partida de v1 (formato plano) a v2 (secciones estructuradas).

    Cambios estructurales:
      - `'nombre_entrenador'` pasa a `'entrenador': {'nombre': ...}`.
      - Se añade la sección `'progreso'` con valores iniciales de Kanto.
      - Se normaliza la `'clase'` de los Pokémon en `'equipo'` y `'pc'`.
      - Se construye `'pokedex'` con `'vistos'` y `'capturados'` a partir de las
        especies presentes en el equipo y el PC.

    Args:
        datos: Diccionario de partida en versión 1.

    Returns:
        dict: Nuevo diccionario con el formato de versión 2.
    '''
    equipo_raw = datos.get("equipo") if isinstance(datos.get("equipo"), dict) else {}
    lista_equipo = [
        _normalizar_entrada_pokemon(p) for p in equipo_raw.get("pokemon", [])
    ]
    lista_pc = [
        _normalizar_entrada_pokemon(p) for p in equipo_raw.get("pc", [])
    ]

    equipo_migrado = {
        "pokemon": lista_equipo,
        "pc": lista_pc,
    }

    # Recolecta especies únicas presentes en el equipo activo y el PC para la Pokédex
    especies: list[str] = []
    for p in lista_equipo + lista_pc:
        if isinstance(p, dict) and isinstance(p.get("nombre"), str):
            especie = p["nombre"]
            if especie not in especies:
                especies.append(especie)

    mochila_raw = datos.get("mochila") if isinstance(datos.get("mochila"), dict) else {}

    return {
        "version": 2,
        "entrenador": {"nombre": datos.get("nombre_entrenador")},
        "progreso": {
            "ubicacion_actual": "Pueblo Paleta",
            "insignias": [],
            "eventos_completados": [],
        },
        "equipo": equipo_migrado,
        "mochila": mochila_raw,
        # En v1 no existía Pokédex; se registran como vistas y capturadas las especies poseídas
        "pokedex": {
            "vistos": list(especies),
            "capturados": list(especies),
        },
    }


# Mapa escalonado de migraciones: version_origen -> funcion_migracion
MIGRACIONES: dict[int, callable] = {
    1: _migrar_v1_a_v2,
}


def migrar(datos: dict) -> dict:
    '''Actualiza un diccionario de partida paso a paso hasta `VERSION_ACTUAL`.

    No modifica el diccionario original (`datos`); trabaja sobre una copia profunda.

    Args:
        datos: Diccionario leído desde el archivo JSON de partida.

    Returns:
        dict: Diccionario migrado y listo para validar en `VERSION_ACTUAL`.

    Raises:
        ValueError: Si `datos` no es un `dict`, la versión es inválida, supera
            `VERSION_ACTUAL` o falta una función de migración en la cadena.
    '''
    # 1. La raíz del JSON debe ser un objeto/diccionario
    if not isinstance(datos, dict):
        raise ValueError("La partida no es un objeto JSON.")

    version = datos.get("version")

    # 2. La versión debe ser un entero >= 1 (se excluyen bool porque True == 1 en Python)
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError(f"Versión de guardado inválida: {version!r}")

    # 3. Evita cargar partidas creadas en versiones superiores del juego
    if version > VERSION_ACTUAL:
        raise ValueError(
            f"La partida es de una versión más nueva ({version}) que la soportada "
            f"({VERSION_ACTUAL})."
        )

    # 4. Copia profunda para preservar el diccionario original ante cualquier fallo
    datos_migrados = copy.deepcopy(datos)

    # 5. Avanza versión por versión hasta alcanzar VERSION_ACTUAL
    while datos_migrados["version"] < VERSION_ACTUAL:
        version_en_curso = datos_migrados["version"]
        paso = MIGRACIONES.get(version_en_curso)

        if paso is None:
            raise ValueError(
                f"No existe migración desde la versión {version_en_curso}."
            )

        datos_migrados = paso(datos_migrados)

    return datos_migrados