import random
import time
from servicios.repositorio import DICCIONARIO_POKEMON
from modelos.pokemon import PokemonSalvaje
from modelos.objeto import Pokeball, Pocion
from sistemas.captura import _gestionar_captura
from sistemas.estadisticas import efectividad_tipos
from sistemas.experiencia import (
    calcular_exp_ganada, comprobar_subida_nivel
)
from sistemas.efectos import (
    evaluar_estado_pre_turno,
    aplicar_efectos_movimiento,
    aplicar_danio_fin_turno,
)
from interfaz.mensajes import (
    imprimir_con_retraso,
    mostrar_barras,
    resumen_movimiento,
    ajustar_ancho,
)
from modelos.movimiento import Movimiento

MOVIMIENTO_FORCEJEO = Movimiento(
    nombre="Forcejeo",
    tipo="normal",
    categoria="fisico",
    potencia=50,
    precision=100,
    pp=1,
)

def _elegir_movimiento(pokemon):
        '''Muestra los movimientos conocidos del Pokémon y solicita elegir uno.'''
        # Si todos los movimientos tienen 0 PP, usa Forcejeo automáticamente (regla oficial Gen III)
        if all(mov.pp <= 0 for mov in pokemon.movimientos):
            imprimir_con_retraso(f"\n ⚠️  ¡A {pokemon.nombre_visible} no le quedan PP en ningún movimiento!\n")
            time.sleep(0.5)
            return MOVIMIENTO_FORCEJEO

        imprimir_con_retraso(f"\n  ¡Adelante {pokemon.nombre_visible}!")
        time.sleep(.5)
        
        # MOSTRAMOS LA LISTA DE MOVIMIENTOS EN EL CUADRO DE 58 COLUMNAS
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
        print(" ╚" + "═" * 58 + "╝")
        time.sleep(.5)
        
        # BUCLE SEGURO DE CAPTURA DE DATOS
        while True:
            try:
                # Solicitamos la opción al jugador
                op = int(input(" 👉 Elige un movimiento: "))
                # Verificamos que el número ingresado esté dentro del menú
                if 1 <= op <= len(pokemon.movimientos):
                    elegido = pokemon.movimientos[op - 1]
                    if elegido.pp <= 0:
                        print(f" ⚠️  ¡A {elegido.nombre} no le quedan PP! Elige otro.")
                        continue
                    return elegido
                print(" ❌ Movimiento fuera de rango. Selecciona uno de la lista.")
            except ValueError:
                print(" ❌ Introduce un número válido.")


