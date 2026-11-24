'''Carga y construcción en memoria de los catálogos base del juego.

Lee los archivos JSON generados en `datos/` y construye las estructuras
principales de movimientos, especies de Pokémon y ratios de captura.
'''

import json
from pathlib import Path
from config import DATOS_DIR
from modelos.movimiento import Movimiento

ARCHIVO_POKEMON: Path = DATOS_DIR / "pokemon_gen3.json"
ARCHIVO_MOVIMIENTOS: Path = DATOS_DIR / "movimientos_gen3.json"


def _cargar_json(ruta: Path) -> dict:
    '''Carga y decodifica un archivo JSON en codificación UTF-8.

    Args:
        ruta: Ruta del archivo JSON a leer.

    Returns:
        Diccionario con el contenido del JSON.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
    '''
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero: python -m servicios.descargar_datos"
        )
    return json.loads(ruta.read_text(encoding="utf-8"))


# Carga de movimientos convertidos a instancias de la clase Movimiento
_RAW_MOVIMIENTOS = _cargar_json(ARCHIVO_MOVIMIENTOS)

DICCIONARIO_MOVIMIENTOS: dict[str, Movimiento] = {
    nombre: Movimiento(
        nombre=datos["nombre"],
        tipo=datos["tipo"],
        categoria=datos["categoria"],
        potencia=datos["potencia"],
        precision=datos["precision"],
        pp=datos.get("pp", 15),
        prioridad=datos.get("prioridad", 0),
        efecto_estado=datos.get("efecto_estado", "none"),
        prob_estado=datos.get("prob_estado", 0),
        cambios_stats=datos.get("cambios_stats", []),
        prob_stat=datos.get("prob_stat", 0),
        objetivo=datos.get("objetivo", "selected-pokemon"),
    )
    for nombre, datos in _RAW_MOVIMIENTOS.items()
}

# Diccionario de especies de Kanto y tabla rápida de ratio de captura
DICCIONARIO_POKEMON: dict[str, dict] = _cargar_json(ARCHIVO_POKEMON)

TABLA_RATIOS: dict[str, int] = {
    nombre: datos["ratio_captura"]
    for nombre, datos in DICCIONARIO_POKEMON.items()
}