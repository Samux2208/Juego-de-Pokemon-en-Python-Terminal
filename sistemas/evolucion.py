from datos.tipos_evoluciones import EVOLUCIONES_NIVEL
from servicios.catalogos import DICCIONARIO_POKEMON
from sistemas.estadisticas import generar_movimientos

def evolucionar_pokemon(pokemon, nueva_especie):
    '''Evoluciona un Pokémon a una nueva especie, ajusta sus PS y actualiza ataques.'''
    if nueva_especie not in DICCIONARIO_POKEMON:
        raise ValueError(f"Especie de evolución desconocida: {nueva_especie}")

    nombre_anterior = pokemon.nombre_visible
    salud_anterior = pokemon.salud_maxima

    # Actualizamos especie, tipos y estadísticas mediante el método seguro de Pokemon
    pokemon.cambiar_especie(nueva_especie)
    pokemon.movimientos = generar_movimientos(nueva_especie, pokemon.nivel)

    # Ajustamos los PS actuales sumando la diferencia de vida ganada al evolucionar
    pokemon.salud_actual = min(
        pokemon.salud_maxima,
        max(0, pokemon.salud_actual + pokemon.salud_maxima - salud_anterior)
    )
    return f"✨ ¡{nombre_anterior} evolucionó a {nueva_especie}!"

def verificar_evolucion_nivel(pokemon):
    '''Comprueba si el Pokémon cumple el nivel para evolucionar (soporta evoluciones en cadena).'''
    eventos = []
    evolucion = EVOLUCIONES_NIVEL.get(pokemon.especie)
    while evolucion and pokemon.nivel >= evolucion[0]:
        eventos.append(evolucionar_pokemon(pokemon, evolucion[1]))
        evolucion = EVOLUCIONES_NIVEL.get(pokemon.especie)
    return eventos
