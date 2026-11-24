'''Motor de combates por turnos para Pokémon Gen III (Rojo Fuego / Verde Hoja).

Gestiona la selección de acciones y movimientos, orden de turno por prioridad
y velocidad, cálculo de daño físico/especial, estados alterados, captura,
experiencia y enfrentamientos contra Pokémon salvajes o entrenadores NPC.
'''

import random
import time
from interfaz.mensajes import (
    ajustar_ancho,
    imprimir_con_retraso,
    mostrar_barras,
    resumen_movimiento,
)
from modelos.movimiento import Movimiento
from sistemas.efectos import (
    aplicar_danio_fin_turno,
    aplicar_efectos_movimiento,
    evaluar_estado_pre_turno,
)
from sistemas.estadisticas import efectividad_tipos
from sistemas.experiencia import calcular_exp_ganada, comprobar_subida_nivel

# Movimiento de respaldo oficial Gen III cuando un Pokémon no tiene PP útiles
MOVIMIENTO_FORCEJEO = Movimiento(
    nombre="Forcejeo",
    tipo="normal",
    categoria="fisico",
    potencia=50,
    precision=100,
    pp=1,
)


def _elegir_movimiento(pokemon):
    '''Muestra los movimientos conocidos del Pokémon y solicita elegir uno.

    Si todos los movimientos del Pokémon tienen 0 PP, devuelve automáticamente
    `MOVIMIENTO_FORCEJEO` según las reglas de Tercera Generación.

    Args:
        pokemon: Instancia del Pokémon aliado que va a atacar.

    Returns:
        Movimiento | None: Movimiento elegido, `MOVIMIENTO_FORCEJEO`, o `None`
        si el jugador cancela con `[0]`.
    '''
    if all(mov.pp <= 0 for mov in pokemon.movimientos):
        imprimir_con_retraso(
            f"\n ⚠️  ¡A {pokemon.nombre_visible} no le quedan PP en ningún movimiento!\n"
        )
        time.sleep(.5)
        return MOVIMIENTO_FORCEJEO

    imprimir_con_retraso(f"\n  ¡Adelante {pokemon.nombre_visible}!")
    time.sleep(.5)

    # Cuadro de movimientos al estilo de pantalla de batalla en consola
    print("\n" + " ╔" + "═" * 58 + "╗")
    titulo = f" ⚔️  MOVIMIENTOS DE {pokemon.nombre_visible.upper()}"
    print(f" ║{ajustar_ancho(titulo, 58)}║")
    print(" ╟" + "─" * 58 + "╢")

    for i, mov in enumerate(pokemon.movimientos, start=1):
        l1, l2 = resumen_movimiento(mov, prefijo=f"[{i}]")
        if mov.pp <= 0:
            l1 = ajustar_ancho(f" [{i}] {mov.nombre:<20} │ ❌ SIN PP", 58)
        print(f" ║{l1}║")
        print(f" ║{l2}║")
        if i < len(pokemon.movimientos):
            print(" ║" + " ·" * 29 + "║")

    print(" ╟" + "─" * 58 + "╢")
    print(f" ║{ajustar_ancho(' [X] 🔙 Volver al menú de combate', 58)}║")
    print(" ╚" + "═" * 58 + "╝")
    time.sleep(.5)

    while True:
        entrada = input(" 👉 Elige un movimiento: ").strip().lower()

        if entrada == "x":
            return None

        if not entrada.isdigit():
            print(" ❌ Introduce un número válido o pulsa [X] para volver.")
            continue

        op = int(entrada)
        if 1 <= op <= len(pokemon.movimientos):
            elegido = pokemon.movimientos[op - 1]
            if elegido.pp <= 0:
                print(f" ⚠️  ¡A {elegido.nombre} no le quedan PP! Elige otro.")
                continue
            return elegido

        print(" ❌ Movimiento fuera de rango. Selecciona uno de la lista o [X].")


