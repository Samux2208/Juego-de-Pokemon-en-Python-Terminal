from modelos.pokemon import Pokemon, PokemonAtrapado, PokemonSalvaje
from sistemas.estadisticas import efectividad_tipos

def pruebas_basicas():
    '''Pruebas sencillas de clases, herencia, validación y efectividad.'''
    pokemon = Pokemon("Pikachu", 5)
    assert pokemon.nombre == "Pikachu"
    assert efectividad_tipos("agua", ("fuego",)) == 2.0

    jugador = PokemonAtrapado("Charmander", 5, entrenador="Prueba")
    assert jugador.entrenador == "Prueba"
    assert isinstance(jugador, Pokemon)

    salvaje = PokemonSalvaje("Rattata", 4, rareza="comun", ruta="Ruta 1")
    assert isinstance(salvaje, Pokemon)

    vida_inicial = jugador.salud_actual
    jugador.recibir_danio(3)
    assert jugador.salud_actual == max(0, vida_inicial - 3)

    try:
        PokemonAtrapado("Charmander", 5, entrenador="")
    except ValueError:
        pass
    else:
        raise AssertionError("La validación del entrenador no rechazó un nombre vacío.")

    print("✓ Pruebas básicas superadas.\n")

pruebas_basicas()