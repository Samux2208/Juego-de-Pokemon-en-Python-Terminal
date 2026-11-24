'''Modelo de equipo Pokémon y Sistema de Almacenamiento (PC) para Gen III.

Administra el equipo activo de hasta 6 Pokémon y el almacenamiento en PC
respetando las reglas básicas de Pokémon Rojo Fuego y Verde Hoja.
'''

from modelos.pokemon import Pokemon


class Equipo:
    '''Gestiona los Pokémon activos del entrenador y los almacenados en el PC.

    Atributos de clase:
        LIMITE (int): Capacidad máxima del equipo activo (6 Pokémon).
    '''

    LIMITE: int = 6

    def __init__(self, pokemon=None, pc=None):
        '''Inicializa el equipo activo y el almacenamiento del PC.

        Args:
            pokemon: Iterable inicial de Pokémon para el equipo activo.
            pc: Iterable inicial de Pokémon guardados en el PC.

        Raises:
            ValueError: Si el equipo inicial supera `LIMITE` (6 Pokémon).
        '''
        # Listas internas privadas para controlar mutaciones solo vía métodos
        self.__pokemon = list(pokemon or [])
        self.__pc = list(pc or [])

        if len(self.__pokemon) > self.LIMITE:
            raise ValueError(f"El equipo no puede superar {self.LIMITE} Pokémon.")

    # --------------------------------------------------------
    # PROPIEDADES DE CONSULTA
    # --------------------------------------------------------

    @property
    def pokemon(self) -> tuple:
        '''Devuelve una copia inmutable (tupla) del equipo activo.'''
        return tuple(self.__pokemon)

    @property
    def pc(self) -> tuple:
        '''Devuelve una copia inmutable (tupla) de los Pokémon en el PC.'''
        return tuple(self.__pc)

    @property
    def activo(self):
        '''Devuelve el primer Pokémon consciente del equipo o `None` si todos cayeron.'''
        for poke in self.__pokemon:
            if poke.salud_actual > 0:
                return poke
        return None

    # --------------------------------------------------------
    # GESTIÓN DE EQUIPO Y SISTEMA DE ALMACENAMIENTO (PC)
    # --------------------------------------------------------

    def agregar(self, pokemon) -> bool:
        '''Añade un Pokémon al equipo activo si hay espacio disponible.

        Args:
            pokemon: Instancia de Pokémon a incorporar al equipo.

        Returns:
            bool: `True` si se añadió; `False` si el equipo ya está lleno.
        '''
        if pokemon is None or len(self.__pokemon) >= self.LIMITE:
            return False
        self.__pokemon.append(pokemon)
        return True

    def enviar_al_pc(self, op: int) -> bool:
        '''Envía un Pokémon del equipo activo al PC manteniendo al menos 1 activo.

        Args:
            op: Índice del Pokémon dentro del equipo activo.

        Returns:
            bool: `True` si se transfirió; `False` si el índice no es válido
                o si solo queda un Pokémon en el equipo.
        '''
        if isinstance(op, bool) or not isinstance(op, int):
            return False
        if not 0 <= op < len(self.__pokemon) or len(self.__pokemon) == 1:
            return False
        self.__pc.append(self.__pokemon.pop(op))
        return True

    def reemplazar(self, op: int, nuevo_pokemon) -> bool:
        '''Sustituye un Pokémon del equipo por otro, enviando el anterior al PC.

        Args:
            op: Índice del Pokémon en el equipo activo a sustituir.
            nuevo_pokemon: Instancia de Pokémon que ocupará esa posición.

        Returns:
            bool: `True` si el reemplazo se realizó; `False` en caso contrario.
        '''
        if isinstance(op, bool) or not isinstance(op, int):
            return False
        if nuevo_pokemon is None or not 0 <= op < len(self.__pokemon):
            return False
        self.__pc.append(self.__pokemon[op])
        self.__pokemon[op] = nuevo_pokemon
        return True

    def recuperar_del_pc(self, op: int) -> bool:
        '''Retira un Pokémon del PC y lo agrega al equipo si hay hueco (< 6).

        Args:
            op: Índice del Pokémon dentro del almacenamiento del PC.

        Returns:
            bool: `True` si pasó al equipo; `False` si el índice es inválido
                o el equipo activo ya está lleno.
        '''
        if isinstance(op, bool) or not isinstance(op, int):
            return False
        if not 0 <= op < len(self.__pc) or len(self.__pokemon) >= self.LIMITE:
            return False
        self.__pokemon.append(self.__pc.pop(op))
        return True

    def cambiar_activo(self, indice: int) -> bool:
        '''Coloca un Pokémon consciente en la primera posición del equipo (índice 0).

        Args:
            indice: Posición actual del Pokémon en el equipo activo.

        Returns:
            bool: `True` si se movió al frente; `False` si el índice no es
                válido o el Pokémon está debilitado.
        '''
        if isinstance(indice, bool) or not isinstance(indice, int):
            return False
        if not 0 <= indice < len(self.__pokemon):
            return False
        pokemon = self.__pokemon[indice]
        if pokemon.salud_actual <= 0:
            return False
        self.__pokemon.pop(indice)
        self.__pokemon.insert(0, pokemon)
        return True

    def almacenar_en_pc(self, pokemon) -> None:
        '''Guarda directamente un Pokémon en el PC (ej. al capturar con equipo lleno).

        Args:
            pokemon: Instancia de Pokémon a guardar en el PC.
        '''
        if pokemon is not None:
            self.__pc.append(pokemon)

    # --------------------------------------------------------
    # PERSISTENCIA (EXPORTAR / CARGAR)
    # --------------------------------------------------------

    def exportar_datos(self) -> dict:
        '''Serializa el equipo activo y el PC a un diccionario compatible con JSON.'''
        return {
            "pokemon": [pokemon.exportar_datos() for pokemon in self.__pokemon],
            "pc": [pokemon.exportar_datos() for pokemon in self.__pc],
        }

    @classmethod
    def cargar_datos(cls, datos: dict, cargador_pokemon=None) -> "Equipo":
        '''Reconstruye un `Equipo` desde un diccionario guardado.

        Args:
            datos: Diccionario con claves `'pokemon'` y `'pc'`.
            cargador_pokemon: Función/método opcional para reconstruir cada Pokémon.

        Returns:
            Equipo: Instancia reconstruida con equipo activo y PC.

        Raises:
            ValueError: Si la partida guardada no contiene Pokémon activos.
        '''
        datos = datos or {}
        cargador = cargador_pokemon or Pokemon.cargar_datos

        pokemon_equipo = [cargador(p) for p in datos.get("pokemon", [])]
        pokemon_pc = [cargador(p) for p in datos.get("pc", [])]

        if not pokemon_equipo:
            raise ValueError("La partida no contiene Pokémon activos.")

        return cls(pokemon=pokemon_equipo, pc=pokemon_pc)