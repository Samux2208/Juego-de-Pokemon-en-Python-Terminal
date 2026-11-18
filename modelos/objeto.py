from interfaz.mensajes import imprimir_con_retraso
from config import EVOLUCIONES_OBJETO
from sistemas.evolucion import evolucionar_pokemon

# == OBJETOS Y CATÁLOGO DE TIENDA ============================
# Objeto           | Clase base inmutable para cualquier ítem de mochila.
# Pokeball         | Subclase con multiplicador de captura (bonus).
# Pocion           | Subclase curativa con método usar(pokemon).
# PiedraEvolutiva  | Subclase que activa evoluciones mediante EVOLUCIONES_OBJETO.
# OBJETOS          | Catálogo maestro de ítems disponibles en el juego.
# ============================================================

class Objeto:
    '''Definición base e inmutable de un objeto de mochila.

    Atributos:
        identificador (str): Clave interna única del objeto (ej. 'pokeball').
        nombre (str): Nombre visible en tienda y mochila (ej. 'Poké Ball').
        precio (int): Costo de compra en Pokédolares (₽).
    '''

    def __init__(self, identificador, nombre, precio):
        # Atributos protegidos para evitar modificaciones accidentales en partida
        self._identificador = identificador
        self._nombre = nombre
        self._precio = precio

    # --- PROPIEDADES DE SOLO LECTURA ---
    @property
    def identificador(self):
        return self._identificador

    @property
    def nombre(self):
        return self._nombre

    @property
    def precio(self):
        return self._precio


class Pokeball(Objeto):
    '''Objeto utilizado para capturar Pokémon salvajes en combate.

    Atributos:
        bonus (float): Multiplicador aplicado al ratio de captura (ej. 1.0, 1.5).
    '''
    def __init__(self, identificador, nombre, precio, bonus):
        # Heredamos identificador, nombre y precio de la clase base Objeto
        super().__init__(identificador, nombre, precio)
        self.bonus = bonus


class Pocion(Objeto):
    '''Objeto curativo que restaura PS a un Pokémon consciente.

    Atributos:
        curacion (int): Cantidad máxima de PS que restaura.
    '''
    def __init__(self, identificador, nombre, precio, curacion):
        # Heredamos los atributos base y añadimos la capacidad de curación
        super().__init__(identificador, nombre, precio)
        self.curacion = curacion


    def usar(self, pokemon):
        '''Cura al Pokémon si está herido y consciente; devuelve los PS restaurados.'''
        # Validamos si el Pokémon está debilitado (una poción normal no lo revive)
        if pokemon.salud_actual <= 0:
            imprimir_con_retraso(f" ¡{pokemon.nombre_visible} está debilitado y no puede usar una poción!")
            return 0

        # Validamos si el Pokémon ya tiene su salud al máximo
        if pokemon.salud_actual >= pokemon.salud_maxima:
            imprimir_con_retraso(f" ¡La vida de {pokemon.nombre_visible} ya está al máximo! No se puede curar.")
            return 0
        return pokemon.curar(self.curacion)


class PiedraEvolutiva(Objeto):
    '''Objeto especial que desencadena la evolución de especies compatibles.'''
    def usar(self, pokemon):
        '''Intenta evolucionar al Pokémon usando esta piedra.
        
        Devuelve True si evolucionó (para consumir el objeto) o False si es incompatible.
        '''
        # Buscamos en EVOLUCIONES_OBJETO el diccionario de especies para esta piedra
        evoluciones_compatibles = EVOLUCIONES_OBJETO.get(self.nombre, {})

        # Verificamos si la especie actual del Pokémon aparece como clave
        nueva_especie = evoluciones_compatibles.get(pokemon.especie)
        if not nueva_especie:
            return False

        # Ejecutamos la evolución y confirmamos el uso exitoso
        evolucionar_pokemon(pokemon, nueva_especie)
        return True

# ============================================================
# CATÁLOGO MAESTRO DE OBJETOS (PRECIOS OFICIALES ROJO FUEGO)
# Formato -> clave_interna: Instancia de subclase de Objeto
# ============================================================
OBJETOS = {
    # Poké Balls (Captura)
    "pokeball": Pokeball("pokeball", "Poké Ball", 200, 1.0),
    "superball": Pokeball("superball", "Super Ball", 600, 1.5),

    # Medicinas (Curación de PS)
    "pocion": Pocion("pocion", "Poción", 300, 20),
    "superpocion": Pocion("superpocion", "Superpoción", 700, 50),

    # Piedras Evolutivas
    "piedra_fuego": PiedraEvolutiva("piedra_fuego", "Piedra Fuego", 2100),
    "piedra_agua": PiedraEvolutiva("piedra_agua", "Piedra Agua", 2100),
    "piedra_trueno": PiedraEvolutiva("piedra_trueno", "Piedra Trueno", 2100),
    "piedra_hoja": PiedraEvolutiva("piedra_hoja", "Piedra Hoja", 2100),
    "piedra_lunar": PiedraEvolutiva("piedra_lunar", "Piedra Lunar", 2100),
}