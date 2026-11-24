'''Modelos de Pokémon con jerarquía de herencia multinivel (Gen III).

Jerarquía:
- Clase abuela: `Pokemon` (reglas base, estadísticas, combate y persistencia).
- Clase madre: `PokemonCapturable` (datos de encuentro/captura en el mundo).
- Clases hijas: `PokemonSalvaje` y `PokemonAtrapado` (entrenador y apodo).
'''

import random
from config import NIVEL_MAXIMO
from servicios.catalogos import DICCIONARIO_MOVIMIENTOS, DICCIONARIO_POKEMON
from sistemas.estadisticas import (
    calcular_estadisticas,
    exp_para_nivel,
    generar_movimientos,
    multiplicador_etapa,
    naturaleza_aleatoria,
)


# ============================================================
# CLASE ABUELA: POKEMON
# ============================================================

class Pokemon:
    '''Representa la entidad base de cualquier Pokémon en el juego.

    Atributos:
        nivel (int): Nivel actual entre 1 y `NIVEL_MAXIMO`.
        exp_actual (int): Experiencia acumulada total.
        movimientos (list): Lista de hasta 4 objetos `Movimiento` conocidos.
        estado_alterado (str | None): Estado persistente ('burn', 'paralysis',
            'poison', 'sleep', 'freeze' o None).
        turnos_estado (int): Contador de turnos restantes para estados temporales.
    '''

    def __init__(self, nombre: str, nivel: int = 1, naturaleza: str | None = None):
        '''Inicializa un Pokémon validando especie, nivel y estadísticas base.'''
        if nombre not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nombre}")

        if not isinstance(nivel, int) or isinstance(nivel, bool) or not 1 <= nivel <= NIVEL_MAXIMO:
            raise ValueError(f"El nivel debe estar entre 1 y {NIVEL_MAXIMO}.")

        datos = DICCIONARIO_POKEMON[nombre]

        # Atributos protegidos para subclases
        self._nombre = nombre
        self._tipos = tuple(datos["tipos"])

        # Estado público dinámico
        self.nivel = nivel
        self.exp_actual = exp_para_nivel(self.nivel)
        self.movimientos = generar_movimientos(nombre, self.nivel)

        # Atributos privados calculados
        self.__naturaleza = naturaleza or naturaleza_aleatoria()
        self.__exp_siguiente_nivel = exp_para_nivel(self.nivel + 1)
        self.__estadisticas = calcular_estadisticas(
            datos["stats_base"], self.nivel, self.__naturaleza
        )

        # Salud actual protegida (se modifica mediante propiedades o métodos)
        self._salud_actual = self.__estadisticas["vida"]

        # Estado alterado persistente y contadores de combate
        self.estado_alterado = None
        self.turnos_estado = 0
        self.resetear_combate()

    @property
    def es_capturable(self) -> bool:
        '''Indica si el Pokémon puede ser capturado; la base no es capturable.'''
        return False

    def preparar_turno(self) -> str:
        '''Devuelve una presentación genérica para el turno de combate.'''
        return f" {self.nombre_visible} se prepara para combatir."

    # --------------------------------------------------------
    # COMBATE Y ESTADOS ALTERADOS
    # --------------------------------------------------------

    def resetear_combate(self) -> None:
        '''Reinicia modificadores de estadísticas (-6 a +6) y confusión.'''
        self._estados = {
            "ataque": 0,
            "defensa": 0,
            "atq_esp": 0,
            "def_esp": 0,
            "velocidad": 0,
            "precision": 0,
            "evasion": 0,
        }
        self.confuso = False
        self.turnos_confusion = 0

    def modificar_estado(self, stat: str, cambio: int) -> int:
        '''Ajusta el nivel de una estadística en combate dentro de [-6, +6].

        Returns:
            int: Variación real aplicada (0 si alcanzó el límite).
        '''
        if stat not in self._estados:
            return 0
        anterior = self._estados[stat]
        nuevo = max(-6, min(6, anterior + cambio))
        self._estados[stat] = nuevo
        return nuevo - anterior

    def aplicar_estado(self, estado: str, tipo_ataque: str | None = None) -> bool:
        '''Intenta aplicar un estado alterado respetando inmunidades de Gen III.

        Returns:
            bool: True si se aplicó el estado, False si ya tenía uno o es inmune.
        '''
        if self.estado_alterado is not None:
            return False

        if estado == "burn" and "fuego" in self._tipos:
            return False
        if estado == "poison" and ("veneno" in self._tipos or "acero" in self._tipos):
            return False
        if estado == "freeze" and "hielo" in self._tipos:
            return False
        if estado == "paralysis" and tipo_ataque == "electrico" and "tierra" in self._tipos:
            return False

        self.estado_alterado = estado
        if estado == "sleep":
            self.turnos_estado = random.randint(1, 3)
        return True

    # --------------------------------------------------------
    # PROPIEDADES Y ESTADÍSTICAS EFECTIVAS
    # --------------------------------------------------------

    @property
    def nombre(self) -> str:
        '''Devuelve el nombre de especie del Pokémon.'''
        return self._nombre

    @property
    def especie(self) -> str:
        '''Alias de lectura para la especie del Pokémon.'''
        return self._nombre

    @property
    def nombre_visible(self) -> str:
        '''Nombre a mostrar en pantalla (las subclases con apodo pueden sobrescribirlo).'''
        return self._nombre

    @property
    def tipos(self) -> tuple[str, ...]:
        '''Tupla con los tipos elementales del Pokémon.'''
        return self._tipos

    @property
    def naturaleza(self) -> str:
        '''Naturaleza asignada al Pokémon.'''
        return self.__naturaleza

    @property
    def salud_actual(self) -> int:
        '''Puntos de salud (PS) actuales.'''
        return self._salud_actual

    @salud_actual.setter
    def salud_actual(self, valor: int) -> None:
        '''Mantiene la salud actual acotada entre 0 y `salud_maxima`.'''
        self._salud_actual = max(0, min(int(valor), self.salud_maxima))

    @property
    def salud_maxima(self) -> int:
        '''Puntos de salud (PS) máximos calculados.'''
        return self.__estadisticas["vida"]

    @property
    def ataque(self) -> int:
        '''Ataque físico efectivo considerando etapas y quemadura en Gen III.'''
        val = int(
            self.__estadisticas["ataque"] * multiplicador_etapa(self._estados["ataque"])
        )
        if self.estado_alterado == "burn":
            val //= 2
        return max(1, val)

    @property
    def defensa(self) -> int:
        '''Defensa física efectiva considerando etapas de combate.'''
        return max(
            1,
            int(
                self.__estadisticas["defensa"]
                * multiplicador_etapa(self._estados["defensa"])
            ),
        )

    @property
    def ataque_especial(self) -> int:
        '''Ataque especial efectivo considerando etapas de combate.'''
        return max(
            1,
            int(
                self.__estadisticas["atq_esp"]
                * multiplicador_etapa(self._estados["atq_esp"])
            ),
        )

    @property
    def defensa_especial(self) -> int:
        '''Defensa especial efectiva considerando etapas de combate.'''
        return max(
            1,
            int(
                self.__estadisticas["def_esp"]
                * multiplicador_etapa(self._estados["def_esp"])
            ),
        )

    @property
    def velocidad(self) -> int:
        '''Velocidad efectiva considerando etapas y parálisis en Gen III.'''
        val = int(
            self.__estadisticas["velocidad"]
            * multiplicador_etapa(self._estados["velocidad"])
        )
        if self.estado_alterado == "paralysis":
            val //= 4
        return max(1, val)

    @property
    def mult_precision(self) -> float:
        '''Multiplicador actual de precisión en combate.'''
        return multiplicador_etapa(self._estados["precision"], es_precision_evasion=True)

    @property
    def mult_evasion(self) -> float:
        '''Multiplicador actual de evasión en combate.'''
        return multiplicador_etapa(self._estados["evasion"], es_precision_evasion=True)

    @property
    def exp_siguiente_nivel(self) -> int:
        '''Experiencia total requerida para alcanzar el siguiente nivel.'''
        return self.__exp_siguiente_nivel

    @property
    def barra_de_vida(self) -> str:
        '''Representación visual de PS con emojis proporcionales a la salud restante.'''
        total_barras = 20
        if self.salud_maxima == 0:
            return "⬜" * total_barras

        porcentaje = self.salud_actual / self.salud_maxima
        barras = int(porcentaje * total_barras)
        if self.salud_actual > 0 and barras == 0:
            barras = 1

        color = "🟩" if porcentaje > 0.5 else ("🟨" if porcentaje > 0.2 else "🟥")
        return (color * barras) + ("⬜" * (total_barras - barras))

    # --------------------------------------------------------
    # DAÑO, CURACIÓN Y EVOLUCIÓN / NIVEL
    # --------------------------------------------------------

    def recibir_danio(self, cantidad: int) -> None:
        '''Reduce la salud actual sin permitir valores negativos.'''
        cantidad = max(0, int(cantidad))
        self.salud_actual -= cantidad

    def curar(self, cantidad: int | None = None) -> int:
        '''Recupera PS hasta el máximo (o al 100 % si `cantidad` es None).

        Returns:
            int: Cantidad exacta de PS recuperados.
        '''
        if cantidad is None:
            cantidad = self.salud_maxima
        cantidad = max(0, int(cantidad))
        salud_antes = self.salud_actual
        self.salud_actual += cantidad
        return self.salud_actual - salud_antes

    def restaurar_pp_todos(self) -> int:
        '''Restaura al máximo los PP de todos los movimientos conocidos.

        Pensado para el Centro Pokémon (Enfermera Joy) o efectos de
        recuperación completa del equipo.

        Returns:
            int: Cantidad total de PP recuperados entre todos los movimientos.
        '''
        total_recuperado = 0
        for movimiento in self.movimientos:
            total_recuperado += movimiento.recuperar_pp()
        return total_recuperado

    def actualizar_exp_siguiente_nivel(self, nueva_exp: int) -> None:
        '''Actualiza el umbral de experiencia para el siguiente nivel.'''
        self.__exp_siguiente_nivel = max(0, int(nueva_exp))

    def recalcular_estadisticas(self) -> None:
        '''Recalcula las estadísticas según la especie, nivel y naturaleza actuales.'''
        datos = DICCIONARIO_POKEMON[self._nombre]
        self.__estadisticas = calcular_estadisticas(
            datos["stats_base"], self.nivel, self.__naturaleza
        )

    def cambiar_especie(self, nueva_especie: str) -> None:
        '''Actualiza la especie, tipos y estadísticas base al evolucionar.'''
        if nueva_especie not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nueva_especie}")
        datos = DICCIONARIO_POKEMON[nueva_especie]
        self._nombre = nueva_especie
        self._tipos = tuple(datos["tipos"])
        self.recalcular_estadisticas()

    # --------------------------------------------------------
    # PERSISTENCIA (EXPORTAR / CARGAR)
    # --------------------------------------------------------

    def exportar_datos(self) -> dict:
        '''Serializa el estado base del Pokémon en un diccionario compatible con JSON.'''
        return {
            "clase": self.__class__.__name__,
            "nombre": self._nombre,
            "nivel": self.nivel,
            "naturaleza": self.naturaleza,
            "exp_actual": self.exp_actual,
            "salud_actual": self.salud_actual,
            "estado_alterado": self.estado_alterado,
            "movimientos": [atq.nombre for atq in self.movimientos],
        }

    @classmethod
    def _restaurar_estado_comun(cls, pokemon: "Pokemon", datos: dict) -> "Pokemon":
        '''Aplica experiencia, movimientos, salud y estado alterado a una instancia.'''
        pokemon.exp_actual = max(
            datos.get("exp_actual", pokemon.exp_actual),
            exp_para_nivel(pokemon.nivel),
        )
        movimientos_validos = [
            DICCIONARIO_MOVIMIENTOS[m]
            for m in datos.get("movimientos", [])
            if m in DICCIONARIO_MOVIMIENTOS
        ]
        if movimientos_validos:
            pokemon.movimientos = movimientos_validos[:4]

        salud = datos.get("salud_actual", pokemon.salud_maxima)
        pokemon.salud_actual = max(0, min(int(salud), pokemon.salud_maxima))
        pokemon.estado_alterado = datos.get("estado_alterado")
        return pokemon

    @classmethod
    def cargar_datos(cls, datos: dict) -> "Pokemon":
        '''Reconstruye una instancia base de `Pokemon` desde un diccionario.'''
        # La clase concreta aporta sus campos de constructor sin inspeccionar su tipo.
        argumentos_extra = cls._argumentos_carga(datos)
        pokemon = cls(
            datos["nombre"],
            datos.get("nivel", 1),
            naturaleza=datos.get("naturaleza"),
            **argumentos_extra,
        )
        return cls._restaurar_estado_comun(pokemon, datos)

    @classmethod
    def _argumentos_carga(cls, datos: dict) -> dict:
        '''Devuelve los argumentos específicos de cada nivel para reconstruirlo.'''
        return {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.nombre!r}, nivel={self.nivel}, naturaleza={self.naturaleza!r})"
        )


