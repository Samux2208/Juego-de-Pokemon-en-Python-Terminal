import random
from config import NIVEL_MAXIMO
from servicios.repositorio import DICCIONARIO_POKEMON, DICCIONARIO_MOVIMIENTOS
from sistemas.estadisticas import (
    exp_para_nivel,
    calcular_estadisticas,
    generar_movimientos,
    naturaleza_aleatoria,
    multiplicador_etapa
)

# ============================================================
# CLASE PRINCIPAL POKéMON
# ============================================================

class Pokemon:
    """Representa una instancia individual de un Pokémon en el juego.
    
    Atributos:
        nombre (str): Especie del Pokémon (debe existir en DICCIONARIO_POKEMON).
        nivel (int): Nivel actual entre 1 y NIVEL MAXIMO (por defecto 1).
        exp_actual (int): Puntos de experiencia acumulados.
        movimientos (list): Lista de hasta 4 objetos Movimiento conocidos.
        salud_actual (int): Puntos de salud (PS) restantes en combate.
    """
    def __init__(self, nombre, nivel=1, naturaleza=None):
        if nombre not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nombre}")
        
        if not isinstance(nivel, int) or not 1 <= nivel <= NIVEL_MAXIMO:
            raise ValueError(f"El nivel debe estar entre 1 y {NIVEL_MAXIMO}.")

        datos = DICCIONARIO_POKEMON[nombre]

        # PROTEGIDOS: Accesibles desde clases hijas, ocultos al exterior
        self._nombre = nombre
        self._tipos = tuple(datos["tipos"])
 
        # PÚBLICOS: Estado dinámico del Pokémon
        self.nivel = nivel
        self.exp_actual = exp_para_nivel(self.nivel)
        self.movimientos = generar_movimientos(nombre, self.nivel)
 
        # PRIVADOS: Estadísticas calculadas y umbral de experiencia
        self.__naturaleza = naturaleza or naturaleza_aleatoria()
        self.__exp_siguiente_nivel = exp_para_nivel(self.nivel + 1)
        self.__estadisticas = calcular_estadisticas(
            datos["stats_base"], self.nivel, self.__naturaleza)
 
        # PROTEGIDO: Se modifica con recibir_danio() / curar()
        self._salud_actual = self.__estadisticas["vida"]

        # Estado alterado persistente: None | 'burn' | 'paralysis' | 'poison' | 'sleep' | 'freeze'
        self.estado_alterado = None
        self.turnos_estado = 0

        # Estados volátiles de combate (estados y confusión)
        self.resetear_combate()

    # ============================================================
    # GESTIÓN DE COMBATE Y ESTADOS ALTERADOS
    # ============================================================

    def resetear_combate(self):
        '''Reinicia los niveles de cambio de estadísticas (-6 a +6) y la confusión.'''
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

    def modificar_estado(self, stat, cambio):
        '''Modifica el nivel de una estadística en combate entre -6 y +6.

        Retorna:
            int: La variación efectiva aplicada (0 si ya estaba en el límite).
        '''
        if stat not in self._estados:
            return 0
        anterior = self._estados[stat]
        nuevo = max(-6, min(6, anterior + cambio))
        self._estados[stat] = nuevo
        return nuevo - anterior

    def aplicar_estado(self, estado, tipo_ataque=None):
        '''Intenta aplicar un estado alterado respetando inmunidades oficiales de Gen III.

        Retorna:
            bool: True si el estado se aplicó; False si ya tenía estado o es inmune.
        '''
        if self.estado_alterado is not None:
            return False

        # Inmunidades por tipo elemental
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

    # ============================================================
    # PROPIEDADES Y ESTADÍSTICAS EFECTIVAS EN COMBATE
    # ============================================================

    # -- PROPIEDADES DE SOLO LECTURA ---
    @property
    def nombre(self):
        return self._nombre

    @property
    def especie(self):
        return self._nombre

    @property
    def nombre_visible(self):
        return self.nombre
 
    @property
    def tipos(self):
        return self._tipos

    @property
    def naturaleza(self):
      return self.__naturaleza

    @property
    def salud_actual(self):
        return self._salud_actual

    @salud_actual.setter
    def salud_actual(self, valor):
        '''Garantiza que la salud siempre se mantenga entre 0 y salud_maxima.'''
        self._salud_actual = max(0, min(int(valor), self.salud_maxima))
 
    @property
    def salud_maxima(self):
        return self.__estadisticas["vida"]
 
    @property
    def ataque(self):
        val = int(self.__estadisticas["ataque"] * multiplicador_etapa(self._estados["ataque"]))
        if self.estado_alterado == "burn":
            val //= 2
        return max(1, val)
 
    @property
    def defensa(self):
        return max(1, int(self.__estadisticas["defensa"] * multiplicador_etapa(self._estados["defensa"])))
 
    @property
    def ataque_especial(self):
        return max(1, int(self.__estadisticas["atq_esp"] * multiplicador_etapa(self._estados["atq_esp"])))
 
    @property
    def defensa_especial(self):
        return max(1, int(self.__estadisticas["def_esp"] * multiplicador_etapa(self._estados["def_esp"])))
 
    @property
    def velocidad(self):
        val = int(self.__estadisticas["velocidad"] * multiplicador_etapa(self._estados["velocidad"]))
        if self.estado_alterado == "paralysis":
            val //= 4
        return max(1, val)

    @property
    def mult_precision(self):
        '''Devuelve el multiplicador actual de precisión en combate.'''
        return multiplicador_etapa(self._estados["precision"], es_precision_evasion=True)

    @property
    def mult_evasion(self):
        '''Devuelve el multiplicador actual de evasión en combate.'''
        return multiplicador_etapa(self._estados["evasion"], es_precision_evasion=True)
    
    @property
    def exp_siguiente_nivel(self):
        return self.__exp_siguiente_nivel

    @property
    def barra_de_vida(self):
        '''Calcula la barra visual de salud con emojis proporcional a los PS actuales.'''
        total_barras = 20 # El tamaño fijo de tu barra visual

        # Evitamos división por cero si el Pokémon se debilita
        if self.salud_maxima == 0:
            return "⬜" * total_barras
            
        # Calculamos cuántas barras le quedan proporcionalmente
        porcentaje = self.salud_actual / self.salud_maxima
        barras = int(porcentaje * total_barras)

        # Garantiza al menos 1 barra visible si el Pokémon sigue consciente
        if self.salud_actual > 0 and barras == 0:
            barras = 1

        # Elegimos el color según la vida restante (Verde, Amarillo o Rojo)
        color = "🟩" if porcentaje > 0.5 else ("🟨" if porcentaje > 0.2 else "🟥")
        # Rellenamos lo que falta con cuadros blancos para mantener el ancho fijo
        return (color * barras) + ("⬜" * (total_barras - barras))


    # ---------------- CÁLCULO DE DAÑO EN COMBATE ----------------
    def recibir_danio(self, cantidad):
        '''Descuenta PS asegurando que nunca bajen de 0.'''
        cantidad = max(0, int(cantidad))
        self.salud_actual -= cantidad

    def curar(self, cantidad=None):
        '''Restaura PS hasta el máximo (si cantidad es None, cura al 100%).
        
        Devuelve:
            int: La cantidad exacta de PS recuperados.
        '''
        if cantidad is None:
            cantidad = self.salud_maxima
        cantidad = max(0, int(cantidad))
        salud_antes = self.salud_actual
        self.salud_actual += cantidad
        return self.salud_actual - salud_antes

    def cambiar_especie(self, nueva_especie):
        '''Actualiza la especie, tipos y estadísticas base del Pokémon al evolucionar.'''
        if nueva_especie not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nueva_especie}")

        datos = DICCIONARIO_POKEMON[nueva_especie]
        self._nombre = nueva_especie
        self._tipos = tuple(datos["tipos"])
        self.__estadisticas = calcular_estadisticas(
            datos["stats_base"], self.nivel, self.__naturaleza
        )

    def actualizar_exp_siguiente_nivel(self, nueva_exp):
        '''Actualiza el umbral de experiencia requerido para el siguiente nivel.'''
        self.__exp_siguiente_nivel = max(0, int(nueva_exp))

    def recalcular_estadisticas(self):
        '''Recalcula las estadísticas del Pokémon según su especie, nivel y naturaleza actuales.'''
        datos = DICCIONARIO_POKEMON[self._nombre]
        self.__estadisticas = calcular_estadisticas(
            datos["stats_base"], self.nivel, self.__naturaleza
        )

    def cambiar_especie(self, nueva_especie):
        '''Actualiza la especie, tipos y estadísticas base del Pokémon al evolucionar.'''
        if nueva_especie not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nueva_especie}")
        datos = DICCIONARIO_POKEMON[nueva_especie]
        self._nombre = nueva_especie
        self._tipos = tuple(datos["tipos"])
        self.recalcular_estadisticas()

    # ---------------- PERSISTENCIA (EXPORTAR / CARGAR) ----------------
    def exportar_datos(self):
        '''Convierte los datos del Pokémon en un diccionario sencillo para poder guardarlos.'''        
        # Armamos y devolvemos el diccionario final con los datos básicos
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
    def _restaurar_estado_comun(cls, pokemon, datos):
        '''Restaura experiencia, movimientos, salud y estado alterado.'''
        pokemon.exp_actual = max(
            datos.get("exp_actual", pokemon.exp_actual),
            exp_para_nivel(pokemon.nivel)
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
    def cargar_datos(cls, datos):
        '''Reconstruye una instancia base de Pokemon sin conocer a sus subclases.'''
        pokemon = cls(
            datos["nombre"],
            datos.get("nivel", 1),
            naturaleza=datos.get("naturaleza")
        )
        return cls._restaurar_estado_comun(pokemon, datos)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.nombre!r}, nivel={self.nivel}, naturaleza={self.naturaleza!r})"

