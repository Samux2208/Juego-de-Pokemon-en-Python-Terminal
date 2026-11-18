"""Persistencia de partidas: formato versionado, migraciones, validación y copias de seguridad.

Este paquete trabaja solo con diccionarios JSON; no importa clases del juego,
así que no puede generar importaciones circulares.
"""
from .migraciones import VERSION_ACTUAL, migrar
from .validacion import validar
from .guardado import (
    guardar_partida,
    cargar_partida,
)

__all__ = [
    "VERSION_ACTUAL", "migrar", "validar",
    "PartidaNoEncontrada", "PartidaInvalida", "guardar", "cargar",
]
