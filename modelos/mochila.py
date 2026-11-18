from config import DINERO_INICIAL
from modelos.objeto import OBJETOS

# == GESTIÓN DE INVENTARIO Y ECONOMÍA ========================
# Mochila | Administra el dinero (pokemonedas) y el conteo de ítems
#           del jugador mediante encapsulamiento estricto.
# ============================================================
class Mochila:
    '''Inventario del entrenador por identificador y conteo de unidades.

    Atributos:
        dinero (int): Saldo actual disponible (propiedad de solo lectura; se modifica con ganar() y gastar())).
    '''
    def __init__(self, objetos=None, dinero=DINERO_INICIAL):
        # Diccionario privado: {identificador_objeto: cantidad_entera}
        self.__objetos = {}
        # Validamos el saldo inicial una única vez en el constructor
        if not isinstance(dinero, int) or isinstance(dinero, bool) or dinero < 0:
            raise ValueError("Las pokémonedas iniciales deben ser un entero no negativo.")
        # Inicializamos el saldo privado ya validado
        self.__dinero = dinero

        # Validamos y cargamos los objetos iniciales (si se pasaron al constructor)
        for identificador, cantidad in (objetos or {}).items():
            if identificador not in OBJETOS or not isinstance(cantidad, int) or cantidad < 0:
                raise ValueError(f"Contenido de mochila inválido: {identificador}")
            # Solo guardamos ítems cuya cantidad sea mayor a 0
            if cantidad:
                self.__objetos[identificador] = cantidad

    # --- PROPIEDAD DE ECONOMÍA (SOLO LECTURA) ---
    @property
    def dinero(self):
        return self.__dinero

    # --- MéTODOS SEGUROS DE ECONOMÍA ---
    def ganar(self, cantidad):
        '''Suma pokémonedas al saldo actual (valida que sea un entero positivo).'''
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("La cantidad a ganar debe ser un entero no negativo.")
        self.__dinero += cantidad

    def gastar(self, cantidad):
        '''Descuenta pokémonedas si hay saldo suficiente; devuelve True/False.'''
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("La cantidad a gastar debe ser un entero no negativo.")
        if self.__dinero < cantidad:
            return False
        self.__dinero -= cantidad
        return True
    
    # --- MéTODOS DE GESTIÓN DE ÍTEMS ---
    def cantidad(self, identificador):
        '''Devuelve cuántas unidades posee el jugador de un objeto (0 si no tiene).'''
        return self.__objetos.get(identificador, 0)

    def agregar(self, identificador, cantidad=1):
        '''Añade unidades de un objeto válido; devuelve True si tuvo éxito o False si falló.'''
        if (
            identificador not in OBJETOS
            or isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            return False
        self.__objetos[identificador] = self.cantidad(identificador) + cantidad
        return True

    def quitar(self, identificador, cantidad=1):
        '''Descuenta unidades de un objeto; devuelve True si hubo stock o False si faltó.'''
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
            or self.cantidad(identificador) < cantidad
        ):
            return False
        
        restante = self.cantidad(identificador) - cantidad
        if restante:
            self.__objetos[identificador] = restante
        else:
            # Si llega a 0 unidades, eliminamos la clave para mantener limpia la mochila
            self.__objetos.pop(identificador)
        return True

    def listar(self):
        '''Devuelve una lista de tuplas (objeto_instancia, cantidad) para mostrar en menú.'''
        return [
            (OBJETOS[identificador], cantidad)
            for identificador, cantidad in self.__objetos.items()
        ]

    # --- PERSISTENCIA (EXPORTAR / CARGAR) ---
    def exportar_datos(self):
        '''Convierte el inventario y el saldo en un diccionario de tipos primitivos.'''
        return {
            "objetos": dict(self.__objetos),
            "dinero": self.dinero,
        }

    @classmethod
    def cargar_datos(cls, datos):
        '''Reconstruye una instancia de Mochila a partir de un diccionario guardado.'''
        datos = datos or {}
        return cls(
            objetos=datos.get("objetos", {}),
            dinero=datos.get("dinero", DINERO_INICIAL),
        )