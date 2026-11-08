import time
import random
import sys
import pickle

# ============================================================
# BASE DE DATOS DE ESPECIES
# Las estadísticas corresponden a las estadísticas base de cada especie.
# Los tipos se guardan en minúscula para mantener compatibilidad
# con el método ventaja() de la clase Pokemon.
# ============================================================

DICCIONARIO_POKEMON = {

    # ==================== TIPO FUEGO ====================
    "Charmander": {
        "tipo": "fuego",
        "movimientos": ["Arañazo", "Gruñido", "Ascuas", "Giro Fuego"],
        "EVs": {"vida": 39, "ataque": 52, "defensa": 43},
        "disponibilidad": "Inicial; solo se elige una linea inicial por partida."
    },
    "Charmeleon": {
        "tipo": "fuego",
        "movimientos": ["Arañazo", "Gruñido", "Ascuas", "Lanzallamas"],
        "EVs": {"vida": 58, "ataque": 64, "defensa": 58},
        "disponibilidad": "Evoluciona de Charmander."
    },
    "Charizard": {
        "tipo": "fuego",
        "movimientos": ["Ascuas", "Giro Fuego", "Mov. Sísmico", "Lanzallamas"],
        "EVs": {"vida": 78, "ataque": 84, "defensa": 78},
        "disponibilidad": "Evoluciona de Charmeleon al Nivel 36."
    },
    "Growlithe": {
        "tipo": "fuego",
        "movimientos": ["Mordisco", "Ascuas", "Rugido", "Lanzallamas"],
        "EVs": {"vida": 55, "ataque": 70, "defensa": 45},
        "disponibilidad": "Disponible en Rojo Fuego."
    },
    "Arcanine": {
        "tipo": "fuego",
        "movimientos": ["Mordisco", "Ascuas", "Velocidad Extrema", "Lanzallamas"],
        "EVs": {"vida": 90, "ataque": 110, "defensa": 80},
        "disponibilidad": "Evoluciona de Growlithe mediante Piedra Fuego."
    },

    # ==================== TIPO AGUA ====================
    "Squirtle": {
        "tipo": "agua",
        "movimientos": ["Placaje", "Látigo", "Pistola Agua", "Mordisco"],
        "EVs": {"vida": 44, "ataque": 48, "defensa": 65},
        "disponibilidad": "Inicial; solo se elige una linea inicial por partida."
    },
    "Wartortle": {
        "tipo": "agua",
        "movimientos": ["Placaje", "Pistola Agua", "Mordisco", "Hidrobomba"],
        "EVs": {"vida": 59, "ataque": 63, "defensa": 80},
        "disponibilidad": "Evoluciona de Squirtle."
    },
    "Blastoise": {
        "tipo": "agua",
        "movimientos": ["Mordisco", "Pistola Agua", "Surf", "Hidrobomba"],
        "EVs": {"vida": 79, "ataque": 83, "defensa": 100},
        "disponibilidad": "Evoluciona de Wartortle."
    },
    "Psyduck": {
        "tipo": "agua",
        "movimientos": ["Pistola Agua", "Confusión", "Golpes Furia", "Hidrobomba"],
        "EVs": {"vida": 50, "ataque": 52, "defensa": 48},
        "disponibilidad": "Disponible en Rojo Fuego."
    },

    # ==================== TIPO PLANTA ====================
    "Bulbasaur": {
        "tipo": "planta",
        "movimientos": ["Látigo Cepa", "Placaje", "Drenadoras", "Hoja Afilada"],
        "EVs": {"vida": 45, "ataque": 49, "defensa": 49},
        "disponibilidad": "Inicial; solo se elige una linea inicial por partida."
    },
    "Ivysaur": {
        "tipo": "planta",
        "movimientos": ["Látigo Cepa", "Drenadoras", "Polvo Veneno", "Hoja Afilada"],
        "EVs": {"vida": 60, "ataque": 62, "defensa": 63},
        "disponibilidad": "Evoluciona de Bulbasaur al Nivel 16."
    },
    "Venusaur": {
        "tipo": "planta",
        "movimientos": ["Drenadoras", "Hoja Afilada", "Gigadrenado", "Rayo Solar"],
        "EVs": {"vida": 80, "ataque": 82, "defensa": 83},
        "disponibilidad": "Evoluciona de Ivysaur al Nivel 36."
    },
    "Oddish": {
        "tipo": "planta",
        "movimientos": ["Absorber", "Drenadoras", "Ácido", "Hoja Afilada"],
        "EVs": {"vida": 45, "ataque": 50, "defensa": 55},
        "disponibilidad": "Disponible en rutas con praderas silvestres."
    }
}

