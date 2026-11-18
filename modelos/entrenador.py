from modelos.equipo import Equipo
from modelos.mochila import Mochila

# == ENTRENADORES Y SERVICIOS DEL MUNDO POKéMON ==============
# Entrenador    | Representa al jugador con su nombre, equipo y mochila.
# EntrenadorNPC | Modela entrenadores rivales con equipo fijo y recompensa.
# ============================================================
class Entrenador:
    '''Representa al jugador principal de la aventura.

    Atributos:
        nombre (str): Nombre del entrenador (no vacío).
        equipo (Equipo): Instancia con su equipo activo y PC.
        mochila (Mochila): Instancia con su dinero e inventario de objetos.
    '''
    def __init__(self, nombre, equipo=None, mochila=None):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del entrenador no puede estar vacío.")
        self.nombre = nombre.strip()
        # Si no se reciben equipo o mochila previos, se crean instancias nuevas por defecto
        self.equipo = equipo or Equipo()
        self.mochila = mochila or Mochila()


class EntrenadorNPC:
    '''Representa un entrenador rival (cazabichos, líder de gimnasio, etc.).

    Atributos:
        nombre (str): Nombre y título del rival (ej. 'Líder Brock').
        equipo (tuple): Tupla inmutable con los Pokémon del rival.
        recompensa (int): Pokémonedas entregadas al jugador tras derrotarlo.
    '''
    def __init__(self, nombre, equipo, recompensa=500):
        self.nombre = nombre
        # Guardamos su equipo como tupla inmutable para no alterar su plantilla
        self.equipo = tuple(equipo)
        self.recompensa = recompensa
    
    @property
    def derrotado(self):
        '''Devuelve True si todos los Pokémon del entrenador rival tienen 0 PS.'''
        return all(pokemon.salud_actual <= 0 for pokemon in self.equipo)
