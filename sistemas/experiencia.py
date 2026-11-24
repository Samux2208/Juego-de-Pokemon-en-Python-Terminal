from config import NIVEL_MAXIMO
from servicios.catalogos import DICCIONARIO_POKEMON
from sistemas.estadisticas import exp_para_nivel, generar_movimientos
from sistemas.evolucion import verificar_evolucion_nivel

def calcular_exp_ganada(rival):
    '''Calcula los puntos de experiencia obtenidos al derrotar a un rival.'''
    exp_base = DICCIONARIO_POKEMON[rival.especie]["exp_base"]
    return max(1, int(exp_base * rival.nivel / 7))

def comprobar_subida_nivel(pokemon):
    '''Verifica si la EXP actual alcanza para subir de nivel y retorna los eventos.'''
    eventos = []
    subio = False

    while pokemon.exp_actual >= pokemon.exp_siguiente_nivel and pokemon.nivel < NIVEL_MAXIMO:
        pokemon.nivel += 1
        subio = True
        pokemon.actualizar_exp_siguiente_nivel(exp_para_nivel(pokemon.nivel + 1))
        eventos.append(f"🎉 ¡{pokemon.nombre_visible} subió al Nivel {pokemon.nivel}!")

    if subio:
        salud_anterior = pokemon.salud_maxima
        pokemon.recalcular_estadisticas()
        pokemon.salud_actual += pokemon.salud_maxima - salud_anterior
        eventos.append("📈 ¡Las estadísticas han aumentado!")

        # Guardamos ataques previos antes de evolucionar
        conocidos = {m.nombre for m in pokemon.movimientos}

        # Delegamos la evolución a sistemas/evolucion.py
        eventos.extend(verificar_evolucion_nivel(pokemon))

        # Actualizamos repertorio de movimientos de la especie final
        nuevos = generar_movimientos(pokemon.especie, pokemon.nivel)
        for mov in nuevos:
            if mov.nombre not in conocidos:
                eventos.append(f"📘 ¡{pokemon.nombre_visible} aprendió {mov.nombre}!")
        
        pokemon.movimientos = nuevos

    return eventos