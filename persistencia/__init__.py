'''Paquete de persistencia para partidas de Pokémon Gen III.

Expone utilidades de migración de versión, validación de datos y guardado o
carga segura de partidas.
'''

from .guardado import ErrorGuardado, cargar_partida, guardar_partida
from .migraciones import VERSION_ACTUAL, migrar
from .validacion import validar

__all__ = [
    "VERSION_ACTUAL",
    "migrar",
    "validar",
    "ErrorGuardado",
    "guardar_partida",
    "cargar_partida",
]