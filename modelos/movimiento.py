'''Modelo de movimiento de batalla para Pokémon Gen III.

Define la clase `Movimiento` con encapsulamiento, validación de atributos,
recuperación de PP y evaluación de precisión en combate.
'''

import random
from datos.tipos_evoluciones import TIPOS


class Movimiento:
    '''Representa un ataque o movimiento de estado de la Tercera Generación.

    Atributos:
        nombre (str): Nombre del movimiento.
        tipo (str): Tipo elemental en minúscula sin tilde (ej. 'fuego', 'agua').
        categoria (str): Categoría del movimiento ('fisico', 'especial' o 'estado').
        potencia (int): Potencia base del movimiento (0 para movimientos de estado).
        precision (int): Precisión base en porcentaje (1 a 100).
        pp (int): Puntos de poder (PP) actuales disponibles.
        pp_max (int): Máximo de PP base del movimiento.
        prioridad (int): Prioridad de turno en combate.
        objetivo (str): Objetivo esperado del movimiento.
        efecto_estado (str): Estado alterado asociado ('none', 'burn', etc.).
        prob_estado (int): Probabilidad de aplicar el estado alterado (0 a 100).
        cambios_stats (tuple): Cambios de etapas de estadísticas asociados.
        prob_stat (int): Probabilidad de aplicar los cambios de estadísticas (0 a 100).
    '''

    def __init__(
        self,
        nombre: str,
        tipo: str,
        categoria: str,
        potencia: int,
        precision: int,
        pp: int = 15,
        prioridad: int = 0,
        objetivo: str = "selected-pokemon",
        efecto_estado: str = "none",
        prob_estado: int = 0,
        cambios_stats=None,
        prob_stat: int = 0,
    ):
        '''Inicializa y valida un `Movimiento` con sus reglas y PP iniciales.'''
        if tipo not in TIPOS:
            raise ValueError(f"Tipo desconocido para {nombre}: {tipo}")
        if categoria not in ("fisico", "especial", "estado"):
            raise ValueError(f"Categoría inválida para {nombre}: {categoria}")
        if isinstance(pp, bool) or not isinstance(pp, int) or pp < 1:
            raise ValueError(f"Los PP máximos de {nombre} deben ser al menos 1")

        # Atributos privados: configuración inmutable expuesta como solo lectura
        self.__nombre = nombre
        self.__tipo = tipo
        self.__categoria = categoria
        self.__pp_max = pp
        self.__prioridad = prioridad
        self.__objetivo = objetivo
        self.__efecto_estado = efecto_estado
        self.__prob_estado = prob_estado
        self.__cambios_stats = tuple(cambios_stats or ())
        self.__prob_stat = prob_stat

        # Atributos modificables validados a través de sus propiedades
        self.potencia = potencia
        self.precision = precision
        self.pp = pp

    # --------------------------------------------------------
    # PROPIEDADES DE SOLO LECTURA
    # --------------------------------------------------------

    @property
    def nombre(self) -> str:
        '''Devuelve el nombre del movimiento.'''
        return self.__nombre

    @property
    def tipo(self) -> str:
        '''Devuelve el tipo elemental del movimiento.'''
        return self.__tipo

    @property
    def categoria(self) -> str:
        '''Devuelve la categoría ('fisico', 'especial' o 'estado').'''
        return self.__categoria

    @property
    def pp_max(self) -> int:
        '''Devuelve la cantidad máxima de PP del movimiento.'''
        return self.__pp_max

    @property
    def prioridad(self) -> int:
        '''Devuelve la prioridad de ejecución en combate.'''
        return self.__prioridad

    @property
    def objetivo(self) -> str:
        '''Devuelve el objetivo del movimiento.'''
        return self.__objetivo

    @property
    def efecto_estado(self) -> str:
        '''Devuelve el nombre del efecto de estado alterado.'''
        return self.__efecto_estado

    @property
    def prob_estado(self) -> int:
        '''Devuelve la probabilidad porcentual del efecto de estado.'''
        return self.__prob_estado

    @property
    def cambios_stats(self) -> tuple:
        '''Devuelve una tupla con los cambios de estadísticas del movimiento.'''
        return self.__cambios_stats

    @property
    def prob_stat(self) -> int:
        '''Devuelve la probabilidad porcentual de aplicar cambios de stats.'''
        return self.__prob_stat

    # --------------------------------------------------------
    # PROPIEDADES MODIFICABLES CON VALIDACIÓN
    # --------------------------------------------------------

    @property
    def potencia(self) -> int:
        '''Devuelve la potencia actual del movimiento.'''
        return self._potencia

    @potencia.setter
    def potencia(self, nuevo_valor: int) -> None:
        '''Valida y actualiza la potencia (no permite valores negativos).'''
        if nuevo_valor is None or isinstance(nuevo_valor, bool) or nuevo_valor < 0:
            raise ValueError("La potencia no puede ser negativa")
        self._potencia = int(nuevo_valor)

    @property
    def precision(self) -> int:
        '''Devuelve la precisión base del movimiento (1 a 100).'''
        return self._precision

    @precision.setter
    def precision(self, nuevo_valor: int) -> None:
        '''Valida y actualiza la precisión dentro del rango [1, 100].'''
        if nuevo_valor is None or isinstance(nuevo_valor, bool) or not 1 <= nuevo_valor <= 100:
            raise ValueError(
                f"La precisión de {self.nombre} debe estar entre 1 y 100"
            )
        self._precision = int(nuevo_valor)

    @property
    def pp(self) -> int:
        '''Devuelve los PP actuales del movimiento.'''
        return self._pp

    @pp.setter
    def pp(self, valor: int) -> None:
        '''Ajusta los PP actuales manteniéndolos entre 0 y `pp_max`.'''
        self._pp = max(0, min(int(valor), self.pp_max))

    # --------------------------------------------------------
    # GESTIÓN DE PP Y MECÁNICAS EN COMBATE
    # --------------------------------------------------------

    def recuperar_pp(self, cantidad: int | None = None) -> int:
        '''Restaura PP del movimiento hasta el máximo permitido.

        Si `cantidad` es `None`, recupera todos los PP hasta `pp_max`.
        Si se indica una cantidad, suma esos PP sin superar `pp_max`.

        Args:
            cantidad: Cantidad de PP a recuperar o `None` para llenar al máximo.

        Returns:
            int: Cantidad exacta de PP recuperados.
        '''
        if cantidad is None:
            cantidad = self.pp_max
        cantidad = max(0, int(cantidad))

        pp_antes = self.pp
        self.pp = self.pp + cantidad
        return self.pp - pp_antes

    def impacta(self, mult_precision: float = 1.0) -> bool:
        '''Determina si el movimiento acierta aplicando un multiplicador de precisión.

        Args:
            mult_precision: Multiplicador acumulado de precisión/evasión en combate.

        Returns:
            bool: `True` si el ataque acierta, `False` si falla.
        '''
        prob_final = min(100, max(1, int(self.precision * mult_precision)))
        return random.randint(1, 100) <= prob_final

    def __repr__(self) -> str:
        '''Devuelve una representación legible del movimiento para depuración.'''
        return (
            f"Movimiento({self.nombre!r}, {self.tipo!r}, {self.categoria!r}, "
            f"pot={self.potencia}, prec={self.precision}, pp={self.pp})"
        )