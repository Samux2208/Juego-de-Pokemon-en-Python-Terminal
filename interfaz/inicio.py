'''Interfaz de consola para el arranque y el menú principal.'''

import time
from interfaz.mensajes import imprimir_con_retraso


def pedir_opcion_inicio() -> int:
    '''Muestra la pantalla inicial y devuelve 1 (Continuar) o 2 (Nueva partida).'''
    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║    📟 POOKÉMON EDICIÓN TERMINAL (KANTO) 🎮     ║")
    print(" ╠" + "═" * 48 + "╣")
    print(" ║  [1] 📂 Continuar Partida                      ║")
    print(" ║  [2] ✨ Nueva Partida                          ║")
    print(" ╚" + "═" * 48 + "╝")

    while True:
        try:
            opcion = int(input(" 👉 Selecciona una opción: "))
            if opcion in (1, 2):
                return opcion
            print(" ❌ Por favor, selecciona 1 o 2.")
        except ValueError:
            print(" ❌ Introduce un número válido.")


def pedir_opcion_menu_principal(nombre_entrenador: str, equipo, mochila) -> int:
    '''Muestra el resumen del jugador y devuelve la opción elegida (1 a 7).'''
    lider = equipo.pokemon[0]
    time.sleep(.5)

    print("\n" + " ╔" + "═" * 52 + "╗")
    print(f" ║ 👤 ENTRENADOR: {nombre_entrenador:<35} ║")
    print(
        f" ║ ⭐ LÍDER: {lider.nombre_visible:<15} Nv.{lider.nivel:<5}  "
        f"❤️ {lider.salud_actual:>3}/{lider.salud_maxima:<3}      ║"
    )
    print(
        f" ║ 💰 SALDO: {mochila.dinero:<8} ₽   │   "
        f"🎒 EQUIPO: {len(equipo.pokemon)}/{equipo.LIMITE}          ║"
    )
    print(" ╠" + "═" * 52 + "╣")
    print(" ║  [1] 🗺️  Explorar Rutas de Kanto                    ║")
    print(" ║  [2] 🏘️  Ir al Pueblo (Centro, PC y Tienda)         ║")
    print(" ║  [3] 📊 POKÉMON                                    ║")
    print(" ║  [4] 🎒 Mochila (Objetos y Evolución)              ║")
    print(" ║  [5] 💾 Guardar Partida                            ║")
    print(" ║  [6] 🚪 Salir del Juego                            ║")
    print(" ╚" + "═" * 52 + "╝")

    while True:
        try:
            opcion = int(input(" 👉 ¿Qué deseas hacer?: "))
            if 1 <= opcion <= 7:
                return opcion
            print("\n ⚠️ Opción no válida. Elige del 1 al 6.")
        except ValueError:
            print("\n ⚠️ Por favor, introduce un número del 1 al 6.")


def pedir_pokemon_ficha(pokemones: list):
    '''Permite elegir un Pokémon del equipo para ver su ficha o cancelar.'''
    if len(pokemones) == 1:
        return pokemones[0]

    print("\n 📊 ¿De qué Pokémon quieres ver la ficha?")
    for i, poke in enumerate(pokemones, start=1):
        print(f"  [{i}] {poke.nombre_visible} (Nv.{poke.nivel})")
    print("  [X] 🔙 Cancelar")

    seleccion = input(" 👉 Elige un Pokémon: ").strip().lower()
    if seleccion.isdigit():
        indice = int(seleccion) - 1
        if 0 <= indice < len(pokemones):
            return pokemones[indice]

    return None


def notificar_evento(evento: str, detalle: str = "") -> None:
    '''Muestra mensajes de estado del bucle principal en consola.'''
    match evento:
        case "aviso_carga":
            imprimir_con_retraso(f"\n {detalle}\n")
        case "sin_partida":
            imprimir_con_retraso("\n 📭 No hay partida guardada. Iniciando nueva aventura...\n")
            time.sleep(1)
        case "equipo_debilitado":
            imprimir_con_retraso("\n 💀 Todo tu equipo está debilitado. Visita primero el Centro Pokémon.")
        case "guardado_ok":
            imprimir_con_retraso("\n 💾 ¡Partida guardada correctamente!\n")
        case "guardado_error":
            imprimir_con_retraso(f"\n ❌ No se pudo guardar la partida: {detalle}\n")
        case "salir":
            imprimir_con_retraso("\n 👋 ¡Gracias por jugar POOKÉMON! ¡Hasta pronto!")