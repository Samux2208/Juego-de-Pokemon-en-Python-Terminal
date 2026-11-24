'''Lectura y escritura segura de partidas guardadas para Pokémon Gen III.

Garantías:
  - Escritura atómica mediante archivo temporal (`.tmp`) y `Path.replace`.
  - Respaldo previo de una partida válida en `BACKUPS_DIR / "partida_backup.json"`.
  - Apartado de archivos JSON corruptos con sufijo `.corrupto` sin destruir datos.
  - Reconstrucción polimórfica de subclases de `Pokemon` mediante `REGISTRO_POKEMON`.
'''

import json
import shutil
from config import ARCHIVO_PARTIDA, BACKUPS_DIR, VERSION
from modelos.equipo import Equipo
from modelos.mochila import Mochila
from modelos.pokemon import (
    Pokemon,
    PokemonAtrapado,
    PokemonCapturable,
    PokemonSalvaje,
)
from persistencia.migraciones import migrar
from persistencia.validacion import validar


class ErrorGuardado(Exception):
    '''Excepción lanzada cuando ocurre un error al guardar la partida en disco.'''


# Registro de clases válidas para reconstruir Pokémon según el campo "clase" del JSON
REGISTRO_POKEMON = {
    "Pokemon": Pokemon,
    "PokemonCapturable": PokemonCapturable,
    "PokemonAtrapado": PokemonAtrapado,
    "PokemonJugador": PokemonAtrapado,  # Compatibilidad con partidas generadas como jugador
    "PokemonSalvaje": PokemonSalvaje,
}


def _reconstruir_pokemon(datos: dict):
    '''Reconstruye la instancia de Pokémon correspondiente según su `"clase"` en JSON.

    Args:
        datos: Diccionario serializado de un Pokémon.

    Returns:
        Pokemon: Instancia reconstruida de la clase registrada.

    Raises:
        ValueError: Si `"clase"` no está registrada en `REGISTRO_POKEMON`.
    '''
    nombre_clase = datos.get("clase", "Pokemon")
    clase_pokemon = REGISTRO_POKEMON.get(nombre_clase)
    if clase_pokemon is None:
        raise ValueError(f"Tipo de Pokémon desconocido en partida: {nombre_clase}")
    return clase_pokemon.cargar_datos(datos)


def _leer_y_reconstruir(ruta) -> dict:
    '''Lee un archivo JSON de partida, aplica migraciones, valida y reconstruye el estado.

    Args:
        ruta: Objeto `Path` apuntando al archivo de partida o backup.

    Returns:
        dict: Diccionario con `'nombre_entrenador'`, `'equipo'` y `'mochila'`.

    Raises:
        json.JSONDecodeError: Si el archivo no contiene JSON válido.
        ValueError: Si la estructura o los datos de la partida no son válidos.
        OSError: Si ocurre un error de lectura en disco.
    '''
    contenido = ruta.read_text(encoding="utf-8")
    datos_crudos = json.loads(contenido)

    # 1. Migrar estructura desde versiones anteriores si es necesario
    datos_partida = migrar(datos_crudos)

    # 2. Validar esquema y valores antes de instanciar objetos del dominio
    errores = validar(datos_partida)
    if errores:
        raise ValueError(f"Partida inválida: {'; '.join(errores)}")

    nombre_entrenador = datos_partida["entrenador"]["nombre"]
    equipo = Equipo.cargar_datos(
        datos_partida["equipo"],
        cargador_pokemon=_reconstruir_pokemon,
    )
    mochila = Mochila.cargar_datos(datos_partida.get("mochila"))

    return {
        "nombre_entrenador": nombre_entrenador,
        "equipo": equipo,
        "mochila": mochila,
    }


def guardar_partida(nombre_entrenador: str, equipo, mochila=None) -> None:
    '''Guarda el estado actual de la partida de forma atómica en `ARCHIVO_PARTIDA`.

    Respalda previamente la partida anterior si es un JSON válido y elimina el
    archivo temporal si ocurre algún fallo durante la exportación o escritura.

    Args:
        nombre_entrenador: Nombre del entrenador jugador.
        equipo: Instancia de `Equipo` del jugador.
        mochila: Instancia opcional de `Mochila` (si es `None`, crea una nueva).

    Raises:
        ErrorGuardado: Si falla la serialización o la escritura en disco.
    '''
    mochila = mochila or Mochila()

    # Garantiza que las carpetas destino existan antes de respaldar o escribir
    ARCHIVO_PARTIDA.parent.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    # Archivo temporal en la misma carpeta para permitir un reemplazo atómico
    temporal = ARCHIVO_PARTIDA.with_name(ARCHIVO_PARTIDA.name + ".tmp")

    try:
        datos_partida = {
            "version": VERSION,
            "entrenador": {"nombre": nombre_entrenador},
            "equipo": equipo.exportar_datos(),
            "mochila": mochila.exportar_datos(),
        }

        # Respaldar la partida previa solo si su JSON es legible y válido
        if ARCHIVO_PARTIDA.exists():
            try:
                json.loads(ARCHIVO_PARTIDA.read_text(encoding="utf-8"))
                ruta_backup = BACKUPS_DIR / "partida_backup.json"
                shutil.copy2(ARCHIVO_PARTIDA, ruta_backup)
            except (OSError, json.JSONDecodeError):
                # No sobrescribir el respaldo si la partida anterior estaba dañada
                pass

        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(datos_partida, archivo, indent=4, ensure_ascii=False)

        # Reemplazo atómico del archivo final
        temporal.replace(ARCHIVO_PARTIDA)

    except (OSError, ValueError, TypeError) as error:
        temporal.unlink(missing_ok=True)
        raise ErrorGuardado(str(error)) from error


def cargar_partida() -> tuple[dict | None, str | None]:
    '''Carga la partida principal o recurre al respaldo si aquella está dañada.

    Si la partida principal tiene JSON corrupto, guarda una copia `.corrupto`.

    Returns:
        tuple[dict | None, str | None]: `(datos_partida, mensaje_aviso)`.
            Si no existe partida ni respaldo, devuelve `(None, None)`.
    '''
    ruta_backup = BACKUPS_DIR / "partida_backup.json"

    if not ARCHIVO_PARTIDA.exists() and not ruta_backup.exists():
        return None, None

    # 1. Intentar cargar el archivo principal de partida
    if ARCHIVO_PARTIDA.exists():
        try:
            return _leer_y_reconstruir(ARCHIVO_PARTIDA), None
        except json.JSONDecodeError:
            corrupto = ARCHIVO_PARTIDA.with_name(ARCHIVO_PARTIDA.name + ".corrupto")
            try:
                shutil.copy2(ARCHIVO_PARTIDA, corrupto)
            except OSError:
                pass
        except (OSError, ValueError):
            # Si falló por validación o lectura, conservamos el archivo para diagnóstico
            pass

    # 2. Intentar recuperar desde el archivo de respaldo si existe
    if ruta_backup.exists():
        try:
            datos = _leer_y_reconstruir(ruta_backup)
            aviso = (
                "⚠️ La partida principal estaba dañada. "
                "Se restauró tu copia de seguridad."
            )
            return datos, aviso
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    return None, "⚠️  No se pudo cargar la partida ni la copia de seguridad."