# ============================================================
# CLASE MADRE: POKEMON CAPTURABLE
# ============================================================

class PokemonCapturable(Pokemon):
    '''Clase madre para Pokémon asociados a un encuentro o captura en el mundo.

    Agrega información de rareza y ruta/zona de origen sobre `Pokemon`.
    '''

    RAREZAS_VALIDAS = ("comun", "raro", "muy raro")

    def __init__(
        self,
        nombre: str,
        nivel: int = 1,
        rareza: str = "comun",
        ruta: str = "Desconocida",
        naturaleza: str | None = None,
    ):
        '''Inicializa un Pokémon capturable con su rareza y ruta de origen.'''
        super().__init__(nombre, nivel, naturaleza=naturaleza)
        if rareza not in self.RAREZAS_VALIDAS:
            raise ValueError(
                f"Rareza inválida. Usa una de estas opciones: {', '.join(self.RAREZAS_VALIDAS)}."
            )
        self.rareza = rareza
        self.ruta = ruta.strip() or "Desconocida"

    def exportar_datos(self) -> dict:
        '''Exporta los datos base junto con rareza y ruta.'''
        datos = super().exportar_datos()
        datos.update({"rareza": self.rareza, "ruta": self.ruta})
        return datos

    @classmethod
    def cargar_datos(cls, datos: dict) -> "PokemonCapturable":
        '''Reconstruye una instancia de `PokemonCapturable` desde un diccionario.'''
        # super() restaura estado común; la clase dinámica agrega sus propios datos.
        return super().cargar_datos(datos)

    @classmethod
    def _argumentos_carga(cls, datos: dict) -> dict:
        '''Añade al constructor los datos de rareza y ubicación de origen.'''
        argumentos = super()._argumentos_carga(datos)
        argumentos.update({
            "rareza": datos.get("rareza", "comun"),
            "ruta": datos.get("ruta", "Desconocida"),
        })
        return argumentos