def _ejecutar_ataque(atacante, defensor, movimiento, es_rival: bool = False) -> None:
    '''Ejecuta un movimiento completo sobre el defensor aplicando reglas Gen III.

    Evalúa estados previos al turno, descuenta 1 PP, comprueba precisión frente
    a evasión, aplica efectos de estado/estadísticas o daño y gestiona retroceso.

    Args:
        atacante: Pokémon que realiza el movimiento.
        defensor: Pokémon objetivo del movimiento.
        movimiento: Instancia de `Movimiento` a ejecutar.
        es_rival: `True` si el atacante pertenece al rival; `False` si es aliado.
    '''
    quien = (
        f"El {atacante.nombre_visible} rival" if es_rival else atacante.nombre_visible
    )

    # 1) Estados persistentes o volátiles que impiden actuar en el turno
    puede_moverse, msgs_pre = evaluar_estado_pre_turno(atacante)
    for msg in msgs_pre:
        imprimir_con_retraso(f"\n {msg}\n")
    if not puede_moverse:
        return

    # 2) Consumo de 1 PP (en Gen III se gasta al usar el movimiento aunque falle)
    if movimiento.pp > 0:
        movimiento.pp -= 1

    imprimir_con_retraso(f"\n ⚔️  {quien} usó {movimiento.nombre}!")
    time.sleep(.5)

    # 3) Precisión efectiva del atacante contra evasión del defensor
    ratio_acierto = atacante.mult_precision / defensor.mult_evasion
    if not movimiento.impacta(ratio_acierto):
        imprimir_con_retraso(f" ¡El ataque de {atacante.nombre_visible} falló!")
        return

    # 4) Movimientos de categoría estado
    if movimiento.categoria == "estado":
        efectos_msgs = aplicar_efectos_movimiento(atacante, defensor, movimiento)
        if efectos_msgs:
            for msg in efectos_msgs:
                imprimir_con_retraso(f" {msg}\n")
        else:
            imprimir_con_retraso(" Pero no tuvo efecto...")
        return

    # 5) Movimientos ofensivos (físicos o especiales)
    danio, efectividad = calcular_danio(atacante, movimiento, defensor)
    if efectividad == 0:
        imprimir_con_retraso(f" No afecta a {defensor.nombre_visible}...\n")
        return

    defensor.recibir_danio(danio)

    if efectividad > 1:
        imprimir_con_retraso(" ¡Es muy eficaz!")
    elif efectividad < 1:
        imprimir_con_retraso(" No es muy eficaz...")
    else:
        imprimir_con_retraso(" ¡El ataque impactó!")

    # Efectos secundarios si el defensor sigue en pie
    if defensor.salud_actual > 0:
        for msg in aplicar_efectos_movimiento(atacante, defensor, movimiento):
            imprimir_con_retraso(f" {msg}\n")

    # Retroceso oficial de Forcejeo (1/4 de los PS máximos del atacante)
    if movimiento.nombre == "Forcejeo":
        retroceso = max(1, atacante.salud_maxima // 4)
        atacante.recibir_danio(retroceso)
        imprimir_con_retraso(
            f"\n 💥 ¡{atacante.nombre_visible} se hirió a sí mismo por el retroceso!\n"
        )


def calcular_danio(atacante, movimiento, objetivo) -> tuple[int, float]:
    '''Calcula el daño de un movimiento ofensivo según las reglas de Gen III.

    Aplica categoría física/especial, efectividad de tipos, STAB (1.5x si comparte
    tipo) y variación aleatoria entre 0.85 y 1.00.

    Args:
        atacante: Pokémon que ejecuta el movimiento.
        movimiento: Instancia de `Movimiento`.
        objetivo: Pokémon que recibe el ataque.

    Returns:
        tuple[int, float]: `(danio_final, multiplicador_efectividad)`.
    '''
    if movimiento.categoria == "estado" or movimiento.potencia == 0:
        return 0, 1.0

    efectividad = efectividad_tipos(movimiento.tipo, objetivo.tipos)
    if efectividad == 0:
        return 0, 0.0

    if movimiento.categoria == "fisico":
        ataque, defensa = atacante.ataque, objetivo.defensa
    else:
        ataque, defensa = atacante.ataque_especial, objetivo.defensa_especial

    factor_nivel = (2 * atacante.nivel) // 5 + 2
    danio_base = (
        (factor_nivel * ataque * movimiento.potencia) // max(1, defensa)
    ) // 50 + 2

    stab = 1.5 if movimiento.tipo in atacante.tipos else 1.0
    variacion = random.uniform(0.85, 1.0)

    danio_final = max(1, int(danio_base * efectividad * stab * variacion))
    return danio_final, efectividad


def _elegir_pokemon_activo(equipo):
    '''Muestra los Pokémon conscientes del equipo y solicita elegir uno.

    Args:
        equipo: Instancia de `Equipo` del jugador.

    Returns:
        Pokemon | None: Pokémon consciente elegido, o `None` si no queda ninguno.
    '''
    disponibles = {
        i: pokemon
        for i, pokemon in enumerate(equipo.pokemon)
        if pokemon.salud_actual > 0
    }
    if not disponibles:
        return None

    print("\n" + " ╔" + "═" * 52 + "╗")
    print(f" ║{ajustar_ancho('  👥 EQUIPO DISPONIBLE', 52)}║")
    print(" ╠" + "═" * 52 + "╣")

    for op, pokemon in disponibles.items():
        estado_icon = "❤️" if pokemon.salud_actual > 0 else "💀"
        fila_pkmn = (
            f"  [{op + 1}] 🔴 {pokemon.nombre_visible:<14} "
            f"Nv.{pokemon.nivel:<3} │ {estado_icon}  PS {pokemon.salud_actual:>3}/{pokemon.salud_maxima:<3}"
        )
        print(f" ║{ajustar_ancho(fila_pkmn, 52)}║")

    print(" ╚" + "═" * 52 + "╝")

    while True:
        try:
            op = int(input(" 👉 Elige el Pokémon activo: ")) - 1
            if op in disponibles:
                return equipo.pokemon[op]
        except ValueError:
            pass
        print(" ❌ Opción no válida o Pokémon debilitado.")


def _usar_objeto_en_combate(equipo, mochila, rival, nombre_entrenador: str) -> tuple[bool, bool]:
    '''Muestra la mochila en combate y aplica el objeto elegido si es válido.

    Args:
        equipo: Instancia de `Equipo` del jugador.
        mochila: Instancia de `Mochila` del jugador.
        rival: Pokémon oponente actual.
        nombre_entrenador: Nombre del entrenador jugador.

    Returns:
        tuple[bool, bool]: `(turno_consumido, enemigo_capturado)`.
    '''
    disponibles = [
        (obj, cant)
        for obj, cant in mochila.listar()
        if cant > 0
    ]
    if not disponibles:
        print(" La mochila está vacía.")
        return False, False

    print("\n" + " ╔" + "═" * 52 + "╗")
    print(f" ║{ajustar_ancho('  🎒 MOCHILA EN COMBATE', 52)}║")
    print(" ╠" + "═" * 52 + "╣")
    print(f" ║{ajustar_ancho('   Nº  │ OBJETO               │ CANTIDAD', 52)}║")
    print(" ╟" + "─" * 52 + "╢")

    for i, (obj, cant) in enumerate(disponibles, start=1):
        fila_obj = f"  [{i:<2}] │ {obj.nombre:<20} │ 📦 x{cant:<3}"
        print(f" ║{ajustar_ancho(fila_obj, 52)}║")

    print(" ╟" + "─" * 52 + "╢")
    print(f" ║{ajustar_ancho('  [X]  │ 🔙 Cancelar', 52)}║")
    print(" ╚" + "═" * 52 + "╝")

    entrada = input(" 👉 Elige un objeto: ").strip().lower()
    if entrada == "x":
        return False, False

    if not entrada.isdigit() or not 1 <= int(entrada) <= len(disponibles):
        print(" ⚠️ Opción no válida.")
        return False, False

    objeto = disponibles[int(entrada) - 1][0]
    objetivo = None
    if objeto.requiere_objetivo:
        objetivo = _elegir_objetivo(equipo, incluir_debilitados=True)
        if objetivo is None:
            return False, False

    contexto = {
        "equipo": equipo,
        "mochila": mochila,
        "rival": rival,
        "objetivo": objetivo,
        "nombre_entrenador": nombre_entrenador,
    }
    consumido, combate_terminado = objeto.usar(contexto)
    if consumido:
        mochila.quitar(objeto.identificador)
    return consumido, combate_terminado


def _elegir_objetivo(equipo, incluir_debilitados: bool = False):
    '''Permite seleccionar un objetivo del equipo, incluidos debilitados si aplica.'''
    disponibles = [
        (indice, pokemon)
        for indice, pokemon in enumerate(equipo.pokemon)
        if incluir_debilitados or pokemon.salud_actual > 0
    ]
    if not disponibles:
        print(" No hay Pokémon disponibles como objetivo.")
        return None

    for indice, pokemon in disponibles:
        estado = "💀" if pokemon.salud_actual <= 0 else "❤️"
        print(
            f" [{indice + 1}] {estado} {pokemon.nombre_visible} "
            f"PS {pokemon.salud_actual}/{pokemon.salud_maxima}"
        )
    while True:
        entrada = input(" 👉 Elige el Pokémon objetivo: ").strip()
        if entrada.isdigit():
            indice = int(entrada) - 1
            for posicion, pokemon in disponibles:
                if posicion == indice:
                    return pokemon
        print(" ❌ Opción no válida.")


def _notificar_derrota_si_no_hay_recursos(equipo, mochila) -> None:
    '''Anuncia una derrota cuando no hay aliados conscientes ni reanimación.'''
    equipo_completo = equipo.pokemon + equipo.pc
    hay_pokemon = any(pokemon.salud_actual > 0 for pokemon in equipo_completo)
    if not hay_pokemon and mochila.cantidad("revivir") == 0:
        imprimir_con_retraso(
            "\n 💀 DERROTA: no quedan Pokémon conscientes ni recursos para continuar.\n"
        )


def _ganar_experiencia(pokemon, rival) -> None:
    '''Otorga experiencia al vencer a un rival y narra subidas de nivel.'''
    exp_ganada = calcular_exp_ganada(rival)
    pokemon.exp_actual += exp_ganada
    imprimir_con_retraso(
        f" ✨ ¡{pokemon.nombre_visible} ganó {exp_ganada} puntos de EXP!\n"
    )

    for evento in comprobar_subida_nivel(pokemon):
        imprimir_con_retraso(f" {evento}\n")
        time.sleep(1.0)


def _turno_combate(equipo, rival, mochila, capturable: bool, nombre_entrenador: str):
    '''Ejecuta una ronda de combate respetando prioridades y velocidad Gen III.

    Args:
        equipo: Instancia de `Equipo` del jugador.
        rival: Pokémon oponente actual.
        mochila: Instancia de `Mochila` del jugador.
        capturable: `True` en encuentros salvajes; `False` contra entrenadores.
        nombre_entrenador: Nombre del entrenador jugador.

    Returns:
        str | None: `'capturado'`, `'huida'`, o `None` para continuar.
    '''
    jugador = next((p for p in equipo.pokemon if p.salud_actual > 0), None)
    if jugador is None:
        return None

    while True:
        opcion_huir = "🏃 Huir" if capturable else "🚫 Huir (Entrenador)"
        col_1_fila_1 = ajustar_ancho(" [1] 💥 Atacar", 28)
        col_2_fila_1 = ajustar_ancho(" [2] 🎒 Mochila", 29)
        col_1_fila_2 = ajustar_ancho(" [3] 🔄 Pokémon", 28)
        col_2_fila_2 = ajustar_ancho(f" [4] {opcion_huir}", 29)

        print("╔" + "═" * 58 + "╗")
        print(f"║{ajustar_ancho(f' ⚔️  ¿Qué hará {jugador.nombre_visible}?', 58)}║")
        print("╠" + "═" * 28 + "╤" + "═" * 29 + "╣")
        print(f"║{col_1_fila_1}│{col_2_fila_1}║")
        print("╟" + "─" * 28 + "┼" + "─" * 29 + "╢")
        print(f"║{col_1_fila_2}│{col_2_fila_2}║")
        print("╚" + "═" * 28 + "╧" + "═" * 29 + "╝")
        op = input(" 👉 Elige una acción: ").strip()

        # --- 1) ATACAR ---
        if op == "1":
            mov_jugador = _elegir_movimiento(jugador)
            if mov_jugador is None:
                continue

            movs_rival = [m for m in rival.movimientos if m.pp > 0]
            mov_rival = random.choice(movs_rival) if movs_rival else MOVIMIENTO_FORCEJEO

            # Orden Gen III: Prioridad del movimiento > Velocidad > Azar
            clave_j = (mov_jugador.prioridad, jugador.velocidad, random.random())
            clave_r = (mov_rival.prioridad, rival.velocidad, random.random())

            participantes = [
                (clave_j, jugador, rival, mov_jugador, False),
                (clave_r, rival, jugador, mov_rival, True),
            ]
            participantes.sort(key=lambda turno: turno[0], reverse=True)

            for _, atacante, defensor, mov, es_rival in participantes:
                if atacante.salud_actual <= 0:
                    continue
                imprimir_con_retraso(atacante.preparar_turno())
                _ejecutar_ataque(atacante, defensor, mov, es_rival=es_rival)
                mostrar_barras(jugador, rival)
                time.sleep(.8)

                if defensor.salud_actual <= 0:
                    imprimir_con_retraso(f"\n 💀 ¡{defensor.nombre_visible} se debilitó!")
                    if defensor is rival:
                        _ganar_experiencia(jugador, rival)
                    else:
                        siguiente = _elegir_pokemon_activo(equipo)
                        if siguiente:
                            print(f" ¡Adelante, {siguiente.nombre_visible}!")
                    return None

            # Daño residual al cierre de la ronda (quemadura / veneno)
            for combatiente in (jugador, rival):
                for msg in aplicar_danio_fin_turno(combatiente):
                    imprimir_con_retraso(f"\n {msg}\n")
                    mostrar_barras(jugador, rival)
                    if combatiente.salud_actual <= 0:
                        print(f"\n 💀 ¡{combatiente.nombre_visible} se debilitó!")
                        if combatiente is rival:
                            _ganar_experiencia(jugador, rival)
                        else:
                            siguiente = _elegir_pokemon_activo(equipo)
                            if siguiente:
                                print(f" ¡Adelante, {siguiente.nombre_visible}!")
                        return None

            return None

        # --- 2) MOCHILA ---
        elif op == "2":
            consumido, capturado = _usar_objeto_en_combate(
                equipo, mochila, rival, nombre_entrenador
            )
            if not consumido:
                continue
            if capturado:
                return "capturado"
            break

        # --- 3) CAMBIAR POKÉMON ---
        elif op == "3":
            nuevo = _elegir_pokemon_activo(equipo)
            if nuevo is None:
                return None
            if nuevo is jugador:
                print(" ⚔️ Ese Pokémon ya está en combate.")
                continue
            indice_nuevo = equipo.pokemon.index(nuevo)
            jugador.resetear_combate()
            jugador = nuevo
            equipo.cambiar_activo(indice_nuevo)
            print(f" ¡Adelante, {jugador.nombre_visible}!")
            break

        # --- 4) HUIR ---
        elif op == "4":
            if capturable:
                print(" 🏃 Escapaste del encuentro.")
                return "huida"
            print(" ❌ ¡No puedes huir de un combate contra un entrenador!")
        else:
            print(" ❌ Opción no válida. Elige entre 1 y 4.")

    # Turno del rival tras usar objeto o cambiar Pokémon
    movs_rival = [m for m in rival.movimientos if m.pp > 0]
    mov_rival = random.choice(movs_rival) if movs_rival else MOVIMIENTO_FORCEJEO
    _ejecutar_ataque(rival, jugador, mov_rival, es_rival=True)
    mostrar_barras(jugador, rival)
    time.sleep(.8)

    if jugador.salud_actual <= 0:
        print(f"\n 💀 ¡{jugador.nombre_visible} se debilitó!")
        siguiente = _elegir_pokemon_activo(equipo)
        if siguiente:
            print(f" ¡Adelante, {siguiente.nombre_visible}!")
    return None


def combatir_salvaje(equipo, mochila, salvaje, nombre_entrenador: str) -> bool:
    '''Gestiona un encuentro completo contra un Pokémon salvaje (estilo FRLG).

    Args:
        equipo: Instancia de `Equipo` del jugador.
        mochila: Instancia de `Mochila` del jugador.
        salvaje: Instancia de `PokemonSalvaje`.
        nombre_entrenador: Nombre del entrenador jugador.

    Returns:
        bool: `True` si se capturó o venció al salvaje; `False` si huyó o perdió.
    '''
    for p in equipo.pokemon:
        p.resetear_combate()
    salvaje.resetear_combate()

    print(f" 🌿 ¡Un {salvaje.especie} salvaje apareció (Nv.{salvaje.nivel})!")
    mostrar_barras(equipo.activo, salvaje)

    while salvaje.salud_actual > 0 and any(p.salud_actual > 0 for p in equipo.pokemon):
        resultado = _turno_combate(
            equipo,
            salvaje,
            mochila,
            capturable=True,
            nombre_entrenador=nombre_entrenador,
        )
        if resultado:
            for p in equipo.pokemon:
                p.resetear_combate()
            return resultado == "capturado"

    for p in equipo.pokemon:
        p.resetear_combate()

    if salvaje.salud_actual <= 0:
        imprimir_con_retraso(f" 🥳 ¡{salvaje.especie} salvaje se debilitó!\n")
        time.sleep(.5)
        return True

    _notificar_derrota_si_no_hay_recursos(equipo, mochila)
    imprimir_con_retraso(
        "\n 💀 ¡No te quedan Pokémon disponibles! Corres al Centro Pokémon...\n"
    )
    return False


def combatir_entrenador(equipo, mochila, npc, nombre_entrenador: str) -> bool:
    '''Gestiona un combate completo contra un `EntrenadorNPC` o subclase.

    Args:
        equipo: Instancia de `Equipo` del jugador.
        mochila: Instancia de `Mochila` del jugador.
        npc: Instancia de `EntrenadorNPC` (`Cazabichos`, `LiderGimnasio`, etc.).
        nombre_entrenador: Nombre del entrenador jugador.

    Returns:
        bool: `True` si el jugador derrota todo el equipo del NPC; `False` si cae.
    '''
    for p in equipo.pokemon:
        p.resetear_combate()

    frase_inicio = getattr(npc, "frase_inicio", f"¡{npc.nombre} te desafía a un combate!")
    imprimir_con_retraso(f" 🧢 {npc.nombre}: {frase_inicio}\n")

    # Prepara el equipo del rival con PS, PP y estados limpios
    for pokemon_npc in npc.equipo:
        pokemon_npc.estado_alterado = None
        pokemon_npc.turnos_estado = 0
        pokemon_npc.curar()
        pokemon_npc.restaurar_pp_todos()
        pokemon_npc.resetear_combate()

    for rival in npc.equipo:
        imprimir_con_retraso(
            f"\n 🧢 {npc.nombre} envía a {rival.especie} (Nv.{rival.nivel})!"
        )
        mostrar_barras(equipo.activo, rival)

        while rival.salud_actual > 0 and any(p.salud_actual > 0 for p in equipo.pokemon):
            _turno_combate(
                equipo,
                rival,
                mochila,
                capturable=False,
                nombre_entrenador=nombre_entrenador,
            )

        if not any(p.salud_actual > 0 for p in equipo.pokemon):
            for p in equipo.pokemon:
                p.resetear_combate()
            imprimir_con_retraso(
                "\n 💀 Tu equipo quedó debilitado. Visita un Centro Pokémon."
            )
            if getattr(npc, "es_desafio_final", False):
                imprimir_con_retraso(
                    "\n 💀 DERROTA: has caído ante el Líder de Gimnasio.\n"
                )
            else:
                _notificar_derrota_si_no_hay_recursos(equipo, mochila)
            return False

    for p in equipo.pokemon:
        p.resetear_combate()

    frase_derrota = getattr(
        npc, "frase_derrota", "¡Has sido más fuerte de lo que esperaba!"
    )
    imprimir_con_retraso(f"\n 🧢 {npc.nombre}: {frase_derrota}\n")
    mochila.ganar(npc.recompensa)
    print(f" 🙌 ¡Venciste a {npc.nombre} y ganaste {npc.recompensa} ₽!")

    medalla = npc.entregar_medalla(mochila)
    if medalla:
        print(f" 🏅 ¡Obtuviste la {medalla}!")
    if getattr(npc, "es_desafio_final", False):
        imprimir_con_retraso(
            "\n 🏆 ¡VICTORIA! Has completado el desafío de Kanto\n"
        )

    return True