'''Validación estructural previa de una partida en formato v2 para Gen III.

Actúa como filtro de seguridad antes de instanciar las clases del juego
(`Pokemon`, `PokemonCapturable`, `PokemonSalvaje`, `PokemonAtrapado`,
`Equipo`, `Mochila`), verificando estructura, tipos y rangos numéricos[cite: 8, 13].

No utiliza ninguna librería externa (cero imports)[cite: 13].
'''

# Clases permitidas en el modelo multinivel de Pokémon al serializar/deserializar[cite: 8, 13]
CLASES_VALIDAS = (
    "Pokemon",
    "PokemonCapturable",
    "PokemonSalvaje",
    "PokemonAtrapado",
)

# Rarezas válidas para Pokémon con datos de encuentro/captura[cite: 8]
_RAREZAS_VALIDAS = ("comun", "raro", "muy raro")


def _validar_pokemon(p, ubicacion, especies):
    '''Revisa los campos y tipos de un diccionario individual de Pokémon[cite: 13].

    Args:
        p (dict): Diccionario con los atributos serializados de un Pokémon[cite: 13].
        ubicacion (str): Ruta legible para reportar errores (ej.
            `'equipo.pokemon[0]'`)[cite: 13].
        especies (set | list | tuple | None): Colección opcional de especies
            válidas en el juego[cite: 13].

    Returns:
        list[str]: Lista de mensajes de error encontrados en este Pokémon[cite: 13].
    '''
    errores = []

    # 1. El elemento debe ser un diccionario antes de inspeccionar sus claves[cite: 13]
    if not isinstance(p, dict):
        return [f"{ubicacion}: no es un objeto."]

    # 2. Validación de la especie (texto no vacío y opcionalmente en catálogo)[cite: 13]
    nombre = p.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        errores.append(f"{ubicacion}: falta 'nombre'.")
    elif especies is not None and nombre not in especies:
        errores.append(f"{ubicacion}: especie desconocida '{nombre}'.")

    # 3. Validación de nivel: entero entre 1 y 100 (excluyendo booleanos)[cite: 13]
    nivel = p.get("nivel", 1)
    if isinstance(nivel, bool) or not isinstance(nivel, int) or not 1 <= nivel <= 100:
        errores.append(f"{ubicacion}: nivel inválido ({nivel!r}).")

    # 4. Validación de experiencia y salud: enteros >= 0 (excluyendo booleanos)[cite: 13]
    for campo in ("exp_actual", "salud_actual"):
        valor = p.get(campo, 0)
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            errores.append(f"{ubicacion}: '{campo}' inválido ({valor!r}).")

    # 5. Validación de la clase serializada dentro de la jerarquía multinivel[cite: 8, 13]
    clase = p.get("clase", "Pokemon")
    if clase not in CLASES_VALIDAS:
        errores.append(f"{ubicacion}: clase desconocida {clase!r}.")

    # 6. Movimientos: debe ser una lista de nombres en texto (str)[cite: 13]
    movs = p.get("movimientos", [])
    if not isinstance(movs, list) or not all(isinstance(m, str) for m in movs):
        errores.append(f"{ubicacion}: 'movimientos' debe ser una lista de nombres.")

    # 7. Apodo opcional (None o str no vacío de hasta 15 caracteres)[cite: 8, 13]
    apodo = p.get("apodo")
    if apodo is not None and (
        not isinstance(apodo, str)
        or not apodo.strip()
        or len(apodo.strip()) > 15
    ):
        errores.append(f"{ubicacion}: apodo inválido.")

    # 8. Entrenador opcional si está presente en el diccionario[cite: 8]
    if "entrenador" in p and p["entrenador"] is not None:
        if not isinstance(p["entrenador"], str) or not p["entrenador"].strip():
            errores.append(f"{ubicacion}: 'entrenador' inválido.")

    # 9. Rareza y ruta opcionales si están presentes en el diccionario[cite: 8]
    if "rareza" in p and p["rareza"] is not None:
        if p["rareza"] not in _RAREZAS_VALIDAS:
            errores.append(f"{ubicacion}: 'rareza' inválida ({p['rareza']!r}).")

    if "ruta" in p and p["ruta"] is not None:
        if not isinstance(p["ruta"], str) or not p["ruta"].strip():
            errores.append(f"{ubicacion}: 'ruta' inválida.")

    return errores


