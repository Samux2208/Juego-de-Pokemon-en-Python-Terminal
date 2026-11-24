'''Flujo principal y bucle de estados del juego.

Coordina el arranque de partida y las acciones del menú principal,
delegando los textos y menús a la carpeta `interfaz/`.
'''

from servicios.nueva_partida import nueva_partida
from persistencia.guardado import guardar_partida, cargar_partida, ErrorGuardado
from interfaz.inicio import (
    pedir_opcion_inicio,
    pedir_opcion_menu_principal,
    pedir_pokemon_ficha,
    notificar_evento,
)
from interfaz.menus import (
    gestionar_mochila,
    zona_segura,
    menu_rutas,
)
from interfaz.pokedex_ui import ficha_pokemon


def iniciar_juego() -> None:
    '''Coordina la pantalla inicial, la carga o creación y el bucle principal.'''
    opcion_inicio = pedir_opcion_inicio()

    if opcion_inicio == 1:
        datos_partida, aviso = cargar_partida()
        if aviso:
            notificar_evento("aviso_carga", detalle=aviso)

        if datos_partida:
            nombre_entrenador = datos_partida["nombre_entrenador"]
            equipo = datos_partida["equipo"]
            mochila = datos_partida["mochila"]
        else:
            notificar_evento("sin_partida")
            nombre_entrenador, equipo, mochila = nueva_partida()
    else:
        nombre_entrenador, equipo, mochila = nueva_partida()

    while True:
        opcion = pedir_opcion_menu_principal(nombre_entrenador, equipo, mochila)

        match opcion:
            case 1:
                if not any(poke.salud_actual > 0 for poke in equipo.pokemon):
                    notificar_evento("equipo_debilitado")
                    continue
                menu_rutas(nombre_entrenador, equipo, mochila)

            case 2:
                if zona_segura(equipo, mochila, nombre_entrenador) == "fin":
                    break

            case 3:
                pokemon_elegido = pedir_pokemon_ficha(equipo.pokemon)
                if pokemon_elegido is not None:
                    ficha_pokemon(pokemon_elegido)

            case 4:
                gestionar_mochila(equipo, mochila)

            case 5:
                try:
                    guardar_partida(nombre_entrenador, equipo, mochila)
                    notificar_evento("guardado_ok")
                except ErrorGuardado as error:
                    notificar_evento("guardado_error", detalle=str(error))

            case 6:
                notificar_evento("salir")
                break