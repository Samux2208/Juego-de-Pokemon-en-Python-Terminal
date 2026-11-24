'''Menús de exploración, equipo, mochila y servicios de Kanto.'''

import random
import time
from mundo.rutas import RUTAS
from modelos.pokemon import Pokemon
from modelos.objeto import OBJETOS
from modelos.entrenador import EntrenadorNPC, LiderGimnasio
from mundo.localizaciones import TiendaPokemon, CentroPokemon
from sistemas.combate import _elegir_pokemon_activo, combatir_salvaje, combatir_entrenador
from sistemas.encuentros import explorar_ruta
from interfaz.mensajes import imprimir_con_retraso, ajustar_ancho
from interfaz.pokedex_ui import ficha_pokemon


def gestionar_equipo(equipo):
    '''Muestra la interfaz de consola del PC (Depositar, Sacar, Mover y Ver Ficha).'''
    CentroPokemon.conectar_pc()

    while True:
        time.sleep(.5)
        print("\n" + " ╔" + "═" * 54 + "╗")
        imprimir_con_retraso(f" ║{ajustar_ancho('  💻 PC DE BILL — ALMACENAMIENTO POKéMON', 54)}║\n")
        print(" ╠" + "═" * 54 + "╣")
        time.sleep(.5)

        # Equipo activo
        cabecera_equipo = f"  🎒 EQUIPO ACTIVO ({len(equipo.pokemon)}/{equipo.LIMITE}):"
        print(f" ║{ajustar_ancho(cabecera_equipo, 54)}║")

        for i, pokemon in enumerate(equipo.pokemon, start=1):
            lider = "⭐" if i == 1 else "🔴"
            estado = "❤️" if pokemon.salud_actual > 0 else "💀"
            linea = f"   [{i}] {lider} {pokemon.nombre_visible:<14} Nv.{pokemon.nivel:<3} {estado} {pokemon.salud_actual:>3}/{pokemon.salud_maxima:<3}"
            print(f" ║{ajustar_ancho(linea, 54)}║")

        print(" ╟" + "─" * 54 + "╢")
        cabecera_pc = f"  🖥️  CAJA DEL PC: {len(equipo.pc):<3} Pokémon almacenados"
        print(f" ║{ajustar_ancho(cabecera_pc, 54)}║")
        print(" ╠" + "═" * 54 + "╣")
        print(f" ║{ajustar_ancho('  [1] 📥 Dejar Pokémon     [2] 📤 Sacar Pokémon', 54)}║")
        print(f" ║{ajustar_ancho('  [3] 🔄 Mover Pokémon     [4] 📊 Ver Datos (Ficha)', 54)}║")
        print(f" ║{ajustar_ancho('  [X] 🔙 Desconectar PC', 54)}║")
        print(" ╚" + "═" * 54 + "╝")
        op = input(" 👉 Elige una opción de la PC: ").strip().lower()

        if op == "x":
            imprimir_con_retraso("\n 🔌 Desconectado del Sistema de Almacenamiento de Bill.\n")
            return

        # --- 1. DEJAR EN PC ---
        elif op == "1":
            if len(equipo.pokemon) <= 1:
                print(" ⚠️  No puedes enviar tu último Pokémon al PC.")
                time.sleep(.5)
                continue
            try:
                i = int(input("\n 📤 Número del Pokémon a enviar al PC: ")) - 1
            except ValueError:
                print(" ❌ Debes ingresar un número válido.")
                continue

            if equipo.enviar_al_pc(i):
                print(" ✅ Pokémon depositado en la Caja PC.")
            else:
                print(" ⚠️ Número fuera de rango.")

        # --- 2. SACAR DEL PC ---
        elif op == "2":
            if not equipo.pc:
                print(" 📭 La Caja del PC está vacía.")
                time.sleep(.5)
                continue
            if len(equipo.pokemon) >= equipo.LIMITE:
                print(" ⚠️ Tu equipo ya está lleno (6/6). Deposita uno primero.")
                continue

            print("\n 🖥️  Pokémon en la Caja del PC:")
            for i, p in enumerate(equipo.pc, start=1):
                estado = "❤️" if p.salud_actual > 0 else "💀"
                print(f"  [{i}] {p.nombre_visible:<15} Nv.{p.nivel:<3} | {estado} PS {p.salud_actual}/{p.salud_maxima}")

            try:
                i = int(input("\n 📥 Número del Pokémon a sacar del PC: ")) - 1
            except ValueError:
                print(" ❌ Debes ingresar un número válido.")
                continue

            if equipo.recuperar_del_pc(i):
                print(" ✅ Pokémon añadido a tu equipo.")
            else:
                print(" ⚠️ Número fuera de rango.")

        # --- 3. MOVER / REORDENAR POKéMON ---
        elif op == "3":
            print("\n" + " ╔" + "═" * 54 + "╗")
            print(f" ║{ajustar_ancho('  🔄 ¿DÓNDE QUIERES MOVER POKéMON?', 54)}║")
            print(" ╠" + "─" * 54 + "╣")
            print(f" ║{ajustar_ancho(' [1] 🎒 En el Equipo  [2] 🖥️  En el PC   [X] 🔙 Volver', 54)}║")
            print(" ╚" + "═" * 54 + "╝")
            zona = input(" 👉 Elige ubicación: ").strip().lower()

            if zona == "x":
                continue

            if zona == "1":
                if len(equipo.pokemon) < 2:
                    print(" ⚠️  Necesitas al menos 2 Pokémon en el equipo para moverlos.")
                    continue
                try:
                    a = int(input(" 👉 Número del primer Pokémon a mover: ")) - 1
                    b = int(input(" 👉 Número de la posición destino: ")) - 1
                except ValueError:
                    print(" ❌ Debes ingresar números válidos.")
                    continue

                if a == b:
                    print(" ⚠️ Elegiste la misma posición.")
                elif (a == 0 or b == 0) and (
                    (a == 0 and 0 <= b < len(equipo.pokemon) and equipo.pokemon[b].salud_actual <= 0)
                    or (b == 0 and 0 <= a < len(equipo.pokemon) and equipo.pokemon[a].salud_actual <= 0)
                ):
                    print(" 💀 No puedes dejar un Pokémon debilitado como líder (posición 1).")
                elif equipo.intercambiar_en_equipo(a, b):
                    print(" ✅ Posiciones del equipo actualizadas.")
                else:
                    print(" ⚠️ Números fuera de rango.")

            elif zona == "2":
                if len(equipo.pc) < 2:
                    print(" ⚠️  Necesitas al menos 2 Pokémon en el PC para reordenarlos.")
                    continue
                print("\n 🖥️  Pokémon en la Caja del PC:")
                for i, p in enumerate(equipo.pc, start=1):
                    print(f"  [{i}] {p.nombre_visible:<15} Nv.{p.nivel:<3}")
                try:
                    a = int(input(" 👉 Número del primer Pokémon a mover: ")) - 1
                    b = int(input(" 👉 Número de la posición destino: ")) - 1
                except ValueError:
                    print(" ❌ Debes ingresar números válidos.")
                    continue

                if a == b:
                    print(" ⚠️  Elegiste la misma posición.")
                elif equipo.intercambiar_en_pc(a, b):
                    print(" ✅ Posiciones en el PC actualizadas.")
                else:
                    print(" ⚠️  Números fuera de rango.")
            else:
                print(" ⚠️  Ubicación no válida.")

        # --- 4. VER DATOS (MOSTRAR FICHA DE 3 PÁGINAS) ---
        elif op == "4":
            print("\n 📊 ¿De dónde quieres ver los datos?  [1] 🎒 Equipo   [2] 🖥️  PC")
            zona = input(" 👉 Elige ubicación: ").strip()
            lista = equipo.pokemon if zona == "1" else (equipo.pc if zona == "2" else None)

            if not lista:
                print(" ⚠️ Ubicación inválida o sin Pokémon.")
                continue

            if zona == "2":
                print("\n 🖥️  Pokémon en la Caja del PC:")
                for i, p in enumerate(lista, start=1):
                    print(f"  [{i}] {p.nombre_visible:<15} Nv.{p.nivel:<3}")

            try:
                i = int(input(" 👉 Número del Pokémon para mostrar ficha: ")) - 1
            except ValueError:
                print(" ❌ Debes ingresar un número válido.")
                continue

            if 0 <= i < len(lista):
                ficha_pokemon(lista[i])
            else:
                print(" ⚠️ Número fuera de rango.")

        else:
            print(" ❌ Opción no válida. Elige entre 1 y 4, o X para desconectar.")