# == CLASES HIJAS ===========================================
# PokemonJugador | Extiende Pokemon añadiendo entrenador y apodo.
# PokemonSalvaje | Extiende Pokemon añadiendo rareza y ruta de encuentro.
# ============================================================

class PokemonJugador(Pokemon):
    '''Pokémon que pertenece al entrenador y puede tener un apodo.

    Atributos:
        entrenador (str): Nombre del dueño del Pokémon.
        apodo (str | None): Nombre personalizado (máximo 15 caracteres) o None
    '''
    def __init__(self, nombre, nivel=1, entrenador="Entrenador", apodo=None, naturaleza=None):
        super().__init__(nombre, nivel, naturaleza=naturaleza)
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
    def nombre_visible(self):
        '''Devuelve el apodo si existe; de lo contrario, el nombre de la especie.'''
        return self.apodo or self.especie

    def exportar_datos(self):
        '''Convierte los datos base junto con el entrenador y el apodo.'''
        datos = super().exportar_datos()
        datos.update({"entrenador": self.entrenador, "apodo": self.apodo})
        return datos

    @classmethod
    def cargar_datos(cls, datos):
        pokemon = cls(
            datos["nombre"],
            datos.get("nivel", 1),
            entrenador=datos.get("entrenador", "Entrenador"),
            apodo=datos.get("apodo"),
            naturaleza=datos.get("naturaleza"),
        )
        return cls._restaurar_estado_comun(pokemon, datos)


