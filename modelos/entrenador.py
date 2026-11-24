'''Modelos de entrenadores para Pokémon Gen III (Rojo Fuego / Verde Hoja).

Define al `Entrenador` jugador y la jerarquía de rivales no jugables:
`EntrenadorNPC`, `Cazabichos` y `LiderGimnasio`, calculando las recompensas
monetarias según la fórmula oficial de Tercera Generación (pago_base * nivel).
'''

from modelos.equipo import Equipo
from modelos.mochila import Mochila


class Entrenador:
    '''Representa al jugador principal de la aventura.

    Atributos:
        nombre (str): Nombre del entrenador jugador.
        equipo (Equipo): Equipo activo y almacenamiento en PC.
        mochila (Mochila): Dinero e inventario de objetos del jugador.
    '''

    def __init__(
        self,
        nombre: str,
        equipo: Equipo | None = None,
        mochila: Mochila | None = None,
    ):
        '''Inicializa al entrenador jugador validando su nombre.'''
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del entrenador no puede estar vacío.")

        self.nombre: str = nombre.strip()
        self.equipo: Equipo = equipo if equipo is not None else Equipo()
        self.mochila: Mochila = mochila if mochila is not None else Mochila()


class EntrenadorNPC:
    '''Clase base para entrenadores rivales controlados por el juego.

    En Rojo Fuego / Verde Hoja, la recompensa se calcula multiplicando el
    `PAGO_BASE` de la clase de entrenador por el nivel de su Pokémon más fuerte
    (o el último Pokémon de su equipo).

    Atributos de clase:
        PAGO_BASE (int): Multiplicador base oficial de dinero por nivel en Gen III.
    '''

    PAGO_BASE: int = 20
    es_desafio_final: bool = False

    def __init__(
        self,
        nombre: str,
        equipo,
        recompensa: int | None = None,
        frase_inicio: str = "¡Te desafío a un combate Pokémon!",
        frase_derrota: str = "¡Has sido más fuerte de lo que esperaba!",
    ):
        '''Inicializa un entrenador rival y calcula su recompensa Gen III.'''
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del entrenador NPC no puede estar vacío.")

        lista_equipo = tuple(equipo or ())
        if not lista_equipo:
            raise ValueError("El equipo del entrenador NPC debe tener al menos un Pokémon.")

        self.nombre: str = nombre.strip()
        self._equipo: tuple = lista_equipo
        self.frase_inicio: str = frase_inicio
        self.frase_derrota: str = frase_derrota

        # Si no se fuerza una recompensa manual, aplica la fórmula oficial Gen III
        if recompensa is None:
            nivel_max = max(pokemon.nivel for pokemon in self._equipo)
            self._recompensa: int = self.PAGO_BASE * nivel_max
        else:
            if (
                isinstance(recompensa, bool)
                or not isinstance(recompensa, int)
                or recompensa < 0
            ):
                raise ValueError("La recompensa debe ser un entero no negativo.")
            self._recompensa: int = recompensa

    @property
    def equipo(self) -> tuple:
        '''Devuelve el equipo del rival como tupla inmutable.'''
        return self._equipo

    @property
    def recompensa(self) -> int:
        '''Devuelve los Pokédolares entregados al derrotar a este entrenador.'''
        return self._recompensa

    @property
    def activo(self):
        '''Devuelve el primer Pokémon consciente del rival o `None` si todos cayeron.'''
        for pokemon in self._equipo:
            if pokemon.salud_actual > 0:
                return pokemon
        return None

    @property
    def derrotado(self) -> bool:
        '''Devuelve `True` si todos los Pokémon del rival tienen 0 PS.'''
        return all(pokemon.salud_actual <= 0 for pokemon in self._equipo)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"nombre={self.nombre!r}, pokemon={len(self._equipo)}, recompensa={self.recompensa})"
        )

    def entregar_medalla(self, mochila) -> str | None:
        '''Entrega una recompensa especial; los entrenadores comunes no dan medalla.'''
        return None


class Cazabichos(EntrenadorNPC):
    '''Entrenador rival de rutas y bosques (pago base oficial Gen III: 12 ₽/nivel).'''

    PAGO_BASE: int = 12

    def __init__(
        self,
        nombre: str,
        equipo,
        recompensa: int | None = None,
        ruta: str = "Bosque Verde",
        frase_inicio: str = "¡Mis Pokémon bicho son los más fuertes del bosque!",
        frase_derrota: str = "¡Vaya! Mis bichos no pudieron contigo.",
    ):
        '''Inicializa un Cazabichos con pago oficial 12 × nivel máximo.'''
        super().__init__(
            nombre=nombre,
            equipo=equipo,
            recompensa=recompensa,
            frase_inicio=frase_inicio,
            frase_derrota=frase_derrota,
        )
        self.ruta: str = ruta.strip() if isinstance(ruta, str) and ruta.strip() else "Ruta"


class LiderGimnasio(EntrenadorNPC):
    '''Líder de gimnasio de Kanto (pago base oficial Gen III: 100 ₽/nivel).'''

    PAGO_BASE: int = 100
    es_desafio_final: bool = True

    def __init__(
        self,
        nombre: str,
        equipo,
        gimnasio: str,
        medalla: str,
        recompensa: int | None = None,
        frase_inicio: str = "¡Te mostraré la verdadera fuerza de este gimnasio!",
        frase_derrota: str = "¡Has demostrado ser digno de esta medalla!",
    ):
        '''Inicializa un Líder de Gimnasio con pago oficial 100 × nivel máximo.'''
        if not isinstance(gimnasio, str) or not gimnasio.strip():
            raise ValueError("El nombre del gimnasio no puede estar vacío.")
        if not isinstance(medalla, str) or not medalla.strip():
            raise ValueError("El nombre de la medalla no puede estar vacío.")

        super().__init__(
            nombre=nombre,
            equipo=equipo,
            recompensa=recompensa,
            frase_inicio=frase_inicio,
            frase_derrota=frase_derrota,
        )
        self.gimnasio: str = gimnasio.strip()
        self.medalla: str = medalla.strip()

    def entregar_medalla(self, mochila) -> str:
        '''Registra la medalla ganada en el progreso persistente de la mochila.'''
        mochila.otorgar_medalla(self.medalla)
        return self.medalla