def _ejecutar_ataque(atacante, defensor, movimiento, es_rival=False):
        '''Ejecuta un movimiento completo (reemplaza al antiguo Pokemon.atacar).'''
        # Identificamos quién ataca usando su nombre visible (apodo o especie)
        quien = f"El {atacante.nombre_visible} rival" if es_rival else atacante.nombre_visible

        # Evaluar estados que impiden actuar (Sueño, Congelación, Parálisis, Confusión)
        puede_moverse, msgs_pre = evaluar_estado_pre_turno(atacante)
        for msg in msgs_pre:
            imprimir_con_retraso(f"\n {msg}\n")
        if not puede_moverse:
            return

        # Descontamos 1 PP al ejecutar el movimiento (se gasta incluso si el ataque falla)
        if movimiento.pp > 0:
            movimiento.pp -= 1
        
        imprimir_con_retraso(f"\n ⚔️  {quien} usó {movimiento.nombre}!")
        time.sleep(.5)

        # Comprobar precisión del atacante vs evasión del defensor
        ratio_acierto = atacante.mult_precision / defensor.mult_evasion
        if not movimiento.impacta(ratio_acierto):
            imprimir_con_retraso(f" ¡El ataque de {atacante.nombre_visible} falló!\n")
            return

        # Movimientos de categoría Estado (Gruñido, Onda Trueno, Somnífero, Danza Espada, etc.)
        if movimiento.categoria == "estado":
            efectos_msgs = aplicar_efectos_movimiento(atacante, defensor, movimiento)
            if efectos_msgs:
                for msg in efectos_msgs:
                    imprimir_con_retraso(f" {msg}\n")
            else:
                imprimir_con_retraso(" Pero no tuvó efecto...")
            return

        # Movimientos ofensivos (Físicos o Especiales)
        danio, efectividad = calcular_danio(atacante, movimiento, defensor)
        if efectividad == 0:
            imprimir_con_retraso(f" No afecta a {defensor.nombre_visible}...\n")
            return

        # Aplicamos el daño usando la interfaz encapsulada del defensor
        defensor.recibir_danio(danio)

        # Notificamos al jugador el resultado de la efectividad
        if efectividad > 1:
            imprimir_con_retraso(f" ¡Es muy eficaz!")
        elif efectividad < 1:
            imprimir_con_retraso(f" No es muy eficaz...")
        else:
            imprimir_con_retraso(f" ¡El ataque impactó!")

        # Efectos secundarios de movimientos con daño (ej. Ascuas puede quemar, Rayo puede paralizar)
        if defensor.salud_actual > 0:
            for msg in aplicar_efectos_movimiento(atacante, defensor, movimiento):
                imprimir_con_retraso(f" {msg}\n")

        # Retroceso oficial de Forcejeo (1/4 de los PS máximos del atacante)
        if movimiento.nombre == "Forcejeo":
            retroceso = max(1, atacante.salud_maxima // 4)
            atacante.recibir_danio(retroceso)
            imprimir_con_retraso(f"\n 💥 ¡{atacante.nombre_visible} se hirió a sí mismo por el retroceso!\n")

def calcular_danio(atacante, movimiento, objetivo):
        '''Calcula el daño infligido sobre un objetivo bajo las reglas de Gen III.
        
        Aplica categoría (físico/especial), bonificación por mismo tipo (STAB),
        efectividad elemental y variación aleatoria (85% - 100%).
        
        Devuelve una tupla: (danio_final, mult_efectividad).
        '''
        if movimiento.categoria == "estado" or movimiento.potencia == 0:
            return 0, 1.0
        
        # Comprobamos inmunidad y efectividad elemental
        efectividad = efectividad_tipos(movimiento.tipo, objetivo.tipos)
        if efectividad == 0:
            return 0, 0.0 # El objetivo es inmune a este tipo de ataque

        # Elegimos ataque y defensa según la categoría del movimiento
        if movimiento.categoria == "fisico":
            ataque, defensa = atacante.ataque, objetivo.defensa
        else:
            ataque, defensa = atacante.ataque_especial, objetivo.defensa_especial
        
        # Calculamos el daño base con la fórmula oficial (protegiendo división por cero)
        factor_nivel = (2 * atacante.nivel) // 5 + 2
        danio_base = ((factor_nivel * ataque * movimiento.potencia) // max(1, defensa)) // 50 + 2

        # Aplicamos STAB (+50% si comparte tipo) y variación aleatoria (0.85 a 1.0)
        stab = 1.5 if movimiento.tipo in atacante.tipos else 1.0
        variacion = random.uniform(0.85, 1.0)

        # Garantizamos al menos 1 PS de daño si el golpe no fue inmune
        danio_final = max(1, int(danio_base * efectividad * stab * variacion))
        return danio_final, efectividad

# == COMBATE DE EQUIPO, CAPTURA Y OBJETOS ===================
# _elegir_pokemon_activo() | Filtra Pokémon conscientes y solicita cuál enviar a luchar.
# _usar_objeto_en_combate() | Muestra la mochila y aplica el efecto del objeto elegido.
# ============================================================
def _elegir_pokemon_activo(equipo):
    '''Muestra los Pokémon conscientes del equipo y solicita elegir uno para combatir.
    
    Devuelve la instancia del Pokémon elegido, o None si todo el equipo está debilitado.
    '''
    # Mapeamos {indice_real: objeto_pokemon} solo para los miembros con PS > 0
    disponibles = {
        i: pokemon
        for i, pokemon in enumerate(equipo.pokemon)
        if pokemon.salud_actual > 0
    }
    # Si no queda ningún Pokémon consciente, el equipo fue derrotado
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
    
    # Bucle de validación hasta que el jugador elija un índice consciente válido
    while True:
        try:
            op = int(input(" 👉 Elige el Pokémon activo: ")) - 1
            if op in disponibles:
                return equipo.pokemon[op]
        except ValueError:
            pass
        print(" ❌ Opción no válida o Pokémon debilitado.")


def _usar_objeto_en_combate(equipo, mochila, rival, nombre_entrenador):
    '''Muestra la mochila en combate y ejecuta el efecto del objeto elegido.
    
    Maneja la lógica específica según el tipo de objeto (Pokeball o Pocion),
    descontándolo del inventario solo si su uso fue válido.
    
    Devuelve una tupla de booleanos: (turno_consumido, enemigo_capturado).
    '''
    # Filtramos solo los objetos con existencias disponibles
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

    # Capturamos y validamos la selección del jugador
    entrada = input(" 👉 Elige un objeto: ").strip().lower()

    if entrada == "x":
        return False, False

    if not entrada.isdigit() or not 1 <= int(entrada) <= len(disponibles):
        print(" ⚠️ Opción no válida.")
        return False, False

    op = int(entrada)

    # Extraemos la instancia del obj seleccionado
    objeto = disponibles[op - 1][0]

    # 1) CASO POKé BALL: Intento de captura
    if isinstance(objeto, Pokeball):
        # Verificamos que el oponente sea salvaje antes de lanzar la Poké Ball
        if not isinstance(rival, PokemonSalvaje):
            print(" 🚫 ¡El entrenador rival desvió la Poké Ball!")
            return True, False

        # Descontamos la Poké Ball inmediatamente (se gasta aunque el Pokémon escape)
        mochila.quitar(objeto.identificador)
        capturado = _gestionar_captura(rival, equipo, mochila, objeto.bonus, nombre_entrenador)
        return True, capturado

    # 2) CASO POCIÓN: Curación de un aliado
    if isinstance(objeto, Pocion):
        objetivo = _elegir_pokemon_activo(equipo)
        if objetivo is None:
            return False, False

        # Intentamos aplicar la curación (devuelve 0 si ya tiene la vida al máximo)
        curacion = objeto.usar(objetivo)
        if curacion:
            mochila.quitar(objeto.identificador)
            print(f"💚 {objetivo.nombre_visible} recuperó {curacion} PS.")
            return True, False
        return False, False

    # 3) CASO PIEDRA EVOLUTIVA U OTROS: Bloqueados en medio de la batalla
    print(" ⚠️  Ese objeto no se puede usar durante un combate.")
    return False, False


def _ganar_experiencia(pokemon, rival):
    '''Otorga experiencia al vencer y narra subidas de nivel, evoluciones y nuevos ataques.'''
    # Calculamos la experiencia con la fórmula oficial (garantizando un mínimo de 1 punto)
    exp_ganada = calcular_exp_ganada(rival)
    # Sumamos la experiencia al total acumulado del Pokémon aliado
    pokemon.exp_actual += exp_ganada
    imprimir_con_retraso(f" ✨ ¡{pokemon.nombre_visible} ganó {exp_ganada} puntos de EXP!\n")
    # Verificamos si alcanzó el umbral necesario para subir de nivel o evolucionar

    for evento in comprobar_subida_nivel(pokemon):
        imprimir_con_retraso(f" {evento}\n")
        time.sleep(1.0)


def _turno_combate(equipo, rival, mochila, capturable, nombre_entrenador):
    '''Ejecuta una ronda completa de combate respetando la prioridad oficial de Gen III.
    
    - Usar objeto o cambiar de Pokémon tiene prioridad inmediata antes del ataque rival.
    - Al elegir Atacar, se compara la velocidad de ambos combatientes (empates al 50%)
      y golpea primero el más rápido, deteniendo la ronda si uno cae debilitado.
    
    Devuelve:
        str | None: 'capturado' si se atrapó al salvaje, 'huida' si escapó,
                    o None si el combate continúa o terminó por debilitamiento.
    '''
    # Obtenemos el primer Pokémon consciente del equipo para liderar el turno
    jugador = next((p for p in equipo.pokemon if p.salud_actual > 0), None)
    if jugador is None:
        return None

    # Bucle de decisión del jugador
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

        # --- OPCIÓN 1: ATACAR (CON CÁLCULO DE PRIORIDAD DE VELOCIDAD) ---
        if op == "1":
            mov_jugador = _elegir_movimiento(jugador)
            movs_rival = [m for m in rival.movimientos if m.pp > 0]
            mov_rival = random.choice(movs_rival) if movs_rival else MOVIMIENTO_FORCEJEO

            # Orden oficial Gen III: Prioridad del movimiento > Velocidad > Azar
            clave_j = (mov_jugador.prioridad, jugador.velocidad, random.random())
            clave_r = (mov_rival.prioridad, rival.velocidad, random.random())

            # Ordenamos las acciones: (atacante, defensor, movimiento, es_rival)
            acciones = [
                (jugador, rival, mov_jugador, False),
                (rival, jugador, mov_rival, True),
            ]
            if clave_r > clave_j:
                acciones.reverse()

            # Ejecutamos los ataques en el orden calculado
            for atacante, defensor, mov, es_rival in acciones:
                if atacante.salud_actual <= 0:
                    continue
                _ejecutar_ataque(atacante, defensor, mov, es_rival=es_rival)
                mostrar_barras(jugador, rival)
                time.sleep(0.8)

                # Control de debilitamiento inmediato (corta el segundo ataque)
                if defensor.salud_actual <= 0:
                    imprimir_con_retraso(f"\n 💀 ¡{defensor.nombre_visible} se debilitó!")
                    if defensor is rival:
                        _ganar_experiencia(jugador, rival)
                    else:
                        siguiente = next((p for p in equipo.pokemon if p.salud_actual > 0), None)
                        if siguiente:
                            print(f" ¡Adelante, {siguiente.nombre_visible}!")
                    return None
            
            # Daño residual al final de la ronda (Quemadura / Veneno)
            for combatiente in (jugador, rival):
                for msg in aplicar_danio_fin_turno(combatiente):
                    imprimir_con_retraso(f"\n {msg}\n")
                    mostrar_barras(jugador, rival)
                    if combatiente.salud_actual <= 0:
                        print(f"\n 💀 ¡{combatiente.nombre_visible} se debilitó!")
                        if combatiente is rival:
                            _ganar_experiencia(jugador, rival)
                        else:
                            siguiente = next((p for p in equipo.pokemon if p.salud_actual > 0), None)
                            if siguiente:
                                print(f" ¡Adelante, {siguiente.nombre_visible}!")
                        return None

            return None  # Ambos atacaron y siguen conscientes; termina la ronda

        # --- OPCIÓN 2: USAR OBJETO (PRIORIDAD ALTA) ---
        elif op == "2":
            consumido, capturado = _usar_objeto_en_combate(equipo, mochila, rival, nombre_entrenador)
            if not consumido:
                continue # Canceló o no tuvo efecto; vuelve a elegir acción
            if capturado:
                return "capturado" # Sale del bucle para que el rival ejecute su turno
            break

        # --- OPCIÓN 3: CAMBIAR POKéMON ACTIVO (PRIORIDAD ALTA) ---
        elif op == "3":
            nuevo = _elegir_pokemon_activo(equipo)
            if nuevo is None:
                return None
            if nuevo is jugador:
                print(" ⚔️ Ese Pokémon ya está en combate.")
                continue
            jugador.resetear_combate()
            jugador = nuevo
            equipo.cambiar_activo(jugador)
            print(f" ¡Adelante, {jugador.nombre_visible}!")
            break  # Sale del bucle para que el rival golpee al Pokémon recién entrado

        # --- OPCIÓN 4: HUIR (SOLO ENCUENTROS SALVAJES) ---
        elif op == "4":
            if capturable:
                print(" 🏃 Escapaste del encuentro.")
                return "huida"
            print(" ❌ ¡No puedes huir de un combate contra un entrenador!")
        else:
            print(" ❌ Opción no válida. Elige entre 1 y 4.")


    # Turno del rival tras usar un objeto o cambiar de Pokémon
    movs_rival = [m for m in rival.movimientos if m.pp > 0]
    mov_rival = random.choice(movs_rival) if movs_rival else MOVIMIENTO_FORCEJEO
    _ejecutar_ataque(rival, jugador, mov_rival, es_rival=True)
    mostrar_barras(jugador, rival)
    time.sleep(0.8)

    if jugador.salud_actual <= 0:
        print(f"\n 💀 ¡{jugador.nombre_visible} se debilitó!")
        siguiente = next((p for p in equipo.pokemon if p.salud_actual > 0), None)
        if siguiente:
            print(f" ¡Adelante, {siguiente.nombre_visible}!")
    return None


def combatir_salvaje(equipo, mochila, salvaje, nombre_entrenador):
    '''Gestiona un encuentro completo contra un Pokémon salvaje de principio a fin.
    
    Ejecuta rondas mediante _turno_combate() permitiendo capturar o huir hasta que
    el salvaje sea atrapado, debilitado, el jugador escape o su equipo caiga.
    
    Devuelve:
        bool: True si el jugador ganó el encuentro (por captura o debilitamiento),
              False si huyó o perdió a todo su equipo.
    '''
    for p in equipo.pokemon:
        p.resetear_combate()
    salvaje.resetear_combate()

    print(f" 🌿 ¡Un {salvaje.especie} salvaje apareció (Nv.{salvaje.nivel})!")
    mostrar_barras(equipo.activo, salvaje)

    # El combate continúa mientras el salvaje siga en pie y quede al menos 1 aliado vivo
    while salvaje.salud_actual > 0 and any(p.salud_actual > 0 for p in equipo.pokemon):
        resultado = _turno_combate(
            equipo, salvaje, mochila,
            capturable=True,
            nombre_entrenador=nombre_entrenador
        )
        # Si _turno_combate devuelve 'capturado' o 'huida', terminamos el encuentro
        if resultado:
            for p in equipo.pokemon:
                p.resetear_combate()
            return resultado == "capturado"

    for p in equipo.pokemon:
        p.resetear_combate()

    # Evaluamos el desenlace si el bucle terminó por salud (0 PS)
    if salvaje.salud_actual <= 0:
        premio = random.randint(100, 400)
        mochila.ganar(premio)
        imprimir_con_retraso(f"🥳 Ganaste el combate y recibiste {premio} ₽.")
        time.sleep(.5)
        return True

    # Si llegamos aquí, todo el equipo del jugador quedó debilitado
    imprimir_con_retraso("\n 💀 ¡No te quedan Pokémon disponibles! Corres al Centro Pokémon...\n")
    return False


def combatir_entrenador(equipo, mochila, npc, nombre_entrenador):
    '''Gestiona un combate completo contra un Entrenador NPC de principio a fin.
    
    Enfrenta al equipo del jugador sucesivamente contra cada Pokémon del rival
    (sin permitir captura ni huida) y otorga la recompensa económica al vencer.
    
    Devuelve:
        bool: True si el jugador derrotó a todo el equipo del NPC,
              False si el equipo aliado quedó debilitado.
    '''
    for p in equipo.pokemon:
        p.resetear_combate()
    imprimir_con_retraso(f" 🧢 ¡{npc.nombre} te desafía a un combate!\n")

    # Restauramos la salud del equipo rival por si se vuelve a desafiar al entrenador
    for pokemon_npc in npc.equipo:
        pokemon_npc.salud_actual = pokemon_npc.salud_maxima
        pokemon_npc.resetear_combate()
        for mov in pokemon_npc.movimientos:
            mov.pp = mov.pp_max

    # Recorremos uno a uno los Pokémon del equipo del entrenador rival
    for rival in npc.equipo:
        imprimir_con_retraso(f"\n🧢 {npc.nombre} envía a {rival.especie} (Nv.{rival.nivel})!")
        mostrar_barras(equipo.activo, rival)
        # Mantenemos el duelo actual hasta que caiga el Pokémon rival o todo nuestro equipo
        while rival.salud_actual > 0 and any(p.salud_actual > 0 for p in equipo.pokemon):
            _turno_combate(
                equipo, rival, mochila,
                capturable=False,
                nombre_entrenador=nombre_entrenador
            )

        # Si tras el duelo no queda ningún aliado consciente, el jugador pierde el desafío
        if not any(p.salud_actual > 0 for p in equipo.pokemon):
            for p in equipo.pokemon:
                p.resetear_combate()
            imprimir_con_retraso("\n💀 Tu equipo quedó debilitado. Visita un Centro Pokémon.")
            return False

    for p in equipo.pokemon:
        p.resetear_combate()
    # Si superó a todos los Pokémon del rival, entregamos la recompensa económica
    mochila.ganar(npc.recompensa)
    print(f"🙌 ¡Venciste a {npc.nombre} y ganaste {npc.recompensa} ₽!")
    return True