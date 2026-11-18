import random
from config import TIPOS

# ============================================================
# CLASE MOVIMIENTO Y MéTODOS DE VISUALIZACIÓN
# ============================================================

class Movimiento:
    '''Representa un movimiento de Pokémon Gen III (Físico, Especial o Estado).'''
    def __init__(
        self,
        nombre,
        tipo,
        categoria,
        potencia,
        precision,
        pp=15,
        prioridad=0,
        objetivo="selected-pokemon",
        efecto_estado="none",
        prob_estado=0,
        cambios_stats=None,
        prob_stat=0,
    ):
        if tipo not in TIPOS:
            raise ValueError(f"Tipo desconocido para {nombre}: {tipo}")
        if categoria not in ("fisico", "especial", "estado"):
            raise ValueError(f"Categoría inválida para {nombre}: {categoria}")
        if pp < 1:
            raise ValueError(f"Los PP máximos de {nombre} deben ser al menos 1")

        # Atributos Privados (Solo lectura mediante properties))
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

        # Atributos Protegidos (Usan setters para validarse)
        self.potencia = potencia
        self.precision = precision
        self.pp = pp

    # --- PROPERTIES (SOLO LECTURA) ---
    @property
    def nombre(self):
        return self.__nombre

    @property
    def tipo(self):
        return self.__tipo

    @property
    def categoria(self):
        return self.__categoria

    @property
    def pp_max(self):
        return self.__pp_max

    @property
    def prioridad(self):
        return self.__prioridad

    @property
    def objetivo(self):
        return self.__objetivo

    @property
    def efecto_estado(self):
        return self.__efecto_estado

    @property
    def prob_estado(self):
        return self.__prob_estado

    @property
    def cambios_stats(self):
        return self.__cambios_stats

    @property
    def prob_stat(self):
        return self.__prob_stat
    
    # --- PROPERTIES Y SETTERS (MODIFICABLES CON VALIDACIÓN) ---
    @property
    def potencia(self):
        return self._potencia

    @potencia.setter
    def potencia(self, nuevo_valor):
        if nuevo_valor < 0:
            raise ValueError("La potencia no puede ser negativa")
        self._potencia = nuevo_valor

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, nuevo_valor):
        if not 1 <= nuevo_valor <= 100:
            raise ValueError(f"La precisión de {self.nombre} debe estar entre 1 y 100")
        self._precision = nuevo_valor

    @property
    def pp(self):
        return self._pp

    @pp.setter
    def pp(self, valor):
        self._pp = max(0, min(int(valor), self.pp_max))

    # ---------------- MECÁNICAS EN COMBATE ----------------
    def impacta(self, mult_precision=1.0):
        '''Evalúa si el movimiento acierta considerando precisión y evasión en combate.'''
        prob_final = min(100, max(1, int(self.precision * mult_precision)))
        return random.randint(1, 100) <= prob_final
 
 
    def __repr__(self):
        '''Devuelve la representación en cadena del movimiento para depuración.'''
        # El sufijo '!r' fuerza el uso de repr() en los textos, agregando comillas automáticas
        return (
            f"Movimiento({self.nombre!r}, {self.tipo!r}, {self.categoria!r}, "
            f"pot={self.potencia}, prec={self.precision}, pp={self.pp})"
        )