def gestionar_mochila(equipo, mochila, en_tienda=False):
    '''Muestra la interfaz de la Mochila o de la Tienda Pokémon en consola.
    
    Parámetros:
        equipo (Equipo): Equipo activo del jugador (para aplicar pociones o piedras).
        mochila (Mochila): Inventario y saldo actual del entrenador.
        en_tienda (bool): Si es True, activa el modo de compra en TiendaPokemon;
                          si es False, permite usar objetos del inventario.
    '''
    while True:
        time.sleep(1)
        # Cabecera dinámica según si estamos en la Tienda o en la Mochila
        titulo = "🏪 TIENDA POKÉMON" if en_tienda else "🎒 MOCHILA DEL ENTRENADOR"
        
        print("\n" + " ╔" + "═" * 52 + "╗")
        print(f" ║{ajustar_ancho(f'  {titulo}', 52)}║")
        print(" ╠" + "═" * 52 + "╣")
        
        fila_saldo = f"  💰 Saldo disponible: {mochila.dinero} ₽ (pokémonedas)"
        print(f" ║{ajustar_ancho(fila_saldo, 52)}║")
        print(" ╟" + "─" * 52 + "╢")

        # Listamos el contenido actual de la mochila
        items_actuales = mochila.listar()
        if not items_actuales:
            print(f" ║{ajustar_ancho('  📭 Tu mochila está vacía.', 52)}║")
        else:
            print(f" ║{ajustar_ancho('  📦 Objetos en tu inventario:', 52)}║")
            for i, (objeto, cantidad) in enumerate(items_actuales, start=1):
                fila_item = f"    [{i}] {objeto.nombre:<18} x{cantidad:<3}"
                print(f" ║{ajustar_ancho(fila_item, 52)}║")

        print(" ╚" + "═" * 52 + "╝")

        # ========================================================
        # MODO A: TIENDA POKéMON (COMPRA DE OBJETOS)
        # ========================================================
        if en_tienda:
            print("  [1] 🛒 Comprar objetos | [X] 🔙 Salir de la tienda")
            op = input("\n 👉 Elige una opción: ").strip().lower()

            if op == "x":
                return
            if op != "1":
                print(" ❌ Opción no válida. Elige 1 o 2.")
                continue

            # Mostramos el catálogo oficial de la tienda con precios
            print("\n" + " ╔" + "═" * 52 + "╗")
            print(f" ║{ajustar_ancho(f'  🏪 CATÁLOGO DE LA TIENDA POKÉMON', 52)}║")
            print(" ╠" + "═" * 52 + "╣")
            time.sleep(.5)

            fila_saldo = f"  💰 Tu Saldo: {mochila.dinero} ₽"
            print(f" ║{ajustar_ancho(fila_saldo, 52)}║")
            print(" ╟" + "─" * 52 + "╢")
            print(f" ║{ajustar_ancho('   Nº  │ ARTÍCULO             │ PRECIO', 52)}║")
            print(" ╟" + "─" * 52 + "╢")
            time.sleep(.5)

            catalogo = list(OBJETOS.values())
            for i, objeto in enumerate(catalogo, start=1):
                # Muestra en verde/normal si alcanza el dinero, o con candado si no alcanza
                estado_compra = "💲" if mochila.dinero >= objeto.precio else "🔒"
                fila_prod = f"  [{i:<2}] │ {objeto.nombre:<20} │ {estado_compra} {objeto.precio:>5} ₽"
                print(f" ║{ajustar_ancho(fila_prod, 52)}║")

            print(" ╟" + "─" * 52 + "╢")
            print(f" ║{ajustar_ancho('  [X]  │ 🔙 Cancelar compra', 52)}║")
            print(" ╚" + "═" * 52 + "╝")
            time.sleep(1.5)

            # Leemos primero como texto para detectar 'x' o 'X' antes de convertir a entero
            op = input(" 👉 Elige un objeto: ").strip().lower()
            if op == "x":
                continue
            try:
                selec = int(op)
                if not 1 <= selec <= len(catalogo):
                    print(" ⚠️  Número de objeto fuera de rango.")
                    continue

                objeto_elegido = catalogo[selec - 1]

                # Validamos primero si alcanza para comprar al menos 1 unidad
                if mochila.dinero < objeto_elegido.precio:
                    faltante = objeto_elegido.precio - mochila.dinero
                    print(f" 💸 No tienes suficientes pokémonedas para comprar {objeto_elegido.nombre}\n  (cuesta {objeto_elegido.precio} ₽ y te faltan {faltante} ₽).")
                    continue

                # Como sí le alcanza, calculamos el máximo que puede llevar y preguntamos
                max_unidades = mochila.dinero // objeto_elegido.precio
                cantidad = int(
                    input(f" 🔢 ¿Cuántas unidades de {objeto_elegido.nombre} quieres? (Máx. {max_unidades}): ")
                )
                TiendaPokemon.comprar(
                    mochila, objeto_elegido.identificador, cantidad
                )
            except ValueError:
                print(" ❌ Debes ingresar un número válido.")
            continue

        # ========================================================
        # MODO B: MOCHILA FUERA DE COMBATE (USO DE OBJETOS)
        # ========================================================
        print("   [1] ✨ Usar un objeto  |  [X] 🔙 Cerrar mochila")
        op = input("\n 👉 Elige una opción: ").strip().lower()

        if op == "x":
            return
        if op != "1":
            print(" ❌ Opción no válida. Elige 1 o 2.")
            continue

        disponibles = [(obj, count) for obj, count in items_actuales if count > 0]
        if not disponibles:
            print(" 📭 No tienes objetos disponibles para usar.")
            continue

        print("\n" + " ╔" + "═" * 48 + "╗")
        print(f" ║{ajustar_ancho('  🎒 SELECCIONA EL OBJETO A UTILIZAR', 48)}║")
        print(" ╠" + "═" * 48 + "╣")
        print(f" ║{ajustar_ancho('   Nº  │ OBJETO               │ CANTIDAD', 48)}║")
        print(" ╟" + "─" * 48 + "╢")

        for i, (objeto, cantidad) in enumerate(disponibles, start=1):
            fila_obj = f"  [{i:<2}] │ {objeto.nombre:<20} │ 📦 x{cantidad:<3}"
            print(f" ║{ajustar_ancho(fila_obj, 48)}║")

        print(" ╟" + "─" * 48 + "╢")
        print(f" ║{ajustar_ancho('  [X]  │ 🔙 Cancelar', 48)}║")
        print(" ╚" + "═" * 48 + "╝")
        
        op = input(" 👉 Elige un objeto: ")
        if op == "x":
            continue

        try:
            i = int(op)
            if not 1 <= i <= len(disponibles):
                print(" ⚠️ Número de objeto fuera de rango.")
                continue
            objeto = disponibles[i - 1][0]
        except ValueError:
            print(" ❌ Debes ingresar un número válido.")
            continue

        objetivo = None
        if objeto.requiere_objetivo:
            objetivo = _elegir_objetivo_mochila(equipo)
            if objetivo is None:
                continue

        consumido, _ = objeto.usar({
            "equipo": equipo,
            "mochila": mochila,
            "objetivo": objetivo,
        })
        if consumido:
            mochila.quitar(objeto.identificador)
        else:
            imprimir_con_retraso(
                f" ⚠️  No se pudo usar {objeto.nombre} en este momento."
            )


