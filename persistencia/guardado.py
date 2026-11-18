"""Lectura y escritura segura del estado del juego (entrenador, equipo, PC y mochila).

Garantías:
  - La escritura es atómica (archivo temporal + Path.replace): un corte de luz
    a mitad de guardado no deja un JSON corrupto o a medias.
  - Antes de sobrescribir, la partida válida anterior se respalda en BACKUPS_DIR.
  - Un archivo ilegible o con datos inválidos se aparta como .corrupto en vez de
    perderse o romper el juego.
  - Cero librerías extra de sistema: utiliza únicamente json y pathlib (vía config).
"""

import json
import shutil
from config import ARCHIVO_PARTIDA, BACKUPS_DIR, VERSION
from modelos.equipo import Equipo
from modelos.mochila import Mochila
from modelos.pokemon import Pokemon, PokemonJugador, PokemonSalvaje
from persistencia.migraciones import migrar
from persistencia.validacion import validar

# ============================================================
# PERSISTENCIA (GUARDAR Y CARGAR PARTIDA)
# ============================================================

class ErrorGuardado(Exception):
    '''Fallo al escribir la partida en disco.'''

REGISTRO_POKEMON = {
    "Pokemon": Pokemon,
    "PokemonJugador": PokemonJugador,
    "PokemonSalvaje": PokemonSalvaje,
}

def _reconstruir_pokemon(datos):
    '''Busca la clase adecuada en el registro y delega su reconstrucción.'''
    nombre_clase = datos.get("clase", "Pokemon")
    clase_pokemon = REGISTRO_POKEMON.get(nombre_clase)
    if clase_pokemon is None:
        raise ValueError(f"Tipo de Pokémon desconocido en partida: {nombre_clase}")
    return clase_pokemon.cargar_datos(datos)


def _leer_y_reconstruir(ruta):
    '''Lee un archivo JSON, lo migra, lo valida y reconstruye los objetos del juego.'''
    contenido = ruta.read_text(encoding="utf-8")
    datos_crudos = json.loads(contenido)

    # 1. Actualizamos el formato si viene de una versión antigua (ej. v1 -> v2)
    datos_partida = migrar(datos_crudos)

    # 2. Validamos tipos y estructura antes de instanciar clases
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


def guardar_partida(nombre_entrenador, equipo, mochila=None) -> None:
  '''Guarda el estado serializable de forma atómica. Lanza ErrorGuardado si falla.'''
  mochila = mochila or Mochila()

  # Formato alineado con VERSION_ACTUAL = 2 (migraciones.py y validacion.py)
  datos_partida = {
      "version": VERSION,
      "entrenador": {"nombre": nombre_entrenador},
      "equipo": equipo.exportar_datos(),
      "mochila": mochila.exportar_datos(),
  }

  # Aseguramos que tanto la carpeta de partida como la de respaldos existan
  ARCHIVO_PARTIDA.parent.mkdir(parents=True, exist_ok=True)
  BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

  # Archivo temporal en la misma carpeta para garantizar un reemplazo atómico
  temporal = ARCHIVO_PARTIDA.with_name(ARCHIVO_PARTIDA.name + ".tmp")

  try:
    # Respaldo seguro: solo copiamos la partida anterior si es un JSON legible
    if ARCHIVO_PARTIDA.exists():
      try:
        json.loads(ARCHIVO_PARTIDA.read_text(encoding="utf-8"))
        ruta_backup = BACKUPS_DIR / "partida_backup.json"
        shutil.copy2(ARCHIVO_PARTIDA, ruta_backup)
      except (OSError, json.JSONDecodeError):
        # Si la partida anterior estaba corrupta, evitamos sobrescribir un respaldo sano
        pass

    # Escribimos los nuevos datos en el archivo temporal
    with temporal.open("w", encoding="utf-8") as archivo:
      json.dump(datos_partida, archivo, indent=4, ensure_ascii=False)

    # Reemplazo atómico: sustituye el archivo final de golpe
    temporal.replace(ARCHIVO_PARTIDA)

  except OSError as error:
    # Si algo falla al escribir, limpiamos el archivo temporal si quedó suelto
    temporal.unlink(missing_ok=True)
    raise ErrorGuardado(str(error)) from error

def cargar_partida() -> tuple[dict | None, str | None]:
  '''Carga la partida principal; si está dañada, intenta recuperar el backup.'''
  ruta_backup = BACKUPS_DIR / "partida_backup.json"

  # Si aún no existe archivo de guardado, retornamos None suavemente
  if not ARCHIVO_PARTIDA.exists() and not ruta_backup.exists():
    return None, None

  # 1. Intentar cargar el archivo principal
  if ARCHIVO_PARTIDA.exists():
      try:
          return _leer_y_reconstruir(ARCHIVO_PARTIDA), None
      except json.JSONDecodeError:
          # Solo apartamos como .corrupto si el JSON realmente está roto
          corrupto = ARCHIVO_PARTIDA.with_name(ARCHIVO_PARTIDA.name + ".corrupto")
          shutil.copy2(ARCHIVO_PARTIDA, corrupto)
      except (OSError, ValueError):
          # Si falló por validación o lectura, no destruimos el archivo original
          pass

  # 2. Plan B (Respaldo): intentar recuperar desde partida_backup.json
  if ruta_backup.exists():
      try:
          datos = _leer_y_reconstruir(ruta_backup)
          aviso = "⚠️ La partida principal estaba dañada. Se restauró tu copia de seguridad."
          return datos, aviso
      except (OSError, json.JSONDecodeError, ValueError):
          pass

  return None, "⚠️  No se pudo cargar la partida ni la copia de seguridad."