'''Punto de entrada principal de la aplicación.

Responsabilidad única: verificar que los datos del juego existan y sean
válidos antes de iniciar el flujo principal.
'''

import sys
from servicios.validador_datos import validar_datos


def main() -> None:
    '''Valida los archivos base y arranca el juego si todo está correcto.'''
    try:
        # Se comprueba antes de importar `juego` para que un error de datos
        # se capture aquí y no a mitad de la carga de módulos.
        validar_datos()
    except (FileNotFoundError, ValueError) as error:
        print(f"\nError crítico en los datos del juego: {error}")
        print("Ejecuta primero el generador/cargador de datos antes de jugar.\n")
        sys.exit(1)

    # Import diferido a propósito: evita cargar repositorios y estados
    # si la validación inicial de datos ya falló.
    from juego import iniciar_juego
    iniciar_juego()


if __name__ == "__main__":
    main()