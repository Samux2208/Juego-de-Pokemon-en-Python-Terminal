'''Servicios de ciudades y pueblos de Kanto para Pokémon Gen III.

Incluye `TiendaPokemon` (compra y venta al estilo Rojo Fuego / Verde Hoja)
y `CentroPokemon` (curación completa del equipo y acceso al PC de Bill).
'''

import time
from interfaz.mensajes import imprimir_con_retraso
from modelos.objeto import OBJETOS


class TiendaPokemon:
    '''Servicio comercial para comprar y vender objetos según reglas Gen III.'''

    @staticmethod
    def objetos_disponibles() -> list:
        '''Devuelve la lista de objetos del catálogo disponibles para comprar en tienda.'''
        return [
            objeto
            for objeto in OBJETOS.values()
            if getattr(objeto, "en_tienda", True)
        ]

    @staticmethod
    def comprar(mochila, identificador: str, cantidad: int = 1) -> bool:
        '''Procesa la compra de uno o más objetos descontando Pokédolares (₽).

        Args:
            mochila: Instancia de `Mochila` del jugador.
            identificador: Clave interna del objeto en `OBJETOS`.
            cantidad: Cantidad entera positiva de unidades a comprar.

        Returns:
            bool: `True` si la compra fue exitosa; `False` en caso contrario.
        '''
        objeto = OBJETOS.get(identificador)
        if (
            objeto is None
            or not getattr(objeto, "en_tienda", True)
            or isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            return False

        costo = objeto.precio * cantidad

        # Verifica y descuenta saldo antes de añadir los objetos a la mochila
        if not mochila.gastar(costo):
            imprimir_con_retraso("\n ❌ No tienes suficientes ₽\n")
            return False

        if not mochila.agregar(identificador, cantidad):
            # Reembolso de seguridad si la mochila rechazara el ingreso
            mochila.ganar(costo)
            return False

        imprimir_con_retraso(f"\n ✅ Compraste {objeto.nombre} x{cantidad} por {costo} ₽.\n")
        time.sleep(.5)
        return True

    @staticmethod
    def vender(mochila, identificador: str, cantidad: int = 1) -> bool:
        '''Vende unidades de un objeto de la mochila por la mitad de su precio (Gen III).

        Args:
            mochila: Instancia de `Mochila` del jugador.
            identificador: Clave interna del objeto en `OBJETOS`.
            cantidad: Cantidad entera positiva de unidades a vender.

        Returns:
            bool: `True` si la venta se completó; `False` en caso contrario.
        '''
        objeto = OBJETOS.get(identificador)
        if (
            objeto is None
            or objeto.precio <= 0
            or isinstance(cantidad, bool)
            or not isinstance(cantidad, int)
            or cantidad <= 0
        ):
            return False

        precio_venta_unidad = max(1, objeto.precio // 2)
        ganancia = precio_venta_unidad * cantidad

        if not mochila.quitar(identificador, cantidad):
            return False

        mochila.ganar(ganancia)
        imprimir_con_retraso(
            f"\n 💰 Vendiste {objeto.nombre} x{cantidad} y recibiste {ganancia} ₽.\n"
        )
        time.sleep(.5)
        return True


class CentroPokemon:
    '''Servicio médico gratuito para restaurar el equipo y acceder al PC.'''

    @staticmethod
    def curar(equipo) -> None:
        '''Restaura PS, PP y estados de todos los Pokémon del equipo activo.

        Args:
            equipo: Instancia de `Equipo` cuyos Pokémon activos serán curados.
        '''
        for poke in equipo.pokemon:
            poke.curar()
            poke.restaurar_pp_todos()
            poke.estado_alterado = None
            poke.turnos_estado = 0
            poke.resetear_combate()

        imprimir_con_retraso("\n 🏥 Enfermera Joy: ¡Hola! Bienvenido al Centro Pokémon.")
        imprimir_con_retraso("\n 🩺 Permíteme cuidar a tus Pokémon unos segundos...")
        imprimir_con_retraso("\n 🎶 Pam, pam, pa-ra-ram... ✨")
        imprimir_con_retraso(
            "\n 💖 Enfermera Joy: ¡Gracias por esperar! Tus Pokémon están en plena forma."
        )
        imprimir_con_retraso("\n 👋 ¡Esperamos volver a verte pronto!\n")
        time.sleep(1)

    @staticmethod
    def conectar_pc() -> None:
        '''Muestra el mensaje de conexión al Sistema de Almacenamiento de Bill.'''
        imprimir_con_retraso("\n 💻 Te acercas al terminal del Centro Pokémon...")
        imprimir_con_retraso("\n 🔌 ¡Conectado al Sistema de Almacenamiento de Bill!\n")
        time.sleep(.5)