def _elegir_objetivo_mochila(equipo):
    '''Permite elegir cualquier Pokémon del equipo como objetivo de un objeto.'''
    if not equipo.pokemon:
        return None

    for indice, pokemon in enumerate(equipo.pokemon, start=1):
        estado = "💀" if pokemon.salud_actual <= 0 else "❤️"
        print(
            f" [{indice}] {estado} {pokemon.nombre_visible} "
            f"PS {pokemon.salud_actual}/{pokemon.salud_maxima}"
        )
    while True:
        entrada = input(" 👉 Elige el Pokémon objetivo: ").strip()
        if entrada.isdigit():
            indice = int(entrada) - 1
            if 0 <= indice < len(equipo.pokemon):
                return equipo.pokemon[indice]
        print(" ❌ Opción no válida.")


def zona_segura(equipo, mochila, nombre_entrenador="Entrenador"):
    '''Muestra el menú de servicios del Pueblo / Zona segura.
    
    Permite al entrenador curar a su equipo en el Centro Pokémon, comprar
    objetos en la Tienda, administrar el Equipo/PC, usar la mochila o desafiar
    a Brock. Devuelve `"fin"` si el desafío de gimnasio termina la partida.
    '''
    while True:
        print("\n" + " ╔" + "═" * 48 + "╗")
        print(f" ║{ajustar_ancho('         🏘️  PUEBLO / ZONA SEGURA 🏘️', 48)}║")
        print(" ╠" + "═" * 48 + "╣")
        print(f" ║{ajustar_ancho(' [1] 🏥 Centro Pokémon (Curar equipo)', 48)}║")
        print(f" ║{ajustar_ancho(' [2] 💻 PC de Bill (Almacenamiento Pokémon)', 48)}║")
        print(f" ║{ajustar_ancho(' [3] 🏪 Tienda Pokémon (Comprar objetos)', 48)}║")
        print(f" ║{ajustar_ancho(' [4] 🎒 Mochila (Objetos y Evolución)', 48)}║")
        print(f" ║{ajustar_ancho(' [5] 🏅 Desafiar a Brock (Gimnasio Plateada)', 48)}║")
        print(" ╟" + "─" * 48 + "╢")
        print(f" ║{ajustar_ancho(' [X] 🔙 Volver al menú principal', 48)}║")
        print(" ╚" + "═" * 48 + "╝")

        op = input(" 👉 ¿A qué edificio quieres entrar?: ").strip().lower()

        if op == "1":
            # Restaura al 100% los PS de todos los Pokémon del equipo activo
            CentroPokemon.curar(equipo)
        elif op == "2":
            # Abre el sistema de almacenamiento para mover Pokémon entre equipo y PC
            gestionar_equipo(equipo)
        elif op == "3":
            # Abre la interfaz de mochila en modo compra
            gestionar_mochila(equipo, mochila, en_tienda=True)
        elif op == "4":
            # Abre la mochila para usar pociones o piedras evolutivas
            gestionar_mochila(equipo, mochila)
        elif op == "5":
            desafiar_lider_gimnasio(nombre_entrenador, equipo, mochila)
            return "fin"
        elif op == "x":
            return
        else:
            print(" ❌ Opción no válida. Elige un número entre 1 y 5.")


