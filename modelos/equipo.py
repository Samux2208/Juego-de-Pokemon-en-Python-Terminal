from modelos.pokemon import Pokemon

# == GESTIÓN DE EQUIPO ACTIVO Y ALMACENAMIENTO PC ============
# Equipo | Administra los hasta 6 Pokémon activos del entrenador
#          y el almacenamiento ilimitado en el Sistema de Almacenamiento (PC).
# ============================================================
class Equipo:
    '''Equipo activo con límite de 6 Pokémon y almacenamiento PC sin límite.

    Atributos de clase:
        LIMITE (int): Capacidad máxima del equipo activo (6 Pokémon).
    '''
    LIMITE = 6

    def __init__(self, pokemon=None, pc=None):
        # Listas privadas para evitar modificaciones directas desde fuera de la clase
        self.__pokemon = list(pokemon or [])
        self.__pc = list(pc or [])

        # Validamos que el equipo inicial no exceda el límite permitido
        if len(self.__pokemon) > self.LIMITE:
            raise ValueError("El equipo no puede superar seis Pokémon.")

    # --- PROPIEDADES DE SOLO LECTURA ---
    @property
    def pokemon(self):
        '''Devuelve el equipo activo como tupla inmutable.'''
        return tuple(self.__pokemon)

    @property
    def pc(self):
        '''Devuelve los Pokémon almacenados en el PC como tupla inmutable.'''
        return tuple(self.__pc)

    @property
    def activo(self):
        '''Devuelve el primer Pokémon consciente del equipo (o None si todos cayeron).'''
        for poke in self.__pokemon:
            if poke.salud_actual > 0:
                return poke
        return None

    # --- GESTIÓN DEL EQUIPO Y TRANSFERENCIAS CON EL PC ---
    def agregar(self, pokemon):
        '''Añade un Pokémon al equipo si hay espacio (< 6); devuelve True/False.'''
        if len(self.__pokemon) >= self.LIMITE:
            return False
        self.__pokemon.append(pokemon)
        return True

    def enviar_al_pc(self, op):
        '''Transfiere un Pokémon del equipo al PC (impide dejar el equipo vacío).'''
        if not 0 <= op < len(self.__pokemon) or len(self.__pokemon) == 1:
            return False
        self.__pc.append(self.__pokemon.pop(op))
        return True

    def reemplazar(self, op, nuevo_pokemon):
        '''Sustituye un Pokémon del equipo por uno nuevo, enviando el anterior al PC.'''
        if not 0 <= op < len(self.__pokemon):
            return False
        self.__pc.append(self.__pokemon[op])
        self.__pokemon[op] = nuevo_pokemon
        return True

    def recuperar_del_pc(self, op):
        '''Saca un Pokémon del PC y lo añade al equipo si hay menos de 6.'''
        if not 0 <= op < len(self.__pc) or len(self.__pokemon) >= self.LIMITE:
            return False
        self.__pokemon.append(self.__pc.pop(op))
        return True

    def cambiar_activo(self, indice):
        '''Mueve un Pokémon consciente en la posición `indice` al primer lugar (índice 0).'''
        if not 0 <= indice < len(self.__pokemon):
            return False
        pokemon = self.__pokemon[indice]
        if pokemon.salud_actual <= 0:
            return False
        self.__pokemon.pop(indice)
        self.__pokemon.insert(0, pokemon)
        return True

    def almacenar_en_pc(self, pokemon):
        '''Guarda un Pokémon directamente en el PC (usado al capturar con equipo lleno).'''
        self.__pc.append(pokemon)

    # --- PERSISTENCIA (EXPORTAR / CARGAR) ---
    def exportar_datos(self):
        '''Convierte tanto el equipo activo como el PC a listas de diccionarios.'''
        return {
            "pokemon": [pokemon.exportar_datos() for pokemon in self.__pokemon],
            "pc": [pokemon.exportar_datos() for pokemon in self.__pc],
        }

    @classmethod
    def cargar_datos(cls, datos, cargador_pokemon=None):
        '''Reconstruye un Equipo activo y su PC desde un diccionario guardado.'''
        datos = datos or {}
        cargador = cargador_pokemon or Pokemon.cargar_datos

        pokemon_equipo = [
            cargador(p) for p in datos.get("pokemon", [])
        ]
        pokemon_pc = [
            cargador(p) for p in datos.get("pc", [])
        ]

        if not pokemon_equipo:
            raise ValueError("La partida no contiene Pokémon activos.")

        return cls(pokemon=pokemon_equipo, pc=pokemon_pc)