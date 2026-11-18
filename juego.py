import time
from servicios.nueva_partida import nueva_partida
from persistencia.guardado import guardar_partida, cargar_partida, ErrorGuardado
from interfaz.mensajes import imprimir_con_retraso
from interfaz.menus import gestionar_mochila, zona_segura, menu_rutas
from interfaz.pokedex_ui import ficha_pokemon

# == BUCLE PRINCIPAL DEL JUEGO ===============================
# main() | Controla la pantalla de título, carga/creación de partida
#          y el menú principal de navegación por el mundo Pokémon.
# ============================================================

def iniciar_juego():
    '''Punto de entrada principal que coordina el ciclo completo de la partida.'''
    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║    🎮 POOKéMON EDICIÓN TERMINAL (KANTO) 🎮     ║")
    print(" ╠" + "═" * 48 + "╣")
    print(" ║  [1] 📂 Continuar Partida                      ║")
    print(" ║  [2] ✨ Nueva Partida                          ║")
    print(" ╚" + "═" * 48 + "╝")

    # Control de arranque: elegir entre cargar partida o iniciar una nueva
    while True:
        try:
            op = int(input(" 👉 Selecciona una opción: "))
            if op in (1, 2):
                break
            print(" ❌ Por favor, selecciona 1 o 2.")
        except ValueError:
            print(" ❌ Introduce un número válido.")

    if op == 1:
        datos_partida, aviso = cargar_partida()
        
        if aviso:
            imprimir_con_retraso(f"\n {aviso}\n")

        if datos_partida:
            nombre_entrenador = datos_partida["nombre_entrenador"]
            equipo = datos_partida["equipo"]
            mochila = datos_partida["mochila"]
        else:
            imprimir_con_retraso("\n 📭 No hay partida guardada. Iniciando nueva aventura...\n")
            time.sleep(1)
            nombre_entrenador, equipo, mochila = nueva_partida()
    else:
        nombre_entrenador, equipo, mochila = nueva_partida()

    # BUCLE GENERAL DEL MENÚ PRINCIPAL DEL JUEGO
    while True:
        lider = equipo.pokemon[0]
        time.sleep(.5)
        print("\n" + " ╔" + "═" * 52 + "╗")
        print(f" ║ 👤 ENTRENADOR: {nombre_entrenador:<35} ║")
        print(f" ║ ⭐ LÍDER: {lider.nombre_visible:<15} Nv.{lider.nivel:<5}  ❤️ {lider.salud_actual:>3}/{lider.salud_maxima:<3}      ║")
        print(f" ║ 💰 SALDO: {mochila.dinero:<8} ₽   │   🎒 EQUIPO: {len(equipo.pokemon)}/{equipo.LIMITE}          ║")
        print(" ╠" + "═" * 52 + "╣")
        print(" ║  [1] 🗺️  Explorar Rutas de Kanto                    ║")
        print(" ║  [2] 🏘️  Ir al Pueblo (Centro, PC y Tienda)         ║")
        print(" ║  [3] 📊 POKéMON                                    ║")
        print(" ║  [4] 🎒 Mochila (Objetos y Evolución)              ║")
        print(" ║  [5] 💾 Guardar Partida                            ║")
        print(" ║  [6] 🚪 Salir del Juego                            ║")
        print(" ╚" + "═" * 52 + "╝")

        try:
            op_menu = int(input(" 👉 ¿Qué deseas hacer?: "))
        except ValueError:
            print("\n ⚠️ Por favor, introduce un número del 1 al 6.")
            continue

        # 3. Gestión de las opciones del menú principal
        match op_menu:
            case 1:
                # Bloqueo de seguridad: evita viajar si todo el equipo está debilitado
                if not any(p.salud_actual > 0 for p in equipo.pokemon):
                    imprimir_con_retraso("\n 💀 Todo tu equipo está debilitado. Visita primero el Centro Pokémon.")
                else:
                    menu_rutas(nombre_entrenador, equipo, mochila)  
            case 2:
                zona_segura(equipo, mochila)
            case 3:
                if len(equipo.pokemon) == 1:
                    ficha_pokemon(equipo.pokemon[0])
                else:
                    print("\n 📊 ¿De qué Pokémon quieres ver la ficha?")
                    for i, poke in enumerate(equipo.pokemon, start=1):
                        print(f"  [{i}] {poke.nombre_visible} (Nv.{poke.nivel})")
                    print("  [X] 🔙 Cancelar")
                    sel = input(" 👉 Elige un Pokémon: ").strip().lower()
                    if sel.isdigit() and 1 <= int(sel) <= len(equipo.pokemon):
                        ficha_pokemon(equipo.pokemon[int(sel) - 1])
            case 4:
                gestionar_mochila(equipo, mochila)
            case 5:
                # Guardamos inmediatamente la partida inicial para no perder el progreso
                try:
                    guardar_partida(nombre_entrenador, equipo, mochila)
                    imprimir_con_retraso("\n💾 ¡Partida guardada correctamente!\n")
                except ErrorGuardado as error:
                    imprimir_con_retraso(f"\n❌ No se pudo guardar la partida: {error}\n")
            case 6:
                imprimir_con_retraso("\n 👋 ¡Gracias por jugar POOKéMON! ¡Hasta pronto!")
                break
            case _:
                print("\n ⚠️ Opción no válida. Elige del 1 al 6..")