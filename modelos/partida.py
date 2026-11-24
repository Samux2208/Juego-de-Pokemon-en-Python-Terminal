'''Contenedor del estado de una partida en curso.'''
from dataclasses import dataclass
from modelos.equipo import Equipo
from modelos.mochila import Mochila


@dataclass
class Partida:
    '''Agrupa todo lo que se guarda y se carga de una partida.

    Atributos:
        nombre_entrenador (str): Nombre del jugador.
        equipo (Equipo): Pokémon del jugador.
        mochila (Mochila): Objetos y saldo en ₽.
    '''
    nombre_entrenador: str
    equipo: Equipo
    mochila: Mochila