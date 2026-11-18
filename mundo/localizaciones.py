import time
from modelos.objeto import OBJETOS
from interfaz.mensajes import imprimir_con_retraso

class TiendaPokemon:
    '''Servicio comercial para adquirir objetos del catálogo oficial.'''

    @staticmethod
    def comprar(mochila, identificador, cantidad=1):
        '''Procesa la compra de uno o más objetos descontando pokémonedas.
        
        Devuelve True si la compra fue exitosa o False si no hubo saldo o datos válidos.
        '''
        objeto = OBJETOS.get(identificador)
        if not objeto or not isinstance(cantidad, int) or cantidad <= 0:
            return False
        
        costo = objeto.precio * cantidad

        # Intenta descontar; si no alcanza el saldo, devuelve False
        if not mochila.gastar(costo):
            imprimir_con_retraso("\n ❌ No tienes suficientes ₽\n")
            return False

        mochila.agregar(identificador, cantidad)
        imprimir_con_retraso(f"\n✅ Compraste {objeto.nombre} x{cantidad}.\n")
        time.sleep(.5)
        return True


class CentroPokemon:
    '''Servicio médico gratuito para restaurar el estado del equipo.'''

    @staticmethod
    def curar(equipo):
        '''Restaura al máximo los PS de todos los Pokémon del equipo activo.'''
        for pokemon in equipo.pokemon:
            pokemon.curar()
            pokemon.estado_alterado = None
        imprimir_con_retraso("\n🏥 Enfermera Joy: ¡Hola! Bienvenido al Centro Pokémon.")
        imprimir_con_retraso("\n🩺 Permíteme cuidar a tus Pokémon unos segundos...")
        imprimir_con_retraso("\n🎶 Pam, pam, pa-ra-ram... ✨")
        imprimir_con_retraso(f"\n💖 Enfermera Joy: ¡Gracias por esperar! Tus Pokémon están en plena forma.")
        imprimir_con_retraso("\n👋 ¡Esperamos volver a verte pronto!\n")
        time.sleep(1)

    @staticmethod
    def conectar_pc():
        imprimir_con_retraso("\n 💻 Te acercas al terminal del Centro Pokémon...")
        imprimir_con_retraso("\n 🔌 ¡Conectado al Sistema de Almacenamiento de Bill!\n")
        time.sleep(.5)