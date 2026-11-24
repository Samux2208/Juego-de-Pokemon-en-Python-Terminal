'''Modelos de objetos y catálogo Gen III (Rojo Fuego / Verde Hoja).

Define la clase base `Objeto` y las subclases `Pokeball`, `Pocion`,
`Revivir`, `CuraEstado` y `PiedraEvolutiva`, junto al diccionario `OBJETOS`.
'''

from datos.tipos_evoluciones import EVOLUCIONES_OBJETO
from interfaz.mensajes import imprimir_con_retraso
from sistemas.evolucion import evolucionar_pokemon


class Objeto:
    '''Definición base de un objeto utilizable en mochila o tienda.

    Atributos:
        identificador (str): Clave interna única del objeto (ej. 'pokeball').
        nombre (str): Nombre visible en tienda y mochila (ej. 'Poké Ball').
        precio (int): Costo en Pokédolares (₽).
        en_tienda (bool): Indica si el objeto está disponible para comprar en tienda.
    '''

    requiere_objetivo: bool = False

    def __init__(self, identificador: str, nombre: str, precio: int, en_tienda: bool = True):
        '''Inicializa un objeto validando su precio base.'''
        if isinstance(precio, bool) or not isinstance(precio, int) or precio < 0:
            raise ValueError(f"El precio de '{nombre}' debe ser un entero no negativo.")

        self._identificador = identificador
        self._nombre = nombre
        self._precio = precio
        self.en_tienda = bool(en_tienda)

    @property
    def identificador(self) -> str:
        '''Devuelve la clave interna del objeto.'''
        return self._identificador

    @property
    def nombre(self) -> str:
        '''Devuelve el nombre visible del objeto.'''
        return self._nombre

    @property
    def precio(self) -> int:
        '''Devuelve el precio del objeto en Pokédolares (₽).'''
        return self._precio

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Aplica el objeto desde un contexto y devuelve uso y fin de combate.'''
        return False, False


class Pokeball(Objeto):
    '''Objeto de captura utilizado en combate contra Pokémon salvajes.

    Atributos:
        bonus (float): Multiplicador aplicado al ratio de captura.
    '''

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio: int,
        bonus: float,
        en_tienda: bool = True,
    ):
        '''Inicializa una Poké Ball validando su multiplicador de captura.'''
        super().__init__(identificador, nombre, precio, en_tienda=en_tienda)
        if bonus <= 0:
            raise ValueError(f"El bonus de '{nombre}' debe ser mayor que 0.")
        self.bonus = float(bonus)

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Lanza la Poké Ball; solo la captura exitosa termina el combate.'''
        rival = contexto.get("rival")
        if rival is None:
            return False, False
        if not rival.es_capturable:
            imprimir_con_retraso(" 🚫 ¡El entrenador rival desvió la Poké Ball!")
            return False, False

        from sistemas.captura import _gestionar_captura

        capturado = _gestionar_captura(
            rival,
            contexto["equipo"],
            contexto["mochila"],
            self.bonus,
            contexto.get("nombre_entrenador", "Entrenador"),
        )
        return True, bool(capturado)

class Pocion(Objeto):
    '''Medicina que restaura PS a un Pokémon consciente y herido.

    Atributos:
        curacion (int | None): PS restaurados (`None` indica recuperación total).
    '''

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio: int,
        curacion: int | None,
        en_tienda: bool = True,
    ):
        '''Inicializa una poción validando la cantidad de PS a restaurar.'''
        super().__init__(identificador, nombre, precio, en_tienda=en_tienda)
        if curacion is not None and (isinstance(curacion, bool) or curacion <= 0):
            raise ValueError(f"La curación de '{nombre}' debe ser positiva o None.")
        self.curacion = curacion

    requiere_objetivo = True

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Cura PS desde el objetivo del contexto; devuelve si tuvo efecto.'''
        pokemon = contexto.get("objetivo")
        if pokemon is None:
            return False, False
        if pokemon.salud_actual <= 0:
            imprimir_con_retraso(
                f" ¡{pokemon.nombre_visible} está debilitado y no puede usar una poción!"
            )
            return False, False

        if pokemon.salud_actual >= pokemon.salud_maxima:
            imprimir_con_retraso(
                f"❤️  ¡La vida de {pokemon.nombre_visible} ya está al máximo! No se puede curar.\n"
            )
            return False, False

        curacion = pokemon.curar(self.curacion)
        imprimir_con_retraso(
            f" 💚 ¡{pokemon.nombre_visible} recuperó {curacion} PS!"
        )
        return curacion > 0, False


class Revivir(Objeto):
    '''Medicina que reanima a un Pokémon debilitado con fracción de PS máximos.

    Atributos:
        fraccion_ps (float): Proporción de `salud_maxima` restaurada al reanimar.
    '''

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio: int,
        fraccion_ps: float = 0.5,
        en_tienda: bool = True,
    ):
        '''Inicializa un objeto de reanimación.'''
        super().__init__(identificador, nombre, precio, en_tienda=en_tienda)
        if not 0 < fraccion_ps <= 1.0:
            raise ValueError(f"La fracción de PS de '{nombre}' debe estar entre 0 y 1.")
        self.fraccion_ps = float(fraccion_ps)

    requiere_objetivo = True

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Reanima al objetivo debilitado y devuelve si el objeto tuvo efecto.'''
        pokemon = contexto.get("objetivo")
        if pokemon is None:
            return False, False
        if pokemon.salud_actual > 0:
            imprimir_con_retraso(
                f" ℹ️  {pokemon.nombre_visible} no está debilitado."
            )
            return False, False

        ps_a_recuperar = max(1, int(pokemon.salud_maxima * self.fraccion_ps))
        pokemon.curar(ps_a_recuperar)
        imprimir_con_retraso(
            f" ✨ ¡{pokemon.nombre_visible} volvió al combate con "
            f"{pokemon.salud_actual} PS!"
        )
        return True, False


