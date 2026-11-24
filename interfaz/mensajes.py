import sys
import time
import unicodedata
from config import RETRASO_TEXTO
from datos.tipos_evoluciones import ICONOS_CATEGORIA, nombre_tipo
from sistemas.efectos import ESTADOS_INFO

def imprimir_con_retraso(s):
    '''Imprime un texto carácter por carácter con una pausa configurable.'''
    for letra in s:
        sys.stdout.write(letra)
        sys.stdout.flush()
        time.sleep(RETRASO_TEXTO)  # Pausa por defecto de 0.05 s entre letras


def ancho_visual(texto):
    '''Calcula los espacios reales que ocupa un texto con emojis en la terminal.'''
    ancho = 0
    for ch in texto:
        # Ignoramos selectores de variación invisibles (como el de ☠️)
        if unicodedata.category(ch) == "Mn" or ord(ch) in (0xFE0F, 0x200D):
            continue
        # Los emojis y caracteres anchos ('W' o 'F') ocupan 2 columnas en consola
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            ancho += 2
        else:
            ancho += 1
    return ancho

def ajustar_ancho(texto, ancho_objetivo):
    '''Rellena con espacios a la derecha respetando el ancho real de los emojis.'''
    faltante = max(0, ancho_objetivo - ancho_visual(texto))
    return texto + (" " * faltante)


def resumen_movimiento(mov, prefijo="▸"):
    '''Devuelve una tupla (linea_1, linea_2) de 58 columnas exactas para Pokédex y combate.'''
    cat_str = ICONOS_CATEGORIA.get(mov.categoria, "💥 Fís")
    pot_str = f"{mov.potencia:>3}" if mov.potencia > 0 else " --"

    # Línea 1: Prefijo (▸ o [1]), nombre del movimiento y tipo elemental
    linea_1 = f" {prefijo:<3} {mov.nombre:<28} {nombre_tipo(mov.tipo)}"
    # Línea 2: Categoría, Potencia, Precisión y PP actuales/máximos
    linea_2 = f"     {cat_str} │ Pot {pot_str} │ Prec {mov.precision:>3} │ PP {mov.pp:>2}/{mov.pp_max:<2} |"

    return ajustar_ancho(linea_1, 58), ajustar_ancho(linea_2, 58)


def mostrar_barras(jugador, rival):
    '''Imprime en consola las barras de vida actuales de ambos combatientes.'''
    est_rival = (
        f" {ESTADOS_INFO[rival.estado_alterado]['etiqueta']}"
        if rival.estado_alterado in ESTADOS_INFO
        else ""
    )
    est_jug = (
        f" {ESTADOS_INFO[jugador.estado_alterado]['etiqueta']}"
        if jugador.estado_alterado in ESTADOS_INFO
        else ""
    )
    
    print("\n" + "╔" + "═" * 58 + "╗")
    print(f"║ 👾 {rival.nombre_visible:<16}   Nv.{rival.nivel:<3}{est_rival:<12}                 ║")
    print(f"║    PS {rival.barra_de_vida} {rival.salud_actual:>3}/{rival.salud_maxima:<3}   ║")
    print("╠" + "─" * 58 + "╣")
    print(f"║ 🔴  {jugador.nombre_visible:<16}   Nv.{jugador.nivel:<3}{est_jug:<12}                ║")
    print(f"║    PS {jugador.barra_de_vida} {jugador.salud_actual:>3}/{jugador.salud_maxima:<3}   ║")
    print("╚" + "═" * 58 + "╝")
    time.sleep(.5)