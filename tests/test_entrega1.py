'''Pruebas de aceptación para los requisitos de la Entrega 1.

Ejecutar desde la carpeta raíz:
    python -m tests.test_entrega1

Requiere los JSON de datos que usa el proyecto (datos/pokemon_gen3.json y
datos/movimientos_gen3.json), igual que el arranque normal del juego.
'''

from modelos.pokemon import Pokemon, PokemonAtrapado, PokemonSalvaje


def ejecutar_pruebas():
    # 1. Las dos clases hijas realmente heredan de Pokemon.
    jugador = PokemonAtrapado(
        "Charmander", 5, entrenador="Entrenador de prueba", apodo="Chispa"
    )
    salvaje = PokemonSalvaje(
        "Rattata", 4, rareza="comun", ruta="Ruta 1"
    )
    assert isinstance(jugador, Pokemon)
    assert isinstance(salvaje, Pokemon)

    # 2. Los datos propios de cada hija se guardan correctamente.
    assert jugador.entrenador == "Entrenador de prueba"
    assert jugador.nombre_visible == "Chispa"
    assert salvaje.rareza == "comun"
    assert salvaje.ruta == "Ruta 1"

    # 3. El método heredado modifica la salud y no permite valores negativos.
    salud_inicial = salvaje.salud_actual
    salvaje.recibir_danio(5)
    assert salvaje.salud_actual == max(0, salud_inicial - 5)

    # 4. Las propiedades de solo lectura no permiten asignación directa.
    try:
        jugador.salud_maxima = 999
    except AttributeError:
        pass
    else:
        raise AssertionError("salud_maxima debe ser una propiedad de solo lectura")

    # 5. Los constructores validan los datos específicos de las hijas.
    try:
        PokemonAtrapado("Charmander", 5, entrenador="")
    except ValueError:
        pass
    else:
        raise AssertionError("Se aceptó un nombre de entrenador vacío")

    try:
        PokemonSalvaje("Rattata", 4, rareza="legendario")
    except ValueError:
        pass
    else:
        raise AssertionError("Se aceptó una rareza no permitida")

    # 6. El método protegido de Pokemon se usa desde las hijas al reconstruirlas.
    restaurado = PokemonAtrapado.cargar_datos(jugador.exportar_datos())
    assert isinstance(restaurado, PokemonAtrapado)
    assert restaurado.nombre_visible == "Chispa"

    print("OK: todas las pruebas de la Entrega 1 pasaron.")


if __name__ == "__main__":
    ejecutar_pruebas()
