# ==================================================
# ARCHIVO: interfaz/pokedex_ui.py
# ==================================================
from datos.tipos_evoluciones import nombre_tipo
from interfaz.mensajes import nombre_tipo, resumen_movimiento, ajustar_ancho
from sistemas.pokedex import describir_disponibilidad
from sistemas.estadisticas import exp_para_nivel, NATURALEZAS

# ---------------- INTERFAZ DE FICHA TéCNICA ----------------
def ficha_pokemon(pokemon):
    '''Muestra la ficha técnica paginada del Pokémon en consola (Datos y Estadísticas).'''
    # Buscamos en qué rutas aparece este Pokémon para generar el texto de ubicación
    notas_entrenador = describir_disponibilidad(pokemon.nombre)

    # Precalculamos la barra de experiencia (escala fija de 20 emojis)
    total_barras_exp = 10
    exp_base = exp_para_nivel(pokemon.nivel)
    exp_necesaria = max(1, pokemon.exp_siguiente_nivel - exp_base)
    exp_progresada = pokemon.exp_actual - exp_base
    
    # Determinamos cuántos caracteres '#' pintar (escala de 0 a 20)
    barras_exp = int(max(0, exp_progresada) / exp_necesaria * total_barras_exp)
    if exp_progresada > 0 and barras_exp == 0:
        barras_exp = 1  # Garantiza al menos 1 barra visible si tiene progreso
        
    llenas = min(total_barras_exp, max(0, barras_exp))
    barra_visual_exp = ("🟦" * llenas) + ("⬜" * max(0, total_barras_exp - llenas))

    sube, baja = NATURALEZAS.get(pokemon.naturaleza, (None, None))
    info_nat = f"{pokemon.naturaleza}  [+{sube} / -{baja}]" if sube else f"{pokemon.naturaleza} [Neutra]"

    # Configuramos el menú para que se abra siempre en la primera página de información
    pagina_actual = 1

    while True:
        print("\n" + " ╔" + "═" * 58 + "╗")
        if pagina_actual == 1:
            # --- PÁGINA 1: DATOS BÁSICOS Y NOTAS ---
            print(f" ║{ajustar_ancho(' 📋 INFO. POKéMON                          PÁGINA [1/3]', 58)}║")
            print(" ╠" + "═" * 58 + "╣")
            fila_id = f" Nv.{pokemon.nivel:<4} {pokemon.nombre_visible:<25} Especie {pokemon.nombre:<14}"
            print(f" ║{ajustar_ancho(fila_id, 58)}║")
            
            tipos_str = " / ".join(nombre_tipo(t) for t in pokemon._tipos)
            print(f" ║{ajustar_ancho(f' TIPO {tipos_str}', 58)}║")
            print(f" ║{ajustar_ancho(f' NATURALEZA {info_nat}', 58)}║")
            
            print(" ╟" + "─" * 58 + "╢")
            print(f" ║{ajustar_ancho(' 📝 NOTAS DE LA POKéDEX', 58)}║")
            
            linea = ""
            for palabra in notas_entrenador.split():
                candidato = f"{linea} {palabra}" if linea else palabra
                if len(candidato) > 54:
                    print(f" ║   {ajustar_ancho(linea, 54)} ║")
                    linea = palabra
                else:
                    linea = candidato
            if linea:
                print(f" ║   {ajustar_ancho(linea, 54)} ║")
            print(" ╚" + "═" * 58 + "╝")

        elif pagina_actual == 2:
            # --- PÁGINA 2: ESTADÍSTICAS ---
            print(f" ║{ajustar_ancho(' 📊 HABIL. POKéMON                         PÁGINA [2/3]', 58)}║")
            print(" ╠" + "═" * 58 + "╣")
            print(f" ║{ajustar_ancho(f' Nv.{pokemon.nivel:<4} {pokemon.nombre_visible}', 58)}║")
            
            fila_ps = f" ❤️  PS {pokemon.barra_de_vida} {pokemon.salud_actual:>3}/{pokemon.salud_maxima:<3}"
            print(f" ║{ajustar_ancho(fila_ps, 58)}║")
            
            print(" ╟" + "─" * 58 + "╢")
            fila_atk = f" ⚔️  ATAQUE    {pokemon.ataque:<14} 🛡️  DEFENSA    {pokemon.defensa:<10}"
            fila_spa = f" 🔮 ATQ. ESP. {pokemon.ataque_especial:<14} 🔰 DEF. ESP.  {pokemon.defensa_especial:<10}"
            fila_vel = f" 💨 VELOCIDAD {pokemon.velocidad}"
            print(f" ║{ajustar_ancho(fila_atk, 58)}║")
            print(f" ║{ajustar_ancho(fila_spa, 58)}║")
            print(f" ║{ajustar_ancho(fila_vel, 58)}║")
            
            print(" ╟" + "─" * 58 + "╢")
            fila_exp_barra = f" ✨ EXPERIENCIA       EXP {barra_visual_exp}"
            fila_exp_nums = f"    PUNTOS.EXP {pokemon.exp_actual:<10} SIG. NIVEL: {pokemon.exp_siguiente_nivel}"
            print(f" ║{ajustar_ancho(fila_exp_barra, 58)}║")
            print(f" ║{ajustar_ancho(fila_exp_nums, 58)}║")
            print(" ╚" + "═" * 58 + "╝")

        else:
            # --- PÁGINA 3: MOVIMIENTOS ---
            print(f" ║{ajustar_ancho(' ⚔️  MOV. CONOCIDOS                        PÁGINA [3/3]', 58)}║")
            print(" ╠" + "═" * 58 + "╣")
            print(f" ║{ajustar_ancho(f' Nv.{pokemon.nivel:<4} {pokemon.nombre_visible}', 58)}║")
            print(" ╟" + "─" * 58 + "╢")
            
            for i, mov in enumerate(pokemon.movimientos):
                l1, l2 = resumen_movimiento(mov)
                print(f" ║{l1}║")
                print(f" ║{l2}║")
                if i < len(pokemon.movimientos) - 1:
                    print(" ║" + " ·" * 29 + "║")
            print(" ╚" + "═" * 58 + "╝")

        # Barra de navegación unificada para las 3 páginas
        print("     [A] ◀ Anterior  |  [D] Siguiente ▶  |  [X] 🔙 Salir\n")
        op = input(" 👉 Selecciona una opción: ").strip().lower()


        if op == "x":
            break
        elif op == "a":
            # Retrocede cíclicamente: 1 -> 3 -> 2 -> 1
            pagina_actual = (pagina_actual - 2) % 3 + 1
        else:
            # Avanza cíclicamente con ENTER o D: 1 -> 2 -> 3 -> 1
            pagina_actual = (pagina_actual % 3) + 1