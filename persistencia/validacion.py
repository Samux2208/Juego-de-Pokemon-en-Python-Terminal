"""Validación estructural de una partida en formato v2, antes de construir objetos.

Este módulo actúa como un filtro de seguridad previo: revisa que el diccionario
leído desde el JSON tenga todas las claves, tipos de datos y rangos numéricos
correctos antes de intentar instanciar las clases reales del juego (Pokemon,
Equipo, Mochila).

No utiliza ninguna librería externa (cero imports).
"""

# Tupla con los nombres exactos de las clases de Pokémon permitidas al serializar
CLASES_VALIDAS = ("Pokemon", "PokemonJugador", "PokemonSalvaje")


def _validar_pokemon(p, ubicacion, especies):
  """Revisa los datos individuales de un diccionario de Pokémon.

    Args:
        p (dict): Diccionario con los atributos guardados de un Pokémon.
        ubicacion (str): Ruta legible para reportar errores (ej:
          'equipo.pokemon[0]').
        especies (set | list | None): Colección opcional de especies válidas.

    Returns:
        list[str]: Lista de mensajes de error encontrados en este Pokémon.
    """
  errores = []

  # 1. El elemento debe ser un diccionario; si no lo es, no tiene sentido seguir revisándolo
  if not isinstance(p, dict):
    return [f"{ubicacion}: no es un objeto."]

  # 2. Validación del nombre de especie (obligatorio y texto no vacío)
  nombre = p.get("nombre")
  if not isinstance(nombre, str) or not nombre:
    errores.append(f"{ubicacion}: falta 'nombre'.")
  # Si se pasó un catálogo de especies válidas, verificamos que el Pokémon exista en el juego
  elif especies is not None and nombre not in especies:
    errores.append(f"{ubicacion}: especie desconocida '{nombre}'.")

  # 3. Validación de nivel: debe ser un entero entre 1 y 100 (descartando booleanos)
  nivel = p.get("nivel", 1)
  if (
      isinstance(nivel, bool)
      or not isinstance(nivel, int)
      or not 1 <= nivel <= 100
  ):
    errores.append(f"{ubicacion}: nivel inválido ({nivel!r}).")

  # 4. Validación de experiencia y salud: deben ser enteros iguales o mayores a 0
  for campo in ("exp_actual", "salud_actual"):
    valor = p.get(campo, 0)
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
      errores.append(f"{ubicacion}: '{campo}' inválido ({valor!r}).")

  # 5. Verificamos que la clase serializada pertenezca a las permitidas en el modelo
  if p.get("clase", "Pokemon") not in CLASES_VALIDAS:
    errores.append(f"{ubicacion}: clase desconocida {p.get('clase')!r}.")

  # 6. Los movimientos deben ser una lista y cada elemento dentro debe ser un texto (str)
  movs = p.get("movimientos", [])
  if not isinstance(movs, list) or not all(isinstance(m, str) for m in movs):
    errores.append(
        f"{ubicacion}: 'movimientos' debe ser una lista de nombres."
    )

  # 7. El apodo es opcional (None), pero si existe debe ser texto no vacío de máximo 15 letras
  apodo = p.get("apodo")
  if apodo is not None and (
      not isinstance(apodo, str)
      or not apodo.strip()
      or len(apodo.strip()) > 15
  ):
    errores.append(f"{ubicacion}: apodo inválido.")

  return errores


def validar(datos, especies=None):
  """Valida el diccionario completo de una partida v2 y devuelve todos los errores hallados.

    Args:
        datos (dict): Diccionario completo de la partida (ya migrado a v2).
        especies (set | list | None): Conjunto opcional de nombres de especie
          válidos. Nota: Los objetos y movimientos desconocidos NO marcan error
          aquí; el juego los descarta con un aviso al cargar para no perder la
          partida entera por un dato suelto.

    Returns:
        list[str]: Lista vacía `[]` si la partida es 100% válida, o lista con
          todos los fallos detectados.
    """
  # Validación raíz: el archivo JSON completo debe ser un diccionario
  if not isinstance(datos, dict):
    return ["La partida no es un objeto JSON."]

  errores = []

  # 1. Verificamos que la partida haya pasado por migraciones y esté en versión 2
  if datos.get("version") != 2:
    errores.append(f"Se esperaba versión 2, hay {datos.get('version')!r}.")

  # 2. Validamos la sección 'entrenador' y que su nombre sea texto válido con contenido
  nombre = (
      (datos.get("entrenador") or {}).get("nombre")
      if isinstance(datos.get("entrenador"), dict)
      else None
  )
  if not isinstance(nombre, str) or not nombre.strip():
    errores.append("Falta el nombre del entrenador.")

  # 3. Validamos la sección 'equipo' (tanto el equipo activo de 1-6 como el almacenamiento del PC)
  equipo = datos.get("equipo")
  if not isinstance(equipo, dict):
    errores.append("Falta la sección 'equipo'.")
  else:
    activos, pc = equipo.get("pokemon"), equipo.get("pc", [])

    # Regla oficial: el entrenador siempre debe llevar entre 1 y 6 Pokémon encima
    if not isinstance(activos, list) or not activos:
      errores.append("El equipo activo debe tener al menos un Pokémon.")
    elif len(activos) > 6:
      errores.append("El equipo activo no puede superar 6 Pokémon.")

    # El PC puede estar vacío, pero obligatoriamente debe ser una lista
    if not isinstance(pc, list):
      errores.append("'pc' debe ser una lista.")

    # Recorremos cada Pokémon del equipo y del PC usando enumerate para saber su índice exacto
    for seccion, lista in (("equipo.pokemon", activos), ("equipo.pc", pc)):
      if isinstance(lista, list):
        for i, p in enumerate(lista):
          errores += _validar_pokemon(p, f"{seccion}[{i}]", especies)

  # 4. Validamos la sección 'mochila' (dinero >= 0 y diccionario de objetos con cantidades >= 0)
  mochila = datos.get("mochila")
  if not isinstance(mochila, dict):
    errores.append("Falta la sección 'mochila'.")
  else:
    dinero = mochila.get("dinero", 0)
    if isinstance(dinero, bool) or not isinstance(dinero, int) or dinero < 0:
      errores.append(f"Pokémonedas inválidas ({dinero!r}).")

    objetos = mochila.get("objetos", {})
    # Verificamos que 'objetos' sea un diccionario y que ninguna cantidad sea negativa o booleana
    if not isinstance(objetos, dict) or any(
        isinstance(c, bool) or not isinstance(c, int) or c < 0
        for c in objetos.values()
    ):
      errores.append("'objetos' debe ser {identificador: cantidad >= 0}.")

  # 5. Validamos la sección 'pokedex': debe ser diccionario y contener listas 'vistos' y 'capturados'
  pokedex = datos.get("pokedex", {})
  if not isinstance(pokedex, dict) or any(
      not isinstance(pokedex.get(k, []), list) for k in ("vistos", "capturados")
  ):
    errores.append("'pokedex' debe tener listas 'vistos' y 'capturados'.")

  return errores