class PokemonSalvaje(Pokemon):
    """Pokémon encontrado durante la exploración de una ruta.

    Atributos:
        rareza (str): Nivel de aparición ('comun', 'raro' o 'muy raro').
        ruta (str): Nombre de la zona donde apareció el Pokémon.
    """
    RAREZAS_VALIDAS = ("comun", "raro", "muy raro")

    def __init__(self, nombre, nivel=1, rareza="comun", ruta="Desconocida", naturaleza=None):
        super().__init__(nombre, nivel, naturaleza=naturaleza)
        if rareza not in self.RAREZAS_VALIDAS:
            raise ValueError(
                f"Rareza inválida. Usa una de estas opciones: {', '.join(self.RAREZAS_VALIDAS)}."
            )
        self.rareza = rareza
        self.ruta = ruta.strip() or "Desconocida"

    def exportar_datos(self):
        '''Convierte los datos base junto con su rareza y ruta de origen.'''
        datos = super().exportar_datos()
        datos.update({"rareza": self.rareza, "ruta": self.ruta})
        return datos

    @classmethod
    def cargar_datos(cls, datos):
        pokemon = cls(
            datos["nombre"],
            datos.get("nivel", 1),
            rareza=datos.get("rareza", "comun"),
            ruta=datos.get("ruta", "Desconocida"),
            naturaleza=datos.get("naturaleza"),
        )
        return cls._restaurar_estado_comun(pokemon, datos)