# ============================================================
# FUNCIONES DE UTILIDAD Y RETRASO DE TEXTO
# ===========================================================

def imprimir_con_retraso(s):
    # Imprime una letra a la vez
    for letra in s:
        sys.stdout.write(letra)
        sys.stdout.flush()
        time.sleep(0.05)  # Retraso de 0.05 segundos entre letras

# ============================================================
# CLASE PRINCIPAL POKÉMON
# ============================================================

class Pokemon:
    def __init__(self, nombre, tipo, movimientos, EVs, nivel=1):

        # PROTEGIDOS: Accesibles en herencia, protegidos del exterior
        self._nombre = nombre
        self._tipo = tipo

        # PÚBLICOS: Flujo constante de lectura/escritura
        self.movimientos = movimientos
        self.nivel = nivel
        # Fórmula cúbica clásica: la experiencia acumulada inicial depende del nivel
        self.exp_actual = int((self.nivel ** 3) * 0.8)
        

        # PRIVADOS: Nadie desde fuera los puede tocar directament
        # Aplicar fórmulas de nivel oficiales (Ataque y Defensa) como enteros
        self.__ataque = int(((EVs["ataque"] * 2 * self.nivel) / 100) + 5)
        self.__defensa = int(((EVs["defensa"] * 2 * self.nivel) / 100) + 5)

        # Experiencia requerida para el PRÓXIMO nivel
        self.__exp_siguiente_nivel = int(((self.nivel + 1) ** 3) * 0.8)

        # Definimos la salud máxima del Pokémon usando la fórmula oficial de los juegos
        self.__salud_maxima = int(((EVs.get("vida", 50) * 2 * self.nivel) / 100) + self.nivel + 10)

        # PÚBLICO: Cambia en cada turno del combate
        # Definimos la salud actual del Pokémon, que comienza al máximo
        self.salud_actual = self.__salud_maxima  # Inicia completamente sano

    # MÉTODOS GETTER (Propiedades públicas para LEER los datos privados de forma segura)
    @property
    def barra_de_vida(self):
        """
        Propiedad dinámica: Calcula cuántas barras "=" mostrar 
        según la salud actual del Pokémon en el combate.
        """
        total_barras = 20 # El tamaño fijo de tu barra visual
        
        # Evitamos división por cero si el Pokémon se debilita
        if self.__salud_maxima == 0:
            return ""
            
        # Calculamos cuántas barras le quedan proporcionalmente
        barras_actuales = int((self.salud_actual / self.__salud_maxima) * total_barras)

        # Asegura que si le queda al menos 1 de vida, muestre una barra y no se vea vacío antes de tiempo
        if self.salud_actual > 0 and barras_actuales == 0:
            barras_actuales = 1  
        return "=" * barras_actuales
    
    @property
    def ataque(self):
        return self.__ataque

    @property
    def defensa(self):
        return self.__defensa

    @property
    def salud_maxima(self):
        return self.__salud_maxima

    @property
    def exp_siguiente_nivel(self):
        return self.__exp_siguiente_nivel

    # Muestra la información del Pokémon
    def info_pokemon(self):
        '''Muestra la ficha técnica paginada del Pokémon.
        '''

        # Buscamos el texto de disponibilidad. Si no existe, dejamos un valor por defecto.
        datos_especie = DICCIONARIO_POKEMON.get(self._nombre, {})
        notas_entrenador = datos_especie.get("disponibilidad", "Conseguido en tu aventura.")

        pagina_actual = 1

        while True:
            # ============================================================
            # CÁLCULOS MATEMÁTICOS GLOBALES (Para ambas páginas)
            # ============================================================
            # Calculamos cuánta EXP real requiere este nivel específico y cuánta lleva progresada
            exp_base_nivel_actual = int((self.nivel ** 3) * 0.8)
            exp_necesaria = self.exp_siguiente_nivel - exp_base_nivel_actual
            exp_progresada = self.exp_actual - exp_base_nivel_actual

            if exp_necesaria <= 0:
                exp_necesaria = 1

            # Calculamos cuántas barritas "#" corresponden (ancho de 10 espacios fijos)
            proporcion_exp = max(0, exp_progresada) / exp_necesaria
            barras_exp = int(proporcion_exp * 10)

            # CONTROL ESTÉTICO: Si ya ganó EXP en este nivel pero el redondeo da 0, pintamos 1 barrita
            if exp_progresada > 0 and barras_exp == 0:
                barras_exp = 1
            barra_visual_exp = "#" * min(10, max(0, barras_exp))

            print("\n" + "=" * 50)
            if pagina_actual == 1:
                # ==================== PÁGINA 1: ESTADÍSTICAS BÁSICAS ====================
                print("=" * 50)
                print(f" INFO. POKéMON\t\t\tPÁGINA [1/2]")
                print("=" * 50)
                print(f" NOMBRE:   {self._nombre:<20} NIVEL:    {self.nivel}")
                print(f" TIPO:     {self._tipo:<20}")
                print("-" * 50)
                print(" NOTAS DE LA POKÉDEX 📝")
                print(f" {notas_entrenador}")
                print("=" * 50)
                print("\n [ENTER] Ver Habilidades  |  [X] Volver al Menú")

            else:
                # ==================== PÁGINA 2: LISTA DE MOVIMIENTOS ====================
                print(f" HABIL. POKéMON\t\t\tPÁGINA [2/2]")
                print("=" * 50)
                print(f" NIVEL:  {self.nivel:<10} PS:   {self.salud_actual}/{self.salud_maxima}")
                print(f"                      PS:  [{self.barra_de_vida:<10}]")
                print(f" ATAQUE:   {self.ataque:<10} DEFENSA: {self.defensa}")
                print("-" * 50)
                print(f" EXPERIENCIA. ✨")
                print(f" PUNTOS EXP: {self.exp_actual:<10} SIG. NIVEL: {self.__exp_siguiente_nivel}")
                print(f"          EXP: [{barra_visual_exp:<10}]")
                print("=" * 50)
                print("\n [ENTER] Ver Datos Básicos  |  [X] Volver al Menú")

            # Captura la entrada del jugador
            accion = input("\n Selecciona una opción: ").strip().lower()
            if accion == 'x':
                break  # Sale del bucle de la ficha y regresa al menú de tu partida
                # Si presiona ENTER (o cualquier otra tecla que no sea X), alterna la página
            pagina_actual = 2 if pagina_actual == 1 else 1

    def comprobar_subida_nivel(self):
        """Verifica si el Pokémon sube de nivel y recalcula estadísticas.."""
        subio_nivel = False
        
        # Comprobar si tiene suficiente experiencia.
        # El while permite subir varios niveles si gana mucha experiencia.
        while self.exp_actual >= self.__exp_siguiente_nivel:
            self.nivel += 1
            subio_nivel = True
            
            # Recalculamos la EXP necesaria para el siguiente umbral
            self.__exp_siguiente_nivel = int(((self.nivel + 1) ** 3) * 0.8)
            
            imprimir_con_retraso(f"\n ¡Felicidades! ¡{self._nombre} subió al Nivel {self.nivel}! 🎉\n")
            time.sleep(2)
            
        # Si subió de nivel, actualizamos los atributos privados de estadísticas en caliente
        if subio_nivel:
            # Consultar las estadísticas base de la especie.
            datos_base = DICCIONARIO_POKEMON[self._nombre]["EVs"]

            # Guardamos la salud máxima anterior.
            salud_anterior = self.__salud_maxima
            
            # Actualizamos las estadísticas privadas.
            self.__ataque = int(((datos_base["ataque"] * 2 * self.nivel) / 100) + 5)
            self.__defensa = int(((datos_base["defensa"] * 2 * self.nivel) / 100) + 5)
            self.__salud_maxima = int(((datos_base.get("vida", 50) * 2 * self.nivel) / 100) + self.nivel + 10)
            
            # Aumentar la salud actual según el aumento de salud máxima.
            self.salud_actual += (self.__salud_maxima - salud_anterior)
            imprimir_con_retraso(" ¡Las estadísticas de tu Pokémon han aumentado!\n")

    def ventaja(self, Pokemon2):
        '''Considerar la ventaja de tipo
        Actualiza poderes de ataque y defensa
        Devuelve dos cadenas de informacion
        '''
        tipos = ["fuego", "planta", "agua"] # Fuego > Planta > Agua > Fuego

        # Inicializamos los multiplicadores por defecto (daño neutro = 1.0)
        mult_1, mult_2 = 1.0, 1.0  # El daño que hace tu Pokémon (self) y el rival (Pokemon2)

        # Inicializamos las cadenas por si no entran a ningún caso (aunque siempre entrarán)
        cadena_1 = " Es un golpe neutro.\n"
        cadena_2 = " Es un golpe neutro.\n"

        # Caso especial: Si ambos Pokémon son del mismo tipo
        if self._tipo == Pokemon2._tipo:
            return " No es muy efectivo...\n", " No es muy efectivo...\n", 0.5, 0.5

        # Validación perimetral: ambos deben estar en el triángulo
        if self._tipo in tipos and Pokemon2._tipo in tipos:
            tipo_1 = tipos.index(self._tipo)
            tipo_2 = tipos.index(Pokemon2._tipo) 

            # Triángulo: Fuego (> Planta) > Planta (> Agua) > Agua (> Fuego)
            if tipo_2 == (tipo_1 + 1) % 3:
                mult_1 = 2.0
                cadena_1 = " ¡Es muy eficaz!\n"
            elif tipo_1 == (tipo_2 + 1) % 3:
                mult_1 = 0.5
                cadena_1 = " No es muy efectivo...\n"

            if tipo_1 == (tipo_2 + 1) % 3:
                mult_2 = 2.0
                cadena_2 = " ¡Es muy eficaz!\n"
            elif tipo_2 == (tipo_1 + 1) % 3:
                mult_2 = 0.5
                cadena_2 = " No es muy efectivo...\n"
                
        # Retornamos las 4 cosas juntas al final del método (fuera del bucle for)
        return cadena_1, cadena_2, mult_1, mult_2
        
    def turno(self, Pokemon2, cadena_1, cadena_2, mult_1, mult_2):
        '''Empieza con Pokemon1, elige ataque y calcula el daño real.
        Luego automatiza el ataque aleatorio de Pokemon2.
        El bucle continúa hasta que la salud_actual de alguno llegue a 0.
        '''
        while (self.salud_actual > 0 and Pokemon2.salud_actual > 0):
            
            # Imprimir las barra_de_vida de cada Pokemon            
            print("\n" + "~" * 45)
            print(f" {self._nombre:<15} PS [{self.barra_de_vida:<20}] ({self.salud_actual}/{self.salud_maxima})")
            print(f" {Pokemon2._nombre:<15} PS [{Pokemon2.barra_de_vida:<20}] ({Pokemon2.salud_actual}/{Pokemon2.salud_maxima})")
            print("~" * 45)
            time.sleep(.5)

            # ==================== TURNO POKÉMON 1 (JUGADOR) ====================
            print(f"\n ¡Adelante {self._nombre}!")
            for i, x in enumerate(self.movimientos):
                print(f" {i+1}.", x)
            
            while True:
                try:
                    index = int(input("\n Elige un movimiento: "))
                    if 1 <= index <= len(self.movimientos):
                        break
                    print(" Movimiento nfuera de rango. Selecciona uno de la lista.")
                except ValueError:
                    print(" Introduce un número válido.")

            imprimir_con_retraso(f"\n {self._nombre} usó {self.movimientos[index - 1]}!")
            time.sleep(1)
            imprimir_con_retraso(cadena_1)

            # Determuinar el daño REAL multiplicando el ataque por la ventaja
            danio_p1 = int(self.ataque * mult_1)
            # Calcular salud actual del Pokemon mediante el daño hecho y validar como min 0
            Pokemon2.salud_actual = max(0, Pokemon2.salud_actual - danio_p1)

            # Estado de vida de los ddos pokemones tras el ataque
            time.sleep(1)
            print("\n" + "~" * 45)
            # Imprimir los barra_de_vida de cada Pokemon
            print(f" {self._nombre:<15} PS [{self.barra_de_vida:<20}] ({self.salud_actual}/{self.salud_maxima})")
            print(f" {Pokemon2._nombre:<15} PS [{Pokemon2.barra_de_vida:<20}] ({Pokemon2.salud_actual}/{Pokemon2.salud_maxima})")
            print("~" * 45)
            time.sleep(.5)
            
            # Comprueba si Pokémon se debilitó
            if Pokemon2.salud_actual <= 0:
                imprimir_con_retraso(f"\n ... {Pokemon2._nombre} se debilitó!")
                break
            
            # ==================== TURNO POKÉMON 2 (RIVAL IA) ====================
            index_aleatorio = random.randint(0, len(Pokemon2.movimientos) -1)
            imprimir_con_retraso(f"\n ¡El {Pokemon2._nombre} rival ataca!")
            imprimir_con_retraso(f"\n ¡{Pokemon2._nombre} usó {Pokemon2.movimientos[index_aleatorio]}!")
            time.sleep(.8)
            imprimir_con_retraso(cadena_2)
            
            # Determuinar el daño REAL multiplicando el ataque por la ventaja
            danio_p2 = int(Pokemon2.ataque * mult_2)
            # Calcular salud actual del Pokemon mediante el daño hecho y validar como min 0
            self.salud_actual = max(0, self.salud_actual - danio_p2)
            
            # Comprueba si Pokémon se debilitó
            if self.salud_actual <= 0:
                imprimir_con_retraso(f"\n ... {self._nombre} se debilitó!\n")
                break

    def lucha(self, Pokemon2):
        '''Gestiona el flujo completo del combate y recompensas.
        '''
        # Considerar la ventaja de tipo
        cadena_1, cadena_2, mult_1, mult_2 = self.ventaja(Pokemon2)

        # Ahora la lucha real ...
        # Continúa mientras ambos Pokémon tengan barras de vida
        self.turno(Pokemon2, cadena_1, cadena_2, mult_1, mult_2)

        # Evaluar si tu Pokémon quedó en pie al terminar el combate
        if self.salud_actual > 0:
            moneda = random.randint(150, 1200)
            imprimir_con_retraso(f"\n ¡Has ganado el combate! Obtuviste ${moneda} ₽.\n")
            
            # FÓRMULA DE EXPERIENCIA: Basada en el nivel del rival y un modificador por especie
            # Tomamos el ataque base del rival como factor de dificultad de la especie
            base_rival = DICCIONARIO_POKEMON[Pokemon2._nombre]["EVs"]["ataque"]
            exp_ganada = int((base_rival * Pokemon2.nivel) // 6)
            
            imprimir_con_retraso(f" ¡{self._nombre} ganó {exp_ganada} puntos de EXP! ✨\n")
            
            # Sumamos la experiencia obtenida al acumulador público
            self.exp_actual += exp_ganada
            
            # Invocamos el método que comprueba si alcanza para subir de nivel
            self.comprobar_subida_nivel()

# ============================================================
# PERSISTENCIA (GUARDAR Y CARGAR PARTIDA)
# ============================================================

def guardar_partida(nombre_entrenador, mi_pokemon):
    """Guarda el entrenador y su Pokémon en un archivo binario."""
    datos_partida = { "nombre_entrenador": nombre_entrenador, "pokemon": mi_pokemon}

    try:
        with open("partida_pokemon.dat", "wb") as archivo:
            pickle.dump(datos_partida, archivo)

        print("\n💾 ¡Partida guardada correctamente!")
    except (OSError, pickle.PickleError) as error:
        print(f"❌ No se pudo guardar la partida: {error}")


def cargar_partida():
    """Carga la partida guardada. Devuelve None si no existe."""
    try:
        with open("partida_pokemon.dat", "rb") as archivo:
            datos_partida = pickle.load(archivo)
        print(f"\n ¡Bienvenido de nuevo, {datos_partida['nombre_entrenador']}!")
        return datos_partida
    except FileNotFoundError:
        return None

# ============================================================
# EXPLORACIÓN DE RUTAS
# ============================================================

def explorar_ruta(numero_ruta):
    """Genera un Pokémon salvaje aleatorio según la ruta seleccionada.
    """
    match numero_ruta:
        case 1:
            imprimir_con_retraso("\n🚶 Caminando en la hierba baja de la Ruta 1...\n")
            especie = random.choice(["Charmander", "Squirtle", "Bulbasaur"])  # Usamos formas base existentes
            nivel = random.randint(2, 5)
        case 2:
            imprimir_con_retraso("\n🌲 Adentrándote en los senderos de la Ruta 2...\n")
            especie = random.choice(["Oddish", "Psyduck"])
            nivel = random.randint(5, 9)
        case 3:
            imprimir_con_retraso("\n🔥 Subiendo por el Monte ardiente en la Ruta 3...\n")
            especie = random.choice(["Charmeleon", "Growlithe", "Ivysaur"])
            nivel = random.randint(10, 16)
        case 4:
            imprimir_con_retraso("\n🌊 Cruzando las corrientes profundas de la Ruta 4...\n")
            especie = random.choice(["Charmeleon", "Wartortle"])
            nivel = random.randint(15, 22)
        case 5:
            imprimir_con_retraso("\n⚡ ¡Llegando a la Meseta Épica de los Pokémon!\n")
            especie = random.choice(["Charizard", "Blastoise", "Venusaur", "Arcanine"])
            nivel = random.randint(25, 35)
        case _:
            return None

    # Abrimos la raíz de la especie seleccionada
    datos = DICCIONARIO_POKEMON[especie]
    
    # Abrimos la caja interna de estadísticas que creaste en tu base de datos
    evs = datos["EVs"]

    # Devolvemos el pokemon rival de forma segura y aislada
    return Pokemon(especie, datos["tipo"], datos["movimientos"].copy(), evs, nivel)

# ============================================================
# INICIO DE PARTIDA NUEVA
# ============================================================

def nueva_partida():
    """Solicita el nombre y permite elegir el Pokémon inicial.
    """
    print("\n" + "=" * 45)
    print("          NUEVA PARTIDA POKÉMON")
    print("=" * 45)

    nombre_entrenador = input("\n ¿Cuál es tu nombre, joven entrenador?: ").strip()
    while not nombre_entrenador:
        nombre_entrenador = input(" El nombre no puede estar vacío. Inténtalo de nuevo: ").strip()

    print("\nEl profesor te ofrece elegir a tu compañero inicial:")
    print("[1] Charmander  (Tipo fuego)")
    print("[2] Squirtle   (Tipo agua)")
    print("[3] Bulbasaur   (Tipo planta)")

    iniciales = {1: "Charmander", 2: "Squirtle", 3: "Bulbasaur"}

    while True:
        try:
            opcion = int(input("\n Elige tu inicial (1-3): "))
            if opcion in iniciales:
                break
            print(" Opción no válida. Elige 1, 2 o 3.")
        except ValueError:
            print(" Debes introducir un número entero.")

    especie = iniciales[opcion]
    datos = DICCIONARIO_POKEMON[especie]

    mi_pokemon = Pokemon(especie, datos["tipo"], datos["movimientos"].copy(), datos["EVs"], 5)

    print(f"\n¡Felicidades, {nombre_entrenador}!")
    print(f"¡{especie} será tu compañero de aventuras!")

    # Guardado inmediato para evitar perder el inicio de la partida.
    guardar_partida(nombre_entrenador, mi_pokemon)

    return nombre_entrenador, mi_pokemon

# ============================================================
# BUCLE PRINCIPAL DEL JUEGO
# ============================================================

if __name__ == "__main__":

    print("=" * 45)
    print("       ¡BIENVENIDO AL MUNDO POKÉMON!")
    print("=" * 45)
    print("\n[1] Continuar Partida")
    print("[2] Nueva Partida")

    while True:
        try:
            opcion_inicio = int(input("\n Selecciona una opción: "))
            if opcion_inicio in (1, 2):
                break
            print(" Por favor, selecciona 1 o 2.")
        except ValueError:
            print(" Introduce un número válido.")

    nombre_entrenador, mi_pokemon = "", None

    if opcion_inicio == 1:
        datos_partida = cargar_partida()

        if datos_partida:
            nombre_entrenador = datos_partida["nombre_entrenador"]
            mi_pokemon = datos_partida["pokemon"]
        else:
            print("\n No hay partidas previas. Creando una nueva...")
            nombre_entrenador, mi_pokemon = nueva_partida()
    else:
        nombre_entrenador, mi_pokemon = nueva_partida()

    # ---------------- MENÚ PRINCIPAL ----------------
    while True:
        print("\n" + "=" * 45)
        print(f" 👤 ENTRENADOR: {nombre_entrenador}")
        print(f" 🐾 POKÉMON: {mi_pokemon._nombre} (Nivel {mi_pokemon.nivel})")
        print("=" * 45)
        print(" [1] 🗺️  Explorar Rutas y Combatir")
        print(" [2] 🏥 Visitar Centro Pokémon (Curar)")
        print(" [3] 📊 Ver Ficha de tu Pokémon")
        print(" [4] 💾 Guardar Partida")
        print(" [5] ❌ Salir del Juego")

        try:
            opcion_menu = int(input("\n¿Qué deseas hacer?: "))
        except ValueError:
            print("\n ⚠️ Por favor, introduce un número del 1 al 5.")
            continue

        match opcion_menu:
            case 1:
                # SUBMENÚ DE SELECCIÓN DE RUTAS ANIDADO
                while True:
                    print("\n" + "-" * 15 + " MAPA REGIONAL " + "-" * 15)
                    print(" [1] Ruta 1 (Nivel 2-5)")
                    print(" [2] Ruta 2 (Nivel 5-9)")
                    print(" [3] Ruta 3 - Monte (Nivel 10-16)")
                    print(" [4] Ruta 4 - Costa (Nivel 15-22)")
                    print(" [5] Liga Pokémon (Nivel 25-35)")
                    print(" [6] ↩️ Volver al Menú Principal")
                    
                    try:
                        opcion_ruta = int(input("\n Elige un destino: "))
                    except ValueError:
                        print("\n Introduce un número válido del 1 al 6.")
                        continue
                    
                    if opcion_ruta == 6:
                        break  # Rompe el bucle interno y regresa al menú de arriba
                        
                    if 1 <= opcion_ruta <= 5:
                        rival = explorar_ruta(opcion_ruta)
                        if rival:
                            print(f"\n ¡Un {rival._nombre} salvaje apareció (Nivel {rival.nivel})!")
                            time.sleep(2)
                            mi_pokemon.lucha(rival)
                        break  # Termina la exploración y vuelve al menú principal tras pelear
                    else:
                        print("\n Destino Incorrecto. Elige una opción entre 1 y 6.")

            case 2:
                mi_pokemon.salud_actual = mi_pokemon.salud_maxima
                imprimir_con_retraso("\n 🏥 ¡Las enfermeras Joy han curado a tu Pokémon por completo!\n")
                print(f" PS restaurados: [{mi_pokemon.barra_de_vida:<20}] ({mi_pokemon.salud_actual}/{mi_pokemon.salud_maxima})")
                time.sleep(2)  # Pequeña pausa para que el jugador vea la recuperación

            case 3:
                mi_pokemon.info_pokemon()

            case 4:
                guardar_partida(nombre_entrenador, mi_pokemon)
                time.sleep(1)

            case 5:
                imprimir_con_retraso("\n !Gracias por jugar POOKÉMON (o)! !Hasta pronto!\n")
                break

            case _:
                print("\n ⚠️ Opción no válida. Elige del 1 al 5..")
