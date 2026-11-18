"""Registro de migraciones del formato de guardado.

Cada migración transforma un diccionario de la versión N a la N+1 y es una
función pura (no toca disco ni modifica el diccionario original).

Para añadir una versión futura (ejemplo, v3):
  1. Incrementar VERSION_ACTUAL a 3.
  2. Escribir `_migrar_v2_a_v3(datos)` y registrarla en MIGRACIONES como `2: _migrar_v2_a_v3`.
  3. Actualizar validacion.py y añadir una prueba en tests/test_guardado.py.
"""

# Importamos 'copy' para clonar diccionarios complejos sin alterar los datos originales
import copy

# Constante que indica cuál es la versión más reciente que entiende tu juego hoy
VERSION_ACTUAL = 2


def _migrar_v1_a_v2(datos):
  """Transforma una partida de v1 (formato plano) a v2 (formato agrupado por secciones).

    Cambios estructurales:
      - 'nombre_entrenador' pasa a vivir dentro de 'entrenador': {'nombre': ...}.
      - Se crea la sección 'progreso' con valores iniciales por defecto.
      - Se genera la 'pokedex' automáticamente revisando los Pokémon que ya tiene el
      jugador.
      - 'equipo' y 'mochila' conservan exactamente su misma estructura interna.
    """
  # Extraemos el diccionario del equipo (si no existe, usamos uno vacío para evitar errores)
  equipo = datos.get("equipo", {})

  # Lista temporal para recolectar los nombres únicos de los Pokémon del jugador
  especies = []

  # Unimos la lista del equipo activo y la del PC para revisar todos los Pokémon que posee
  todos_los_pokemon = equipo.get("pokemon", []) + equipo.get("pc", [])

  for p in todos_los_pokemon:
    # Verificamos que cada elemento sea un diccionario válido y tenga un nombre en texto
    if isinstance(p, dict) and isinstance(p.get("nombre"), str):
      # Evitamos guardar nombres duplicados en la Pokédex (ej: si tiene dos Pikachu)
      if p["nombre"] not in especies:
        especies.append(p["nombre"])

  # Retornamos un diccionario completamente nuevo con el formato exacto de la versión 2
  return {
      "version": 2,
      "entrenador": {"nombre": datos.get("nombre_entrenador")},
      "progreso": {
          "ubicacion_actual": "Pueblo Paleta",
          "insignias": [],
          "eventos_completados": [],
      },
      "equipo": equipo,
      "mochila": datos.get("mochila", {}),
      # Como v1 no tenía Pokédex, asumimos que vio y capturó las especies que ya posee
      "pokedex": {"vistos": list(especies), "capturados": list(especies)},
  }


# Diccionario mapa que conecta cada versión antigua con la función que la actualiza.
# Clave = versión de origen | Valor = función que la convierte a la versión siguiente
MIGRACIONES = {1: _migrar_v1_a_v2}


def migrar(datos):
  """Recibe un diccionario de partida y lo actualiza paso a paso hasta VERSION_ACTUAL.

    Args:
        datos (dict): Datos crudos leídos directamente desde el archivo JSON.

    Returns:
        dict: Una copia limpia y actualizada de los datos en formato
          VERSION_ACTUAL.

    Raises:
        ValueError: Si los datos no son un diccionario, la versión es inválida,
                    es de una versión futura o falta una función de migración.
    """
  # 1. Validación inicial: el archivo JSON raíz debe ser un diccionario (objeto)
  if not isinstance(datos, dict):
    raise ValueError("La partida no es un objeto JSON.")

  version = datos.get("version")

  # 2. Validamos que 'version' sea un número entero positivo (1, 2, 3...).
  # Nota: descartamos `bool` explícitamente porque en Python `True == 1` es verdadero.
  if isinstance(version, bool) or not isinstance(version, int) or version < 1:
    raise ValueError(f"Versión de guardado inválida: {version!r}")

  # 3. Evitamos abrir partidas creadas en una versión más nueva del juego (downgrade)
  if version > VERSION_ACTUAL:
    raise ValueError(
        f"La partida es de una versión más nueva ({version}) que la soportada"
        f" ({VERSION_ACTUAL})."
    )

  # 4. Hacemos una copia profunda (deepcopy) para no modificar el diccionario original
  # si ocurre algún error a mitad del proceso de migración.
  datos = copy.deepcopy(datos)

  # 5. Bucle escalonado: actualiza la partida versión por versión (ej: v1 -> v2 -> v3)
  while datos["version"] < VERSION_ACTUAL:
    version_en_curso = datos["version"]
    paso = MIGRACIONES.get(version_en_curso)

    # Si falta un eslabón en la cadena de migraciones, detenemos el proceso con error claro
    if paso is None:
      raise ValueError(
          f"No existe migración desde la versión {version_en_curso}."
      )

    # Ejecutamos la función de migración y reemplazamos `datos` con la nueva versión
    datos = paso(datos)

  return datos
  