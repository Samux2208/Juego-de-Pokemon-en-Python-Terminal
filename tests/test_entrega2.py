'''Pruebas de aceptación para la herencia, objetos y flujo de la Entrega 2.

Ejecutar desde la raíz con ``python -m tests.test_entrega2``.
'''

import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from modelos.equipo import Equipo
from modelos.entrenador import LiderGimnasio
from modelos.movimiento import Movimiento
from modelos.mochila import Mochila
from modelos.objeto import CuraEstado, OBJETOS, Pocion
from modelos.pokemon import (
    Pokemon,
    PokemonAtrapado,
    PokemonCapturable,
    PokemonSalvaje,
)
from persistencia.guardado import cargar_partida, guardar_partida
from sistemas.combate import calcular_danio, combatir_entrenador


def ejecutar_pruebas() -> None:
    '''Ejecuta los asserts de herencia, combate, objetos y persistencia.'''
    # La clase atrapada hereda en tres niveles y exporta sus campos propios.
    assert issubclass(PokemonAtrapado, PokemonCapturable)
    assert issubclass(PokemonCapturable, Pokemon)

    jugador = PokemonAtrapado(
        "Charmander",
        5,
        entrenador="Entrenador de prueba",
        apodo="Chispa",
        ruta="Pueblo Paleta",
    )
    restaurado = PokemonAtrapado.cargar_datos(jugador.exportar_datos())
    assert restaurado.apodo == "Chispa"
    assert restaurado.entrenador == "Entrenador de prueba"
    assert restaurado.ruta == "Pueblo Paleta"
    assert "confía en Chispa" in restaurado.preparar_turno()

    # Todos los objetos reciben el mismo contexto mediante el mismo método.
    mochila = Mochila()
    equipo = Equipo([jugador])
    salvaje = PokemonSalvaje("Rattata", 3, ruta="Ruta 1")
    jugador.salud_actual -= 5
    jugador.estado_alterado = "poison"
    objetos = [
        OBJETOS["pokeball"],
        Pocion("prueba_pocion", "Poción de prueba", 1, 5),
        CuraEstado("prueba_antidoto", "Antídoto de prueba", 1, ("poison",)),
    ]
    contexto = {
        "equipo": equipo,
        "mochila": mochila,
        "rival": salvaje,
        "objetivo": jugador,
        "nombre_entrenador": "Entrenador de prueba",
    }
    with (
        patch("sistemas.captura._gestionar_captura", return_value=True),
        patch("modelos.objeto.imprimir_con_retraso"),
    ):
        resultados = [objeto.usar(contexto) for objeto in objetos]
    assert all(consumido for consumido, _ in resultados)
    assert resultados[0][1]
    assert jugador.estado_alterado is None

    # El daño es determinista al fijar la variación Gen III en su máximo.
    atacante = Pokemon("Charmander", 5, naturaleza="Fuerte")
    objetivo = Pokemon("Caterpie", 5, naturaleza="Fuerte")
    movimiento = Movimiento("Placaje", "normal", "fisico", 40, 100, pp=35)
    factor_nivel = (2 * atacante.nivel) // 5 + 2
    base = (
        (factor_nivel * atacante.ataque * movimiento.potencia)
        // objetivo.defensa
    ) // 50 + 2
    with patch("sistemas.combate.random.uniform", return_value=1.0):
        danio, efectividad = calcular_danio(atacante, movimiento, objetivo)
    assert danio == max(1, int(base * efectividad))

    atacante.movimientos = [movimiento]
    movimiento.pp = 0
    salud_antes = atacante.salud_actual
    atacante.recibir_danio(3)
    atacante.curar(3)
    assert atacante.salud_actual == salud_antes
    assert atacante.restaurar_pp_todos() == movimiento.pp_max
    assert movimiento.pp == movimiento.pp_max

    # La derrota del líder da medalla y declara victoria; caer ante él declara derrota.
    entrenador = PokemonAtrapado("Squirtle", 5, entrenador="Prueba")
    equipo_jugador = Equipo([entrenador])
    lider = LiderGimnasio(
        "Brock",
        [Pokemon("Geodude", 3)],
        gimnasio="Gimnasio Plateada",
        medalla="Medalla Roca",
    )

    def derrotar_rival(
        equipo_actual, rival, mochila_actual, capturable, nombre_entrenador
    ):
        '''Deja al rival debilitado para aislar la ruta de victoria del combate.'''
        rival.salud_actual = 0

    salida = io.StringIO()
    with (
        patch("sistemas.combate._turno_combate", side_effect=derrotar_rival),
        patch("sistemas.combate.time.sleep"),
        patch("sistemas.combate.imprimir_con_retraso", side_effect=print),
        redirect_stdout(salida),
    ):
        victoria = combatir_entrenador(
            equipo_jugador, mochila, lider, "Entrenador de prueba"
        )
    assert victoria
    assert "Medalla Roca" in mochila.medallas
    assert "🏆 ¡VICTORIA! Has completado el desafío de Kanto" in salida.getvalue()

    lider_derrota = LiderGimnasio(
        "Brock",
        [Pokemon("Geodude", 3)],
        gimnasio="Gimnasio Plateada",
        medalla="Medalla Roca",
    )

    def derrotar_jugador(
        equipo_actual, rival, mochila_actual, capturable, nombre_entrenador
    ):
        '''Debilita al equipo aliado para comprobar la condición de derrota del líder.'''
        equipo_actual.pokemon[0].salud_actual = 0

    salida = io.StringIO()
    with (
        patch("sistemas.combate._turno_combate", side_effect=derrotar_jugador),
        patch("sistemas.combate.time.sleep"),
        patch("sistemas.combate.imprimir_con_retraso", side_effect=print),
        redirect_stdout(salida),
    ):
        derrota = combatir_entrenador(
            equipo_jugador, Mochila(), lider_derrota, "Entrenador de prueba"
        )
    assert not derrota
    assert "💀 DERROTA" in salida.getvalue()

    # Guardado temporal atómico: recupera la subclase, apodo y medalla.
    with tempfile.TemporaryDirectory() as directorio:
        raiz = Path(directorio)
        archivo_partida = raiz / "partida.json"
        carpeta_backups = raiz / "backups"
        with (
            patch("persistencia.guardado.ARCHIVO_PARTIDA", archivo_partida),
            patch("persistencia.guardado.BACKUPS_DIR", carpeta_backups),
        ):
            guardar_partida("Entrenador de prueba", equipo, mochila)
            assert archivo_partida.exists()
            assert not archivo_partida.with_name(archivo_partida.name + ".tmp").exists()
            datos_cargados, aviso = cargar_partida()

    assert aviso is None
    assert datos_cargados["equipo"].pokemon[0].__class__ is PokemonAtrapado
    assert datos_cargados["equipo"].pokemon[0].apodo == "Chispa"
    assert datos_cargados["equipo"].pokemon[0].ruta == "Pueblo Paleta"
    assert "Medalla Roca" in datos_cargados["mochila"].medallas
    print("OK: todas las pruebas de la Entrega 2 pasaron.")


if __name__ == "__main__":
    ejecutar_pruebas()