def desafiar_lider_gimnasio(nombre_entrenador, equipo, mochila) -> bool:
    '''Inicia el desafío final de Brock en el Gimnasio Plateada.'''
    lider = LiderGimnasio(
        nombre="Brock",
        equipo=[Pokemon("Geodude", 3)],
        gimnasio="Gimnasio Plateada",
        medalla="Medalla Roca",
    )
    return combatir_entrenador(equipo, mochila, lider, nombre_entrenador)


def menu_rutas(nombre_entrenador, equipo, mochila):
    '''Muestra el mapa regional de Kanto y gestiona el encuentro en la ruta elegida.
    
    Tras seleccionar un destino válido, existe un 25% de probabilidad de ser
    desafiado por un Entrenador NPC de la zona y un 75% de encontrar un
    Pokémon salvaje correspondiente al pool y rango de niveles de la ruta.
    '''
    # Verificamos que el entrenador tenga al menos un Pokémon consciente antes de salir
    if not any(p.salud_actual > 0 for p in equipo.pokemon):
        print("\n 💀 Todos tus Pokémon están debilitados. ¡Visita primero el Centro Pokémon!")
        return
    
    while True:
        print("\n" + " ╔" + "═" * 58 + "╗")
        imprimir_con_retraso(f" ║{ajustar_ancho('  🗺️  MAPA DE KANTO — GUÍA DE ZONAS Y RUTAS', 58)}║\n")
        print(" ╠" + "═" * 58 + "╣")
        time.sleep(.5)

        print(f" ║{ajustar_ancho('   Nº  │ DESTINO / ZONA                   │ NIVELES', 58)}║")
        print(" ╟" + "─" * 58 + "╢")

        # Listamos todas las rutas disponibles con icono según el tipo de zona
        for i, ruta in enumerate(RUTAS, start=1):
            nivel_min, nivel_max = ruta["niveles"]
            nombre_ruta = ruta["nombre"]
            nombre_lower = nombre_ruta.lower()

            # Icono ambiental fiel a Gen III según el lugar
            if "bosque" in nombre_lower:
                icono = "🌲"
            elif "cueva" in nombre_lower or "monte" in nombre_lower or "túnel" in nombre_lower:
                icono = "⛰️ "
            elif "mar" in nombre_lower or "isla" in nombre_lower or "espuma" in nombre_lower:
                icono = "🌊"
            elif "torre" in nombre_lower or "mansión" in nombre_lower or "central" in nombre_lower:
                icono = "🏛️ "
            elif "calle" in nombre_lower or "liga" in nombre_lower:
                icono = "🏆"
            else:
                icono = "🌿"  # Hierba alta estándar de rutas de Kanto

            zona_col = ajustar_ancho(f"{icono} {nombre_ruta}", 32)
            fila_ruta = f"  [{i:>2}] │ {zona_col} │ Nv. {nivel_min:>2}-{nivel_max:>2}"
            print(f" ║{ajustar_ancho(fila_ruta, 58)}║")

        print(" ╟" + "─" * 58 + "╢")
        print(f" ║{ajustar_ancho('  [X]  │ 🔙 Guardar el Mapa y volver al menú', 58)}║")
        print(" ╚" + "═" * 58 + "╝")
        time.sleep(.5)

        # Capturamos y validamos el destino elegido
        op_ruta = input(" 🧭 ¿A qué destino de Kanto deseas viajar?: ").strip().lower()
        if op_ruta == "x":
            break

        if op_ruta == "x":
            return
        if not op_ruta.isdigit() or not 1 <= int(op_ruta) <= len(RUTAS):
            print(" ⚠️  Destino incorrecto. Elige una opción del mapa.")
            continue

        # Convertimos a entero para usarlo en las líneas siguientes (ej. RUTAS[opcion_ruta - 1])
        op_ruta = int(op_ruta)

        # Mostramos la narrativa de exploración de la ruta seleccionada
        ruta = RUTAS[op_ruta - 1]
        imprimir_con_retraso(ruta["mensaje"])
        time.sleep(.5)

        # 25% de probabilidad de encuentro contra un Entrenador NPC de la ruta
        if random.random() < 0.25:
            especie = random.choice(ruta["pool"])
            nivel = random.randint(*ruta["niveles"])
            npc = EntrenadorNPC(
                random.choice(("Joven", "Cazabichos", "Entrenadora", "Montañero")),
                [Pokemon(especie, nivel)],
                recompensa=random.randint(300, 900) + nivel * 20,
            )
            combatir_entrenador(equipo, mochila, npc, nombre_entrenador)
        else:
            # 75% de probabilidad de encuentro contra un Pokémon salvaje
            salvaje = explorar_ruta(op_ruta)
            combatir_salvaje(equipo, mochila, salvaje, nombre_entrenador)
        return