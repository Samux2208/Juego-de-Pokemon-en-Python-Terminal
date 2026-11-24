import random
import time
from servicios.catalogos import DICCIONARIO_POKEMON
from modelos.pokemon import PokemonAtrapado
from interfaz.mensajes import imprimir_con_retraso

# == MECÁNICA DE CAPTURA DE POKéMON ==========================
# _gestionar_captura() | Ejecuta la fórmula Gen III, simula agitamientos y gestiona el destino.
# ============================================================

def _gestionar_captura(salvaje, equipo, mochila, bonus_ball=1.0,
                       nombre_entrenador="Entrenador"):
    '''Gestiona el intento de captura con la fórmula oficial de Gen III (Rojo Fuego).
    
    Calcula el ratio modificado según los PS restantes, el ratio oficial de la especie
    en DICCIONARIO_POKEMON y el bonus de la Poké Ball; simula los 4 agitamientos y
    transfiere el Pokémon capturado al equipo activo o al PC.
    '''
    # Obtenemos el ratio oficial de la especie (3 a 255) y los PS del salvaje
    ratio_especie = DICCIONARIO_POKEMON[salvaje.especie]["ratio_captura"]
    ps_max = max(1, salvaje.salud_maxima)
    ps_act = max(1, salvaje.salud_actual)

    # Fórmula oficial de Gen III para el valor de captura modificado 'a'
    a = int(((3 * ps_max - 2 * ps_act) * ratio_especie * bonus_ball) / (3 * ps_max))
    a = max(1, a)

    # Evaluación de los 4 agitamientos oficiales de la Poké Ball
    if a >= 255:
        agitamientos = 4  # Captura garantizada sin necesidad de agitamientos
    else:
        # Umbral oficial 'b' de Pokémon Rojo Fuego (escala de 0 a 65535)
        b = int(1048560 / ((16711680 / a) ** 0.25))
        agitamientos = 0
        for _ in range(4):
            if random.randint(0, 65535) < b:
                agitamientos += 1
            else:
                break  # Se libera en cuanto falla una comprobación

    # Narración visual de los movimientos de la Poké Ball en combate
    for _ in range(min(3, agitamientos)):
        imprimir_con_retraso(" *La Poké Ball se mueve...*\n")
        time.sleep(.6)

    if agitamientos < 4:
        mensajes_escape = [
            f" ¡Oh no! ¡{salvaje.nombre} se ha liberado!",
            f" ¡Qué pena! ¡Parecía que {salvaje.nombre} estaba atrapado!",
            f" ¡Aaargh! ¡Casi lo tenías!",
            f" ¡Uy! ¡{salvaje.nombre} se escapó por los pelos!",
        ]
        imprimir_con_retraso(f"{mensajes_escape[agitamientos]}\n")
        return False

    # ¡Captura exitosa! (Superó las 4 comprobaciones)
    imprimir_con_retraso(f" ¡Ya está! ¡{salvaje.especie} ha sido atrapado! 🎉\n")

    # Solicitud opcional de apodo (validando entre 1 y 15 caracteres)
    apodo = None
    if input(f" ¡Capturaste a {salvaje.especie}! ¿Quieres ponerle un apodo? [s/N]: ").strip().lower() == "s":
        apodo = input(" Escribe el apodo (máximo 15 caracteres): ").strip()
        while not apodo or len(apodo) > 15:
            apodo = input(" Apodo inválido. Introduce entre 1 y 15 caracteres: ").strip()

    # Creamos la instancia de PokemonAtrapado conservando su estado de salud y EXP
    capturado = PokemonAtrapado(
        salvaje.especie, salvaje.nivel,
        entrenador=nombre_entrenador,
        apodo=apodo
    )
    capturado.salud_actual = salvaje.salud_actual
    capturado.exp_actual = salvaje.exp_actual

    # Si hay espacio en el equipo (< 6), entra directamente
    if equipo.agregar(capturado):
        print(f" {capturado.nombre_visible} se unió a tu equipo.")
        return True

    # Si el equipo está lleno (6/6), el jugador decide si enviarlo al PC o reemplazar
    print("\n🎒 ¡Tu equipo está lleno! ¿Qué quieres hacer?")
    print(" [1] 💻 Enviar al PC  |  [2] 🔄 Reemplazar un Pokémon del equipo")
    while True:
        op = input("\n 👉 Elige una opción (1 o 2): ").strip()
        if op == "1":
            equipo.almacenar_en_pc(capturado)
            print(f"\n💻 ¡Listo! {capturado.nombre_visible} fue enviado al PC.")
            return True
        if op == "2":
            print("\n📋 Tu equipo actual:")
            for i, pokemon in enumerate(equipo.pokemon, start=1):
                print(f" [{i}] 🐾 {pokemon.nombre_visible} Nv.{pokemon.nivel}")
            try:
                i = int(input("\n🔄 Escribe el número del Pokémon a reemplazar: ")) - 1
            except ValueError:
                print("⚠️ Por favor, ingresa solo un número válido.")
                continue
            if equipo.reemplazar(i, capturado):
                print(f"\n✨ ¡Cambio realizado! {capturado.nombre_visible} ocupa el lugar en el equipo; "
                      "💻 el Pokémon anterior fue enviado al PC.")
                return True
        print("❌ Opción no válida. Intenta de nuevo.")