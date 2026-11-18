"""Punto de entrada del juego.

Responsabilidad única: verificar que los datos existen y arrancar el juego.
No contiene lógica de juego ni de interfaz.
"""
import sys
from servicios.validador_datos import validar_datos


def main() -> None:
    """Valida los datos y, solo si son correctos, inicia el juego.

    El import de `juego` es diferido (dentro de la función) a propósito:
    importar `juego` carga el repositorio y los JSON, y si faltan archivos
    el error debe ocurrir DENTRO del try/except, no antes.
    """
    try:
        validar_datos()  # Comprueba que los JSON de PokéAPI existen y son válidos
    except (FileNotFoundError, ValueError) as error:
        print(f"\n ❌ Error crítico en los datos del juego: {error}")
        print(" 💡 Ejecuta el script ETL de PokéAPI antes de iniciar.\n")
        sys.exit(1)  # Código 1 = terminación con error

    from juego import iniciar_juego  # Import diferido (ver docstring)
    iniciar_juego()


if __name__ == "__main__":
    main()