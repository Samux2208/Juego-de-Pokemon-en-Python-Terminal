import time
from config import INICIALES, DINERO_INICIAL
from servicios.repositorio import DICCIONARIO_POKEMON
from modelos.pokemon import PokemonJugador
from modelos.equipo import Equipo
from modelos.mochila import Mochila
from persistencia.guardado import guardar_partida, ErrorGuardado
from interfaz.mensajes import imprimir_con_retraso, nombre_tipo, ajustar_ancho

# ============================================================
# INICIO DE PARTIDA NUEVA
# ============================================================

def nueva_partida():
    '''Configura e inicia una partida nueva solicitando nombre y Pokémon inicial.
    
    Crea la instancia de PokemonJugador a nivel 5, inicializa el Equipo y la Mochila
    con objetos básicos de aventura y guarda el progreso inicial en disco.
    
    Devuelve:
        tuple: (nombre_entrenador, equipo, mochila) listos para jugar.
    '''
    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║           ✨ NUEVA PARTIDA POKéMON ✨          ║")
    print(" ╚" + "═" * 48 + "╝")

    # Diálogo de bienvenida estilo Profesor Oak
    imprimir_con_retraso("\n 👨🔬 Prof. Oak: ¡Hola! ¡Bienvenido al mundo de los POKéMON!\n")
    time.sleep(.5)
    imprimir_con_retraso("\n 👨🔬 Prof. Oak: Primero dime, ¿cómo te llamas?: ")

    nombre_entrenador = input().strip()
    while not nombre_entrenador:
        nombre_entrenador = input(" ⚠️  El nombre no puede estar vacío. Dime, ¿cómo te llamas?: ").strip()

    # Elección del Pokémon inicial sobre la mesa del laboratorio
    imprimir_con_retraso(f"\n 👨🔬 Prof. Oak: ¡Muy bien, {nombre_entrenador}! Elige tu compañero en la mesa:\n")
    time.sleep(.5)
    
    print("\n" + " ╔" + "═" * 48 + "╗")
    print(" ║      🔴 POKé BALLS EN EL LABORATORIO           ║")
    print(" ╠" + "═" * 48 + "╣")
    # Mostramos los 3 iniciales disponibles (Charmander, Squirtle y Bulbasaur)
    for n, especie in INICIALES.items():
        tipos_str = " / ".join(nombre_tipo(t) for t in DICCIONARIO_POKEMON[especie]["tipos"])
        print(f" ║  [{n}] {especie:<12} │ {ajustar_ancho(tipos_str, 26)} ║")
    print(" ╚" + "═" * 48 + "╝")

    # Capturamos y validamos la elección del Pokémon inicial (1 a 3)
    while True:
        try:
            op = int(input("\n Elige tu inicial (1-3): "))
            if op in INICIALES:
                break
            print(" ❌ Opción no válida. Elige 1, 2 o 3.")
        except ValueError:
            print(" Debes introducir un número entero.")

    # Creamos el Pokémon inicial (Nivel 5)
    especie = INICIALES[op]

    # --- OPCIÓN DE APODO AL PRIMER POKéMON (1 A 15 CARACTERES) ---
    apodo = None
    resp = input(f"\n ✏️  ¿Quieres ponerle un apodo a tu {especie}? [s/N]: ").strip().lower()
    if resp == "s":
        while True:
            entrada_apodo = input(" 👉 Escribe el apodo (1 a 15 caracteres): ").strip()
            if isinstance(entrada_apodo, str) and 1 <= len(entrada_apodo) <= 15:
                apodo = entrada_apodo
                break
            print(" ⚠️  Apodo inválido: debe tener entre 1 y 15 caracteres.")

    mi_pokemon = PokemonJugador(especie, 5, entrenador=nombre_entrenador, apodo=apodo)
    equipo = Equipo([mi_pokemon])
    mochila = Mochila(dinero=DINERO_INICIAL) # Saldo inicial oficial Gen III: 3000 ₽

    # Kit de bienvenida para comenzar la exploración
    mochila.agregar("pokeball", 5)
    mochila.agregar("pocion", 3)

    imprimir_con_retraso(f"\n 🎉 ¡Felicidades, {nombre_entrenador}!")
    imprimir_con_retraso(f"\n ⭐ ¡{mi_pokemon.nombre_visible} ({especie}, Nv.5 - Nat. {mi_pokemon.naturaleza}) será tu compañero!\n")

    # Guardamos inmediatamente la partida inicial para no perder el progreso
    try:
        guardar_partida(nombre_entrenador, equipo, mochila)
        imprimir_con_retraso("\n💾 ¡Partida guardada correctamente!\n")
    except ErrorGuardado as error:
        imprimir_con_retraso(f"\n❌ No se pudo guardar la partida: {error}\n")


    return nombre_entrenador, equipo, mochila