def validar(datos, especies=None):
    '''Valida el diccionario completo de una partida v2 y devuelve los errores[cite: 13].

    Args:
        datos (dict): Diccionario completo de la partida (ya migrado a v2)[cite: 13].
        especies (set | list | tuple | None): Conjunto opcional de especies
            válidas[cite: 13]. Los objetos y movimientos desconocidos no se
            marcan aquí como error fatal[cite: 13].

    Returns:
        list[str]: Lista vacía `[]` si es válida, o lista de errores hallados[cite: 13].
    '''
    if not isinstance(datos, dict):
        return ["La partida no es un objeto JSON."]

    errores = []

    # 1. Versión esperada del esquema tras pasar por migraciones[cite: 12, 13]
    if datos.get("version") != 2:
        errores.append(f"Se esperaba versión 2, hay {datos.get('version')!r}.")

    # 2. Sección 'entrenador': debe ser dict con 'nombre' de texto no vacío[cite: 13]
    entrenador = datos.get("entrenador")
    nombre = entrenador.get("nombre") if isinstance(entrenador, dict) else None
    if not isinstance(nombre, str) or not nombre.strip():
        errores.append("Falta el nombre del entrenador.")

    # 3. Sección 'equipo': equipo activo (1 a 6 Pokémon) y PC (lista)[cite: 8, 13]
    equipo = datos.get("equipo")
    if not isinstance(equipo, dict):
        errores.append("Falta la sección 'equipo'.")
    else:
        activos = equipo.get("pokemon")
        pc = equipo.get("pc", [])

        if not isinstance(activos, list) or not activos:
            errores.append("El equipo activo debe tener al menos un Pokémon.")
        elif len(activos) > 6:
            errores.append("El equipo activo no puede superar 6 Pokémon.")

        if not isinstance(pc, list):
            errores.append("'pc' debe ser una lista.")

        for seccion, lista in (("equipo.pokemon", activos), ("equipo.pc", pc)):
            if isinstance(lista, list):
                for i, p in enumerate(lista):
                    errores += _validar_pokemon(p, f"{seccion}[{i}]", especies)

    # 4. Sección 'mochila': saldo entero >= 0 y 'objetos' con cantidades enteras >= 0[cite: 8, 13]
    mochila = datos.get("mochila")
    if not isinstance(mochila, dict):
        errores.append("Falta la sección 'mochila'.")
    else:
        dinero = mochila.get("dinero", 0)
        if isinstance(dinero, bool) or not isinstance(dinero, int) or dinero < 0:
            errores.append(f"Pokémonedas inválidas ({dinero!r}).")

        objetos = mochila.get("objetos", {})
        if not isinstance(objetos, dict) or any(
            isinstance(c, bool) or not isinstance(c, int) or c < 0
            for c in objetos.values()
        ):
            errores.append("'objetos' debe ser {identificador: cantidad >= 0}.")

        medallas = mochila.get("medallas", [])
        if not isinstance(medallas, list) or any(
            not isinstance(medalla, str) or not medalla.strip()
            for medalla in medallas
        ):
            errores.append("'medallas' debe ser una lista de nombres no vacíos.")

    # 5. Sección 'pokedex': diccionario con listas 'vistos' y 'capturados'[cite: 12, 13]
    pokedex = datos.get("pokedex", {})
    if not isinstance(pokedex, dict) or any(
        not isinstance(pokedex.get(k, []), list) for k in ("vistos", "capturados")
    ):
        errores.append("'pokedex' debe tener listas 'vistos' y 'capturados'.")

    return errores