class CuraEstado(Objeto):
    '''Medicina que elimina estados alterados persistentes en Gen III.

    Atributos:
        estados_objetivo (tuple[str, ...]): Estados que cura (vacía = cualquiera).
    '''

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio: int,
        estados_objetivo=(),
        en_tienda: bool = True,
    ):
        '''Inicializa un objeto curativo de estados alterados.'''
        super().__init__(identificador, nombre, precio, en_tienda=en_tienda)
        self.estados_objetivo = tuple(estados_objetivo)

    requiere_objetivo = True

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Limpia el estado alterado del objetivo si el remedio es compatible.'''
        pokemon = contexto.get("objetivo")
        if pokemon is None:
            return False, False
        estado_actual = getattr(pokemon, "estado_alterado", None)
        if not estado_actual:
            imprimir_con_retraso(
                f" ℹ️  {pokemon.nombre_visible} no tiene ningún problema de estado."
            )
            return False, False

        if self.estados_objetivo and estado_actual not in self.estados_objetivo:
            imprimir_con_retraso(
                f" ⚠️  {self.nombre} no tiene efecto sobre el estado de {pokemon.nombre_visible}."
            )
            return False, False

        pokemon.estado_alterado = None
        pokemon.turnos_estado = 0
        imprimir_con_retraso(f" 💚 ¡{pokemon.nombre_visible} ya está mejor!")
        return True, False


class PiedraEvolutiva(Objeto):
    '''Objeto evolutivo que hace evolucionar especies compatibles en Gen III.'''

    requiere_objetivo = True

    def __init__(
        self,
        identificador: str,
        nombre: str,
        precio: int,
        en_tienda: bool = True,
    ):
        '''Inicializa una piedra evolutiva.'''
        super().__init__(identificador, nombre, precio, en_tienda=en_tienda)

    def usar(self, contexto: dict) -> tuple[bool, bool]:
        '''Intenta evolucionar el objetivo y devuelve si la piedra tuvo efecto.'''
        pokemon = contexto.get("objetivo")
        if pokemon is None:
            return False, False
        evoluciones_compatibles = EVOLUCIONES_OBJETO.get(self.nombre, {})
        nueva_especie = evoluciones_compatibles.get(pokemon.especie)
        if not nueva_especie:
            return False, False

        evolucionar_pokemon(pokemon, nueva_especie)
        imprimir_con_retraso(f" ✨ ¡{pokemon.nombre_visible} evolucionó!")
        return True, False


# ============================================================
# CATÁLOGO MAESTRO (PRECIOS Y DISPONIBILIDAD ROJO FUEGO / VERDE HOJA)
# ============================================================

OBJETOS = {
    # --- Poké Balls ---
    "pokeball": Pokeball("pokeball", "Poké Ball", 200, 1.0, en_tienda=True),
    "superball": Pokeball("superball", "Super Ball", 600, 1.5, en_tienda=True),
    "ultraball": Pokeball("ultraball", "Ultra Ball", 1200, 2.0, en_tienda=True),

    # --- Medicinas: Restauración de PS y Reanimación ---
    "pocion": Pocion("pocion", "Poción", 300, 20, en_tienda=True),
    "superpocion": Pocion("superpocion", "Superpoción", 700, 50, en_tienda=True),
    "hiperpocion": Pocion("hiperpocion", "Hiperpoción", 1200, 200, en_tienda=True),
    "pocion_maxima": Pocion("pocion_maxima", "Poción Máxima", 2500, None, en_tienda=True),
    "revivir": Revivir("revivir", "Revivir", 1500, 0.5, en_tienda=True),

    # --- Medicinas: Estados Alterados ---
    "antidoto": CuraEstado("antidoto", "Antídoto", 100, ("poison",), en_tienda=True),
    "antiparalizante": CuraEstado(
        "antiparalizante", "Antiparalizante", 200, ("paralysis",), en_tienda=True
    ),
    "despertar": CuraEstado("despertar", "Despertar", 250, ("sleep",), en_tienda=True),
    "antiquemar": CuraEstado("antiquemar", "Antiquemar", 250, ("burn",), en_tienda=True),
    "antihielo": CuraEstado("antihielo", "Antihielo", 250, ("freeze",), en_tienda=True),
    "cura_total": CuraEstado("cura_total", "Cura Total", 600, (), en_tienda=True),

    # --- Piedras Evolutivas ---
    "piedra_fuego": PiedraEvolutiva("piedra_fuego", "Piedra Fuego", 2100, en_tienda=True),
    "piedra_agua": PiedraEvolutiva("piedra_agua", "Piedra Agua", 2100, en_tienda=True),
    "piedra_trueno": PiedraEvolutiva("piedra_trueno", "Piedra Trueno", 2100, en_tienda=True),
    "piedra_hoja": PiedraEvolutiva("piedra_hoja", "Piedra Hoja", 2100, en_tienda=True),
    "piedra_lunar": PiedraEvolutiva("piedra_lunar", "Piedra Lunar", 2100, en_tienda=False),
}