# ============================================================
# CLASES HIJAS: POKEMON SALVAJE Y POKEMON ATRAPADO
# ============================================================

class PokemonSalvaje(PokemonCapturable):
    '''Clase hija para Pokémon salvajes encontrados en rutas o zonas.'''

    def __init__(
        self,
        nombre: str,
        nivel: int = 1,
        rareza: str = "comun",
        ruta: str = "Desconocida",
        naturaleza: str | None = None,
    ):
        '''Inicializa un Pokémon salvaje listo para un encuentro.'''
        super().__init__(
            nombre,
            nivel=nivel,
            rareza=rareza,
            ruta=ruta,
            naturaleza=naturaleza,
        )

    @property
    def es_capturable(self) -> bool:
        '''Los Pokémon salvajes son capturables por definición.'''
        return True

    def preparar_turno(self) -> str:
        '''Presenta la conducta de un oponente salvaje en su turno.'''
        return f"{super().preparar_turno()} ¡El Pokémon salvaje acecha!"


class PokemonAtrapado(PokemonCapturable):
    '''Clase hija para Pokémon atrapados o asignados a un entrenador (con apodo).'''

    def __init__(
        self,
        nombre: str,
        nivel: int = 1,
        entrenador: str = "Entrenador",
        apodo: str | None = None,
        rareza: str = "comun",
        ruta: str = "Desconocida",
        naturaleza: str | None = None,
    ):
        '''Inicializa un Pokémon de entrenador validando dueño y apodo opcional.'''
        super().__init__(
            nombre,
            nivel=nivel,
            rareza=rareza,
            ruta=ruta,
            naturaleza=naturaleza,
        )
        if not isinstance(entrenador, str) or not entrenador.strip():
            raise ValueError("El nombre del entrenador no puede estar vacío.")

        if apodo is not None:
            if not isinstance(apodo, str) or not apodo.strip():
                raise ValueError("El apodo debe contener texto.")
            if len(apodo.strip()) > 15:
                raise ValueError("El apodo no puede superar los 15 caracteres.")

        self.entrenador = entrenador.strip()
        self.apodo = apodo.strip() if apodo else None

    @property
    def nombre_visible(self) -> str:
        '''Devuelve el apodo si tiene uno asignado; de lo contrario, la especie.'''
        return self.apodo or self.especie

    def preparar_turno(self) -> str:
        '''Presenta al Pokémon como compañero del entrenador que lo posee.'''
        return (
            f"{super().preparar_turno()} ¡{self.entrenador} confía en "
            f"{self.nombre_visible}!"
        )

    def exportar_datos(self) -> dict:
        '''Exporta los datos heredados más el entrenador y el apodo.'''
        datos = super().exportar_datos()
        datos.update({"entrenador": self.entrenador, "apodo": self.apodo})
        return datos

    @classmethod
    def cargar_datos(cls, datos: dict) -> "PokemonAtrapado":
        '''Reconstruye una instancia de `PokemonAtrapado` desde un diccionario.'''
        # Cada nivel de la jerarquía agrega sus campos mediante el hook heredado.
        return super().cargar_datos(datos)

    @classmethod
    def _argumentos_carga(cls, datos: dict) -> dict:
        '''Añade al constructor entrenador y apodo tras los datos capturables.'''
        argumentos = super()._argumentos_carga(datos)
        argumentos.update({
            "entrenador": datos.get("entrenador", "Entrenador"),
            "apodo": datos.get("apodo"),
        })
        return argumentos


# Compatibilidad con partidas y módulos que aún usan el nombre anterior.
PokemonJugador = PokemonAtrapado