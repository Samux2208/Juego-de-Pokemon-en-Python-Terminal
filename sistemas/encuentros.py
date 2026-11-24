import random
from mundo.rutas import RUTAS
from modelos.pokemon import PokemonSalvaje

# == EXPLORACIÓN DE RUTAS ====================================
# explorar_ruta() | Selecciona una ruta por su índice (1..N), muestra su
#                   narrativa y genera una instancia de PokemonSalvaje.
# ============================================================
 
def explorar_ruta(numero_ruta):
    '''Genera un Pokémon salvaje aleatorio del pool de la ruta elegida.
    
    Parámetros:
        numero_ruta (int): Índice humano de la ruta (entre 1 y len(RUTAS)).
        
    Devuelve:
        PokemonSalvaje | None: Instancia generada o None si el número es inválido.
    '''
    # Validamos que el número de ruta esté dentro del rango disponible
    if not 1 <= numero_ruta <= len(RUTAS):
        return None

    # Convertimos el número humano (1-based) al índice de lista (0-based)
    ruta = RUTAS[numero_ruta - 1]

    # 3. Elegimos especie al azar dentro del pool y nivel dentro del rango de la zona
    especie = random.choice(ruta["pool"])
    nivel = random.randint(*ruta["niveles"])

    # Asignamos la rareza ponderada: 75% común, 20% raro, 5% muy raro
    rareza = random.choices(
        PokemonSalvaje.RAREZAS_VALIDAS, weights=(75, 20, 5), k=1
    )[0]
    
    return PokemonSalvaje(especie, nivel, rareza=rareza, ruta=ruta["nombre"])
 