'''Modelo de mochila e inventario del entrenador para Pokémon Gen III.

Administra el dinero en Pokédolares (₽) y las cantidades de objetos
poseídos por el jugador mediante encapsulamiento y validación estricta.
'''

from config import DINERO_INICIAL
from modelos.objeto import OBJETOS


class Mochila:
    '''Inventario del entrenador por identificador de objeto y cantidad.

    Atributos:
        dinero (int): Saldo actual disponible (solo lectura; se modifica
            mediante `ganar()` y `gastar()`).
    '''

    def __init__(
        self,
        objetos: dict[str, int] | None = None,
        dinero: int = DINERO_INICIAL,
        medallas: list[str] | None = None,
    ):
        '''Inicializa la mochila validando el saldo inicial y los objetos.

        Args:
            objetos: Diccionario opcional `{identificador: cantidad}` inicial.
            dinero: Saldo inicial en Pokédolares (por defecto `DINERO_INICIAL`).

        Raises:
            ValueError: Si `dinero` es inválido o algún objeto inicial no existe
                o tiene una cantidad inválida.
        '''
        # Diccionario privado para evitar modificaciones directas desde fuera
        self.__objetos: dict[str, int] = {}

        if isinstance(dinero, bool) or not isinstance(dinero, int) or dinero < 0:
            raise ValueError("Las pokémonedas iniciales deben ser un entero no negativo.")

        # Saldo privado validado una sola vez al construir la instancia
        self.__dinero: int = dinero
        self.__medallas = list(medallas or [])
        if any(not isinstance(medalla, str) or not medalla.strip() for medalla in self.__medallas):
            raise ValueError("Cada medalla debe tener un nombre válido.")

        for identificador, cantidad in (objetos or {}).items():
            if (
                identificador not in OBJETOS
                or isinstance(cantidad, bool)
                or not isinstance(cantidad, int)
                or cantidad < 0
            ):
                raise ValueError(f"Contenido de mochila inválido: {identificador}")

            # Solo se almacenan objetos con al menos 1 unidad
            if cantidad > 0:
                self.__objetos[identificador] = cantidad

    # --------------------------------------------------------
    # ECONOMÍA DEL ENTRENADOR
    # --------------------------------------------------------

    @property
    def dinero(self) -> int:
        '''Devuelve el saldo actual disponible en Pokédolares.'''
        return self.__dinero

    @property
    def medallas(self) -> tuple[str, ...]:
        '''Devuelve las medallas obtenidas en el desafío de Kanto.'''
        return tuple(self.__medallas)

    def otorgar_medalla(self, medalla: str) -> bool:
        '''Registra una medalla una sola vez y conserva el progreso al guardar.'''
        if not isinstance(medalla, str) or not medalla.strip():
            raise ValueError("El nombre de la medalla no puede estar vacío.")
        medalla = medalla.strip()
        if medalla in self.__medallas:
            return False
        self.__medallas.append(medalla)
        return True

    def ganar(self, cantidad: int) -> None:
        '''Suma Pokédolares al saldo actual tras validar la cantidad.

        Args:
            cantidad: Monto entero no negativo a sumar.

        Raises:
            ValueError: Si `cantidad` no es un entero válido o es negativa.
        '''
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad a ganar debe ser un entero no negativo.")
        self.__dinero += cantidad

    def gastar(self, cantidad: int) -> bool:
        '''Descuenta Pokédolares si el saldo actual cubre el monto solicitado.

        Args:
            cantidad: Monto entero no negativo a descontar.

        Returns:
            bool: `True` si había saldo suficiente y se descontó; `False` si no alcanzó.

        Raises:
            ValueError: Si `cantidad` no es un entero válido o es negativa.
        '''
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad a gastar debe ser un entero no negativo.")
        if self.__dinero < cantidad:
            return False
        self.__dinero -= cantidad
        return True

    # --------------------------------------------------------
    # GESTIÓN DE OBJETOS
    # --------------------------------------------------------

    def cantidad(self, identificador: str) -> int:
        '''Devuelve cuántas unidades de un objeto posee el jugador (0 si no tiene).

        Args:
            identificador: Clave interna del objeto en `OBJETOS`.

        Returns:
            int: Cantidad de unidades disponibles.
        '''
        return self.__objetos.get(identificador, 0)

    def agregar(self, identificador: str, cantidad: int = 1) -> bool:
        '''Añade unidades de un objeto válido del catálogo a la mochila.

        Args:
            identificador: Clave interna del objeto en `OBJETOS`.
            cantidad: Número entero positivo de unidades a agregar (por defecto 1).

        Returns:
            bool: `True` si se añadieron; `False` si el objeto o cantidad no son válidos.
        '''
        if (
            identificador not in OBJETOS
            or isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            return False

        self.__objetos[identificador] = self.cantidad(identificador) + cantidad
        return True

    def quitar(self, identificador: str, cantidad: int = 1) -> bool:
        '''Descuenta unidades de un objeto si hay suficiente stock en la mochila.

        Si la cantidad restante llega a 0, elimina la entrada del inventario.

        Args:
            identificador: Clave interna del objeto en `OBJETOS`.
            cantidad: Número entero positivo de unidades a retirar (por defecto 1).

        Returns:
            bool: `True` si se retiraron las unidades; `False` si faltó stock o es inválido.
        '''
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
            or self.cantidad(identificador) < cantidad
        ):
            return False

        restante = self.cantidad(identificador) - cantidad
        if restante > 0:
            self.__objetos[identificador] = restante
        else:
            # Elimina la clave cuando llega a 0 para no mantener ítems vacíos
            self.__objetos.pop(identificador, None)
        return True

    def listar(self) -> list[tuple]:
        '''Devuelve una lista de tuplas `(objeto, cantidad)` con el inventario actual.

        Returns:
            list[tuple]: Pares `(instancia_objeto, cantidad_entera)`.
        '''
        return [
            (OBJETOS[identificador], cantidad)
            for identificador, cantidad in self.__objetos.items()
        ]

    # --------------------------------------------------------
    # PERSISTENCIA (EXPORTAR / CARGAR)
    # --------------------------------------------------------

    def exportar_datos(self) -> dict:
        '''Serializa los objetos y el saldo en un diccionario listo para JSON.'''
        return {
            "objetos": dict(self.__objetos),
            "dinero": self.dinero,
            "medallas": list(self.__medallas),
        }

    @classmethod
    def cargar_datos(cls, datos: dict | None) -> "Mochila":
        '''Reconstruye una `Mochila` a partir de un diccionario de partida guardada.

        Args:
            datos: Diccionario con claves opcionales `'objetos'` y `'dinero'`.

        Returns:
            Mochila: Nueva instancia reconstruida.
        '''
        datos = datos or {}
        return cls(
            objetos=datos.get("objetos", {}),
            dinero=datos.get("dinero", DINERO_INICIAL),
            medallas=datos.get("medallas", []),
        )