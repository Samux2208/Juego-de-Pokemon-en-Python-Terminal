'''Flujo de creación de una nueva partida al estilo Rojo Fuego / Verde Hoja.

Gestiona el diálogo introductorio con el Profesor Oak, la elección del Pokémon
inicial, la asignación opcional de apodo, el kit inicial y el primer guardado.
'''

import time
from config import DINERO_INICIAL, INICIALES
from interfaz.mensajes import ajustar_ancho, imprimir_con_retraso, nombre_tipo
from modelos.equipo import Equipo
from modelos.mochila import Mochila
from modelos.pokemon import PokemonAtrapado
from persistencia.guardado import ErrorGuardado, guardar_partida
from servicios.catalogos import DICCIONARIO_POKEMON

MAX_CARACTERES_APODO = 15  # Límite de apodo (clásico si prefieres a 10)


def nueva_partida():
    '''Configura e inicia una partida nueva solicitando nombre, inicial y apodo.

    Crea el `PokemonAtrapado` a nivel 5, inicializa el `Equipo` y la `Mochila`
    con los objetos básicos de inicio y guarda la partida inicial en disco.

    Returns:
        tuple: `(nombre_entrenador, equipo, mochila)` listos para jugar.
    '''
    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║           ✨ NUEVA PARTIDA POKÉMON ✨          ║")
    print(" ╚" + "═" * 48 + "╝")

    # Presentación inicial del Profesor Oak
    imprimir_con_retraso("\n 👨🔬 Prof. Oak: ¡Hola! ¡Bienvenido al mundo de los POKÉMON!\n")
    time.sleep(.5)
    imprimir_con_retraso("\n 👨🔬 Prof. Oak: Primero dime, ¿cómo te llamas?: ")

    nombre_entrenador = input().strip()
    while not nombre_entrenador:
        nombre_entrenador = input(
            " ⚠️  El nombre no puede estar vacío. Dime, ¿cómo te llamas?: "
        ).strip()

    # Selección de Pokémon inicial sobre la mesa del laboratorio
    imprimir_con_retraso(
        f"\n 👨🔬 Prof. Oak: ¡Muy bien, {nombre_entrenador}! Elige tu compañero en la mesa:\n"
    )
    time.sleep(.5)

    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║      🔴 POKÉ BALLS EN EL LABORATORIO           ║")
    print(" ╠" + "═" * 48 + "╣")
    for n, especie in INICIALES.items():
        tipos_str = " / ".join(
            nombre_tipo(t) for t in DICCIONARIO_POKEMON[especie]["tipos"]
        )
        print(f" ║  [{n}] {especie:<12} │ {ajustar_ancho(tipos_str, 26)} ║")
    print(" ╚" + "═" * 48 + "╝")

    while True:
        try:
            op = int(input("\n 👉 Elige tu inicial: "))
            if op in INICIALES:
                break
            print(" ❌ Opción no válida. Elige una de las opciones mostradas.")
        except ValueError:
            print(" ⚠️  Debes introducir un número entero.")

    especie = INICIALES[op]
    imprimir_con_retraso(
        f"\n 👨‍🔬 Prof. Oak: ¡Has elegido a {especie}! Una gran decisión.\n"
    )

    # Opción de apodo al estilo Rojo Fuego / Verde Hoja
    apodo = None
    resp = input(
        f"\n ✏️  ¿Quieres ponerle un apodo a {especie}? [s/N]: "
    ).strip().lower()
    if resp in ("s", "si", "sí"):
        while True:
            entrada_apodo = input(
                f" 👉 Escribe el apodo para {especie}\n (1 a {MAX_CARACTERES_APODO} caracteres, o vacío para cancelar): "
            ).strip()
            if not entrada_apodo:
                imprimir_con_retraso(f"\n ℹ️  {especie} conservará su nombre original.\n")
                break
            if 1 <= len(entrada_apodo) <= MAX_CARACTERES_APODO:
                apodo = entrada_apodo
                break
            print(
                f" ⚠️  Apodo inválido: debe tener entre 1 y {MAX_CARACTERES_APODO} caracteres."
            )

    mi_pokemon = PokemonAtrapado(especie, 5, entrenador=nombre_entrenador, apodo=apodo)
    equipo = Equipo([mi_pokemon])
    mochila = Mochila(dinero=DINERO_INICIAL)

    # Kit inicial de exploración
    mochila.agregar("pokeball", 5)
    mochila.agregar("pocion", 3)

    imprimir_con_retraso(f"\n 🎉 ¡Felicidades, {nombre_entrenador}!")
    if apodo:
        imprimir_con_retraso(
            f"\n ⭐ ¡{mi_pokemon.nombre_visible} (especie {especie}, Nv.5 - Nat. {mi_pokemon.naturaleza}) será tu compañero!\n"
        )
    else:
        imprimir_con_retraso(
            f"\n ⭐ ¡{especie} (Nv.5 - Nat. {mi_pokemon.naturaleza}) será tu compañero!\n"
        )

    # Guardado automático inicial para conservar la partida recién creada
    try:
        guardar_partida(nombre_entrenador, equipo, mochila)
        imprimir_con_retraso("\n 💾 ¡Partida guardada correctamente!\n")
    except ErrorGuardado as error:
        imprimir_con_retraso(f"\n ❌ No se pudo guardar la partida: {error}\n")

    return nombre_entrenador, equipo, mochila