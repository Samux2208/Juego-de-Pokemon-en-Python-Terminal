import time
import random
import sys
import pickle

# ============================================================
# CONSTANTES GENERALES
# ============================================================
 
RETRASO_TEXTO = 0.05      # Segundos entre letras en imprimir_con_retraso
NIVEL_MAXIMO = 100
ARCHIVO_PARTIDA = "partida_pookemon.dat"

# ============================================================
# TIPOS Y TABLA DE EFECTIVIDADES (GEN III: 17 TIPOS)
# Las claves se guardan en minúscula y sin tildes; para mostrarlos
# en pantalla se usa nombre_tipo().
# ============================================================

# Tipo de Pokémon dispoinibles
TIPOS = (
    "normal", "fuego", "agua", "electrico", "planta", "hielo", "lucha",
    "veneno", "tierra", "volador", "psiquico", "bicho", "roca", "fantasma",
    "dragon", "siniestro", "acero",
)

# Nombres corregidos con tilde y en Mayuscula la primera letra
NOMBRES_TIPO = {"electrico": "Eléctrico", "psiquico": "Psíquico", "dragon": "Dragón"}
 
# En la Gen III la categoría (físico/especial) depende del TIPO del movimiento.
TIPOS_ESPECIALES = {"fuego", "agua", "planta", "electrico", "hielo", "psiquico", "dragon", "siniestro"}
 
# COLECCIÓN | Formato : tipo atacante -> {multiplicador: (tipos defensores afectados)}
'''
- 2.0 (Ventaja / Súper eficaz): Tipos defensores que reciben el doble de daño.
- 0.5 (Desventaja / Poco eficaz): Tipos defensores que resisten el golpe y reciben la mitad del daño.
- 0.0 (Inmunidad): Tipos defensores que bloquean por completo el ataque, recibiendo cero daño.
- Lo que no aparece: Si un tipo defensor no está en ninguna de esas listas, el código asume por defecto que el daño es neutro (1.0).
'''
_EFECTIVIDADES = {
    "normal":    {0.5: ("roca", "acero"), 0.0: ("fantasma",)},
    "fuego":     {2.0: ("planta", "hielo", "bicho", "acero"), 0.5: ("fuego", "agua", "roca", "dragon")},
    "agua":      {2.0: ("fuego", "tierra", "roca"), 0.5: ("agua", "planta", "dragon")},
    "electrico": {2.0: ("agua", "volador"), 0.5: ("electrico", "planta", "dragon"), 0.0: ("tierra",)},
    "planta":    {2.0: ("agua", "tierra", "roca"),
                  0.5: ("fuego", "planta", "veneno", "volador", "bicho", "dragon", "acero")},
    "hielo":     {2.0: ("planta", "tierra", "volador", "dragon"), 0.5: ("fuego", "agua", "hielo", "acero")},
    "lucha":     {2.0: ("normal", "hielo", "roca", "siniestro", "acero"),
                  0.5: ("veneno", "volador", "psiquico", "bicho"), 0.0: ("fantasma",)},
    "veneno":    {2.0: ("planta",), 0.5: ("veneno", "tierra", "roca", "fantasma"), 0.0: ("acero",)},
    "tierra":    {2.0: ("fuego", "electrico", "veneno", "roca", "acero"), 0.5: ("planta", "bicho"),
                  0.0: ("volador",)},
    "volador":   {2.0: ("planta", "lucha", "bicho"), 0.5: ("electrico", "roca", "acero")},
    "psiquico":  {2.0: ("lucha", "veneno"), 0.5: ("psiquico", "acero"), 0.0: ("siniestro",)},
    "bicho":     {2.0: ("planta", "psiquico", "siniestro"),
                  0.5: ("fuego", "lucha", "veneno", "volador", "fantasma", "acero")},
    "roca":      {2.0: ("fuego", "hielo", "volador", "bicho"), 0.5: ("lucha", "tierra", "acero")},
    "fantasma":  {2.0: ("psiquico", "fantasma"), 0.5: ("siniestro", "acero"), 0.0: ("normal",)},
    "dragon":    {2.0: ("dragon",), 0.5: ("acero",)},
    "siniestro": {2.0: ("psiquico", "fantasma"), 0.5: ("lucha", "siniestro", "acero")},
    "acero":     {2.0: ("hielo", "roca"), 0.5: ("fuego", "agua", "electrico", "acero")},
}

# Creamos un diccionario vacío para almacenar el resultado final
TABLA_TIPOS = {}

# Recorremos los atacantes y sus grupos
for atq, grupos in _EFECTIVIDADES.items():
    
    # Creamos un diccionario vacío dentro del atacante actual
    TABLA_TIPOS[atq] = {}
    
    # Recorremos los multiplicadores y los grupos de defensores
    for mult, defensores in grupos.items():
        
        # Recorremos cada defensor individual dentro de la colección
        for defensor in defensores:
            
            # Asignamos el multiplicador directamente a la combinación Atacante-Defensor
            TABLA_TIPOS[atq][defensor] = mult


def nombre_tipo(tipo):
    '''Devuelve el nombre del tipo listo para mostrar (con tildes y mayúscula).'''

    return NOMBRES_TIPO.get(tipo, tipo.capitalize())


def efectividad_tipos(tipo_movimiento, tipos_defensor):
    '''Multiplicador total de un movimiento contra uno o dos tipos defensores.'''

    mult_total = 1.0
    for tipo in tipos_defensor:
        # Busca el multiplicador del tipo defensor en la tabla; si no existe, usa 1.0 (neutro)
        mult_total *= TABLA_TIPOS.get(tipo_movimiento, {}).get(tipo, 1.0)
    return mult_total

# ============================================================
# CLASE MOVIMIENTO Y BASE DE DATOS GLOBAL DE MOVIMIENTOS
# ============================================================
 
class Movimiento:
    '''Un ataque con daño. Los movimientos de estado no están incluidos.'''
 
    def __init__(self, nombre, tipo, categoria, potencia, precision):
        if tipo not in TIPOS:
            raise ValueError(f"Tipo desconocido para {nombre}: {tipo}")
        if categoria not in ("fisico", "especial"):
            raise ValueError(f"Categoría inválida para {nombre}: {categoria}")

        # Atributos Potegidos (Solo lectura mediante properties)
        self._nombre = nombre
        self._tipo = tipo
        self._categoria = categoria

        # Atributos Modificables (Usan setters para validarse)
        self.potencia = potencia
        self.precision = precision

    # --- PROPERTIES (SOLO LECTURA) ---
    @property
    def nombre(self):
        return self._nombre

    @property
    def tipo(self):
        return self._tipo

    @property
    def categoria(self):
        return self._categoria

    # --- PROPERTIES Y SETTERS (MODIFICABLES CON VALIDACIÓN) ---
    @property
    def potencia(self):
        return self._potencia

    @potencia.setter
    def potencia(self, nuevo_valor):
        if nuevo_valor < 0:
            raise ValueError("La potencia no puede ser negativa")
        self._potencia = nuevo_valor

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, nuevo_valor):
        if not 1 <= nuevo_valor <= 100:
            raise ValueError(f"La precisión de {self.nombre} debe estar entre 1 y 100")
        self._precision = nuevo_valor

    # --- MÉTODOS DE LA CLASE ---
    def impacta(self):
        '''Compara la precisión del movimiento con un número aleatorio (1-100).'''

        return random.randint(1, 100) <= self.precision
 
    def resumen(self):
        '''
        Devuelve una línea de texto formateada con los datos clave del movimiento.
        Para que los ataques se vean ordenados como en una lista de juego
        '''

        cat = "Fís" if self.categoria == "fisico" else "Esp"
        return f"{self.nombre:<18} [{nombre_tipo(self.tipo):<9}| {cat} | Pot {self.potencia:>3} | Prec {self.precision:>3}]"
 
    def __repr__(self):
        '''Devuelve la representación en cadena del movimiento para depuración.'''

        # El sufijo '!r' fuerza el uso de repr() en los textos, agregando comillas automáticas
        return f"Movimiento({self.nombre!r}, {self.tipo!r}, {self.categoria!r}, {self.potencia}, {self.precision})"
 
 
# COLECCIÓN: tipo -> {nombre: (potencia, precisión)}
_DATOS_MOVIMIENTOS = {
    "normal": {
        "Placaje": (35, 95), "Arañazo": (40, 100), "Destructor": (40, 100), "Ataque Rápido": (40, 100),
        "Día de Pago": (40, 100), "Corte": (55, 95), "Rapidez": (60, 100),
        "Cornada": (65, 100), "Pisotón": (65, 100), "Cuchillada": (70, 100), "Golpe Cabeza": (70, 100),
        "Fuerza": (80, 100), "Megapuño": (80, 85), "Triataque": (80, 100), "Velocidad Extrema": (80, 100),
        "Hipercolmillo": (80, 100), "Atizar": (80, 75), "Golpe Cuerpo": (85, 100), "Derribo": (90, 85),
        "Bomba Huevo": (100, 75), "Doble Filo": (120, 100), "Mega Patada": (120, 75), "Hiperrayo": (150, 90),
        "Golpes Furia": (18, 80), "Puño Cometa": (18, 85), "Doble Bofetón": (15, 85), "Atadura": (15, 85),
    },
    "fuego": {
        "Ascuas": (40, 100), "Giro Fuego": (15, 70), "Puño Fuego": (75, 100),
        "Lanzallamas": (95, 100), "Llamarada": (120, 85),
    },
    "agua": {
        "Burbuja": (20, 100), "Pistola Agua": (40, 100), "Tenaza": (35, 75), "Hidropulso": (60, 100),
        "Rayo Burbuja": (65, 100), "Cascada": (80, 100), "Martillazo": (90, 85), "Surf": (95, 100),
        "Hidrobomba": (120, 80),
    },
    "planta": {
        "Absorber": (20, 100), "Látigo Cepa": (35, 100), "Megaagotar": (40, 100), "Hoja Afilada": (55, 95),
        "Gigadrenado": (60, 100), "Danza Pétalo": (70, 100), "Rayo Solar": (120, 100),
    },
    "electrico": {
        "Impactrueno": (40, 100), "Chispa": (65, 100), "Puño Trueno": (75, 100),
        "Rayo": (95, 100), "Trueno": (120, 70),
    },
    "hielo": {
        "Nieve Polvo": (40, 100), "Rayo Aurora": (65, 100), "Puño Hielo": (75, 100),
        "Rayo Hielo": (95, 100), "Ventisca": (120, 70),
    },
    "lucha": {
        "Doble Patada": (30, 100), "Puño Certero": (150, 100), "Golpe Kárate": (50, 100),
        "Patada Giro": (60, 85), "Sumisión": (80, 80), "Patada Salto Alta": (85, 90),
        "Tajo Cruzado": (100, 80),
    },
    "veneno": {
        "Picotazo Veneno": (15, 100), "Polución": (20, 70), "Ácido": (40, 100),
        "Residuos": (65, 100), "Bomba Lodo": (90, 100),
    },
    "tierra": {
        "Bofetón Lodo": (20, 100), "Disparo Lodo": (55, 95), "Excavar": (60, 100),
        "Hueso Palo": (65, 85), "Terremoto": (100, 100),
    },
    "volador": {
        "Picotazo": (35, 100), "Tornado": (40, 100), "Ataque Ala": (60, 100), "Golpe Aéreo": (60, 100),
        "Vuelo": (70, 95), "Pico Taladro": (80, 100),
    },
    "psiquico": {
        "Confusión": (50, 100), "Psicorrayo": (65, 100), "Psíquico": (90, 100),
    },
    "bicho": {
        "Pin Misil": (14, 85), "Chupavidas": (20, 100), "Doble Ataque": (25, 100), "Rayo Señal": (75, 100),
    },
    "roca": {
        "Lanzarrocas": (50, 65), "Tumba Rocas": (50, 80), "Avalancha": (75, 90),
    },
    "fantasma": {
        "Lengüetazo": (20, 100), "Puño Sombra": (60, 100), "Bola Sombra": (80, 100),
    },
    "dragon": {
        "Dragoaliento": (60, 100), "Garra Dragón": (80, 100),
    },
    "siniestro": {
        "Mordisco": (60, 100), "Finta": (60, 100), "Triturar": (80, 100),
    },
    "acero": {
        "Garra Metal": (50, 95), "Ala de Acero": (70, 90), "Cola Férrea": (100, 75),
    },
}
 
# Creamos un diccionario vacío para almacenar los objetos Movimiento finales
DICCIONARIO_MOVIMIENTOS = {}

# Recorremos cada tipo de movimiento en los datos iniciales
for tipo, movimientos in _DATOS_MOVIMIENTOS.items():
        
    # Recorremos cada movimiento individual dentro de ese tipo
    for nombre, (potencia, precision) in movimientos.items():

        # Decidimos la categoría (Especial o Físico) basándonos en el tipo (Regla de Gen III)
        categoria = "especial" if tipo in TIPOS_ESPECIALES else "fisico"
        
        # Creamos el objeto Movimiento y lo guardamos usando su nombre como clave
        DICCIONARIO_MOVIMIENTOS[nombre] = Movimiento(
            nombre, 
            tipo, 
            categoria, 
            potencia, 
            precision
        )

# ============================================================
# BASE DE DATOS DE ESPECIES (151 POKÉMON DE KANTO)
# Formato: nombre: (tipos, (PS, Atq, Def, AtqEsp, DefEsp, Vel), movimientos)
# Los movimientos están ordenados de "aprendido antes" a "aprendido después".
# Un Pokémon conoce los 4 últimos movimientos que su nivel le permite.
# ============================================================
 
_CLAVES_STATS = ("vida", "ataque", "defensa", "atq_esp", "def_esp", "velocidad")

_DATOS_POKEMON = {
    "Bulbasaur":  (("planta", "veneno"), (45, 49, 49, 65, 65, 45), ("Placaje", "Absorber", "Látigo Cepa", "Hoja Afilada", "Danza Pétalo", "Rayo Solar")),
    "Ivysaur":    (("planta", "veneno"), (60, 62, 63, 80, 80, 60), ("Placaje", "Látigo Cepa", "Hoja Afilada", "Megaagotar", "Danza Pétalo", "Rayo Solar")),
    "Venusaur":   (("planta", "veneno"), (80, 82, 83, 100, 100, 80), ("Látigo Cepa", "Hoja Afilada", "Megaagotar", "Danza Pétalo", "Gigadrenado", "Rayo Solar")),
    "Charmander": (("fuego",), (39, 52, 43, 60, 50, 65), ("Arañazo", "Ascuas", "Giro Fuego", "Cuchillada", "Lanzallamas")),
    "Charmeleon": (("fuego",), (58, 64, 58, 80, 65, 80), ("Arañazo", "Ascuas", "Cuchillada", "Giro Fuego", "Lanzallamas", "Dragoaliento")),
    "Charizard":  (("fuego", "volador"), (78, 84, 78, 109, 85, 100), ("Ascuas", "Cuchillada", "Giro Fuego", "Lanzallamas", "Golpe Aéreo", "Garra Dragón", "Llamarada")),
    "Squirtle":   (("agua",), (44, 48, 65, 50, 64, 43), ("Placaje", "Burbuja", "Pistola Agua", "Mordisco", "Hidropulso", "Hidrobomba")),
    "Wartortle":  (("agua",), (59, 63, 80, 65, 80, 58), ("Placaje", "Pistola Agua", "Mordisco", "Rayo Burbuja", "Hidropulso", "Hidrobomba")),
    "Blastoise":  (("agua",), (79, 83, 100, 85, 105, 78), ("Placaje", "Pistola Agua", "Mordisco", "Surf", "Rayo Hielo", "Hidrobomba")),
    "Caterpie":   (("bicho",), (45, 30, 35, 20, 20, 45), ("Placaje", "Chupavidas")),
    "Metapod":    (("bicho",), (50, 20, 55, 25, 25, 30), ("Placaje", "Chupavidas")),
    "Butterfree": (("bicho", "volador"), (60, 45, 50, 80, 80, 70), ("Chupavidas", "Confusión", "Tornado", "Psicorrayo", "Psíquico")),
    "Weedle":     (("bicho", "veneno"), (40, 35, 30, 20, 20, 50), ("Picotazo Veneno", "Chupavidas")),
    "Kakuna":     (("bicho", "veneno"), (45, 25, 50, 25, 25, 35), ("Picotazo Veneno", "Chupavidas")),
    "Beedrill":   (("bicho", "veneno"), (65, 80, 40, 45, 80, 75), ("Picotazo Veneno", "Chupavidas", "Doble Ataque", "Pin Misil", "Rayo Señal")),
    "Pidgey":     (("normal", "volador"), (40, 45, 40, 35, 35, 56), ("Placaje", "Tornado", "Ataque Rápido", "Ataque Ala", "Golpe Aéreo")),
    "Pidgeotto":  (("normal", "volador"), (63, 60, 55, 50, 50, 71), ("Placaje", "Tornado", "Ataque Rápido", "Ataque Ala", "Golpe Aéreo", "Vuelo")),
    "Pidgeot":    (("normal", "volador"), (83, 80, 75, 70, 70, 91), ("Tornado", "Ataque Rápido", "Ataque Ala", "Golpe Aéreo", "Vuelo", "Doble Filo")),
    "Rattata":    (("normal",), (30, 56, 35, 25, 35, 72), ("Placaje", "Ataque Rápido", "Mordisco", "Hipercolmillo")),
    "Raticate":   (("normal",), (55, 81, 60, 50, 70, 97), ("Placaje", "Ataque Rápido", "Mordisco", "Hipercolmillo", "Doble Filo")),
    "Spearow":    (("normal", "volador"), (40, 60, 30, 31, 31, 70), ("Picotazo", "Ataque Rápido", "Pico Taladro", "Golpe Aéreo", "Ataque Ala")),
    "Fearow":     (("normal", "volador"), (65, 90, 65, 61, 61, 100), ("Picotazo", "Ataque Rápido", "Ataque Ala", "Pico Taladro", "Golpe Aéreo")),
    "Ekans":      (("veneno",), (35, 60, 44, 40, 54, 55), ("Atadura", "Picotazo Veneno", "Mordisco", "Ácido", "Residuos", "Bomba Lodo")),
    "Arbok":      (("veneno",), (60, 85, 69, 65, 79, 80), ("Atadura", "Picotazo Veneno", "Mordisco", "Ácido", "Bomba Lodo")),
    "Pikachu":    (("electrico",), (35, 55, 30, 50, 40, 90), ("Impactrueno", "Ataque Rápido", "Chispa", "Rayo", "Trueno")),
    "Raichu":     (("electrico",), (60, 90, 55, 90, 80, 100), ("Impactrueno", "Chispa", "Puño Trueno", "Rayo", "Trueno", "Golpe Cuerpo")),
    "Sandshrew":  (("tierra",), (50, 75, 85, 20, 30, 40), ("Arañazo", "Bofetón Lodo", "Cuchillada", "Excavar", "Terremoto")),
    "Sandslash":  (("tierra",), (75, 100, 110, 45, 55, 65), ("Arañazo", "Bofetón Lodo", "Cuchillada", "Excavar", "Terremoto", "Golpes Furia")),
    "Nidoran♀":   (("veneno",), (55, 47, 52, 40, 40, 41), ("Arañazo", "Picotazo Veneno", "Mordisco", "Golpes Furia", "Bomba Lodo")),
    "Nidorina":   (("veneno",), (70, 62, 67, 55, 55, 56), ("Arañazo", "Picotazo Veneno", "Mordisco", "Golpes Furia", "Bomba Lodo", "Doble Patada")),
    "Nidoqueen":  (("veneno", "tierra"), (90, 82, 87, 75, 85, 76), ("Arañazo", "Picotazo Veneno", "Golpe Cuerpo", "Bomba Lodo", "Terremoto", "Megapuño")),
    "Nidoran♂":   (("veneno",), (46, 57, 40, 40, 40, 50), ("Picotazo Veneno", "Doble Patada", "Cornada", "Bomba Lodo")),
    "Nidorino":   (("veneno",), (61, 72, 57, 55, 55, 65), ("Picotazo Veneno", "Doble Patada", "Cornada", "Bomba Lodo", "Golpe Cabeza")),
    "Nidoking":   (("veneno", "tierra"), (81, 92, 77, 85, 75, 85), ("Picotazo Veneno", "Cornada", "Bomba Lodo", "Doble Patada", "Terremoto", "Megapuño")),
    "Clefairy":   (("normal",), (70, 45, 48, 60, 65, 35), ("Destructor", "Doble Bofetón", "Puño Cometa", "Golpe Cuerpo", "Psíquico")),
    "Clefable":   (("normal",), (95, 70, 73, 85, 90, 60), ("Destructor", "Doble Bofetón", "Puño Cometa", "Golpe Cuerpo", "Psíquico", "Megapuño")),
    "Vulpix":     (("fuego",), (38, 41, 40, 50, 65, 65), ("Ascuas", "Ataque Rápido", "Giro Fuego", "Lanzallamas", "Llamarada")),
    "Ninetales":  (("fuego",), (73, 76, 75, 81, 100, 100), ("Ascuas", "Ataque Rápido", "Giro Fuego", "Lanzallamas", "Llamarada")),
    "Jigglypuff": (("normal",), (115, 45, 20, 45, 25, 20), ("Destructor", "Doble Bofetón", "Golpe Cuerpo", "Doble Filo")),
    "Wigglytuff": (("normal",), (140, 70, 45, 75, 50, 45), ("Destructor", "Doble Bofetón", "Golpe Cuerpo", "Megapuño", "Doble Filo")),
    "Zubat":      (("veneno", "volador"), (40, 45, 35, 30, 40, 55), ("Chupavidas", "Mordisco", "Ataque Ala", "Golpe Aéreo", "Triturar")),
    "Golbat":     (("veneno", "volador"), (75, 80, 70, 65, 75, 90), ("Chupavidas", "Mordisco", "Ataque Ala", "Golpe Aéreo", "Triturar")),
    "Oddish":     (("planta", "veneno"), (45, 50, 55, 75, 65, 30), ("Absorber", "Ácido", "Megaagotar", "Danza Pétalo", "Hoja Afilada", "Rayo Solar")),
    "Gloom":      (("planta", "veneno"), (60, 65, 70, 85, 75, 40), ("Absorber", "Ácido", "Megaagotar", "Danza Pétalo", "Bomba Lodo", "Rayo Solar")),
    "Vileplume":  (("planta", "veneno"), (75, 80, 85, 100, 90, 50), ("Absorber", "Ácido", "Danza Pétalo", "Megaagotar", "Bomba Lodo", "Rayo Solar")),
    "Paras":      (("bicho", "planta"), (35, 70, 55, 45, 55, 25), ("Arañazo", "Chupavidas", "Absorber", "Cuchillada", "Megaagotar")),
    "Parasect":   (("bicho", "planta"), (60, 95, 80, 60, 80, 30), ("Arañazo", "Chupavidas", "Megaagotar", "Cuchillada", "Gigadrenado", "Rayo Solar")),
    "Venonat":    (("bicho", "veneno"), (60, 55, 50, 40, 55, 45), ("Placaje", "Confusión", "Chupavidas", "Psicorrayo", "Psíquico")),
    "Venomoth":   (("bicho", "veneno"), (70, 65, 60, 90, 75, 90), ("Placaje", "Confusión", "Chupavidas", "Psicorrayo", "Bomba Lodo", "Psíquico")),
    "Diglett":    (("tierra",), (10, 55, 25, 35, 45, 95), ("Arañazo", "Bofetón Lodo", "Excavar", "Terremoto")),
    "Dugtrio":    (("tierra",), (35, 80, 50, 50, 70, 120), ("Arañazo", "Bofetón Lodo", "Excavar", "Cuchillada", "Terremoto")),
    "Meowth":     (("normal",), (40, 45, 35, 40, 40, 90), ("Arañazo", "Mordisco", "Día de Pago", "Cuchillada", "Triturar")),
    "Persian":    (("normal",), (65, 70, 60, 65, 65, 115), ("Arañazo", "Mordisco", "Día de Pago", "Cuchillada", "Triturar", "Triataque")),
    "Psyduck":    (("agua",), (50, 52, 48, 65, 50, 55), ("Arañazo", "Pistola Agua", "Confusión", "Hidropulso", "Hidrobomba")),
    "Golduck":    (("agua",), (80, 82, 78, 95, 80, 85), ("Arañazo", "Pistola Agua", "Confusión", "Hidropulso", "Psíquico", "Hidrobomba")),
    "Mankey":     (("lucha",), (40, 80, 35, 35, 45, 70), ("Arañazo", "Golpe Kárate", "Doble Patada", "Patada Giro", "Sumisión")),
    "Primeape":   (("lucha",), (65, 105, 60, 60, 70, 95), ("Arañazo", "Golpe Kárate", "Patada Giro", "Sumisión", "Tajo Cruzado", "Terremoto")),
    "Growlithe":  (("fuego",), (55, 70, 45, 70, 50, 60), ("Mordisco", "Ascuas", "Giro Fuego", "Lanzallamas", "Llamarada")),
    "Arcanine":   (("fuego",), (90, 110, 80, 100, 80, 95), ("Mordisco", "Ascuas", "Velocidad Extrema", "Lanzallamas", "Triturar", "Llamarada")),
    "Poliwag":    (("agua",), (40, 50, 40, 40, 40, 90), ("Burbuja", "Pistola Agua", "Doble Bofetón", "Rayo Burbuja", "Hidrobomba")),
    "Poliwhirl":  (("agua",), (65, 65, 65, 50, 50, 90), ("Burbuja", "Pistola Agua", "Doble Bofetón", "Rayo Burbuja", "Golpe Cuerpo", "Hidrobomba")),
    "Poliwrath":  (("agua", "lucha"), (90, 85, 95, 70, 90, 70), ("Pistola Agua", "Rayo Burbuja", "Sumisión", "Golpe Cuerpo", "Hidrobomba", "Tajo Cruzado")),
    "Abra":       (("psiquico",), (25, 20, 15, 105, 55, 90), ("Confusión", "Psicorrayo", "Psíquico")),
    "Kadabra":    (("psiquico",), (40, 35, 30, 120, 70, 105), ("Confusión", "Psicorrayo", "Psíquico")),
    "Alakazam":   (("psiquico",), (55, 50, 45, 135, 85, 120), ("Confusión", "Psicorrayo", "Psíquico", "Bola Sombra")),
    "Machop":     (("lucha",), (70, 80, 50, 35, 35, 35), ("Golpe Kárate", "Puño Certero", "Patada Giro", "Sumisión", "Tajo Cruzado")),
    "Machoke":    (("lucha",), (80, 100, 70, 50, 60, 45), ("Golpe Kárate", "Puño Certero", "Patada Giro", "Sumisión", "Tajo Cruzado", "Terremoto")),
    "Machamp":    (("lucha",), (90, 130, 80, 65, 85, 55), ("Golpe Kárate", "Puño Certero", "Sumisión", "Megapuño", "Tajo Cruzado", "Terremoto")),
    "Bellsprout": (("planta", "veneno"), (50, 75, 35, 70, 30, 40), ("Látigo Cepa", "Picotazo Veneno", "Ácido", "Hoja Afilada", "Rayo Solar")),
    "Weepinbell": (("planta", "veneno"), (65, 90, 50, 85, 45, 55), ("Látigo Cepa", "Ácido", "Hoja Afilada", "Megaagotar", "Bomba Lodo", "Rayo Solar")),
    "Victreebel": (("planta", "veneno"), (80, 105, 65, 100, 60, 70), ("Látigo Cepa", "Ácido", "Hoja Afilada", "Bomba Lodo", "Gigadrenado", "Rayo Solar")),
    "Tentacool":  (("agua", "veneno"), (40, 40, 35, 50, 100, 70), ("Picotazo Veneno", "Ácido", "Rayo Burbuja", "Hidropulso", "Surf")),
    "Tentacruel": (("agua", "veneno"), (80, 70, 65, 80, 120, 100), ("Picotazo Veneno", "Ácido", "Rayo Burbuja", "Hidropulso", "Bomba Lodo", "Surf")),
    "Geodude":    (("roca", "tierra"), (40, 80, 100, 30, 30, 20), ("Placaje", "Bofetón Lodo", "Lanzarrocas", "Tumba Rocas", "Terremoto")),
    "Graveler":   (("roca", "tierra"), (55, 95, 115, 45, 45, 35), ("Placaje", "Lanzarrocas", "Tumba Rocas", "Avalancha", "Terremoto", "Megapuño")),
    "Golem":      (("roca", "tierra"), (80, 110, 130, 55, 65, 45), ("Placaje", "Lanzarrocas", "Avalancha", "Terremoto", "Megapuño", "Doble Filo")),
    "Ponyta":     (("fuego",), (50, 85, 55, 65, 65, 90), ("Placaje", "Ascuas", "Pisotón", "Giro Fuego", "Derribo", "Llamarada")),
    "Rapidash":   (("fuego",), (65, 100, 70, 80, 80, 105), ("Ascuas", "Pisotón", "Giro Fuego", "Derribo", "Cornada", "Llamarada")),
    "Slowpoke":   (("agua", "psiquico"), (90, 65, 65, 40, 40, 15), ("Placaje", "Confusión", "Pistola Agua", "Golpe Cabeza", "Psíquico")),
    "Slowbro":    (("agua", "psiquico"), (95, 75, 110, 100, 80, 30), ("Placaje", "Confusión", "Pistola Agua", "Golpe Cabeza", "Surf", "Psíquico")),
    "Magnemite":  (("electrico", "acero"), (25, 35, 70, 95, 55, 45), ("Placaje", "Impactrueno", "Chispa", "Rayo", "Trueno")),
    "Magneton":   (("electrico", "acero"), (50, 60, 95, 120, 70, 70), ("Placaje", "Impactrueno", "Chispa", "Rayo", "Trueno")),
    "Farfetch'd": (("normal", "volador"), (52, 65, 55, 58, 62, 60), ("Picotazo", "Corte", "Golpe Aéreo", "Cuchillada")),
    "Doduo":      (("normal", "volador"), (35, 85, 45, 35, 35, 75), ("Picotazo", "Ataque Rápido", "Pico Taladro", "Derribo")),
    "Dodrio":     (("normal", "volador"), (60, 110, 70, 60, 60, 100), ("Picotazo", "Ataque Rápido", "Pico Taladro", "Derribo", "Golpe Aéreo")),
    "Seel":       (("agua",), (65, 45, 55, 45, 70, 45), ("Cornada", "Pistola Agua", "Rayo Aurora", "Surf", "Rayo Hielo")),
    "Dewgong":    (("agua", "hielo"), (90, 70, 80, 70, 95, 70), ("Cornada", "Pistola Agua", "Rayo Aurora", "Golpe Cuerpo", "Surf", "Rayo Hielo")),
    "Grimer":     (("veneno",), (80, 80, 50, 40, 50, 25), ("Destructor", "Bofetón Lodo", "Ácido", "Residuos", "Bomba Lodo")),
    "Muk":        (("veneno",), (105, 105, 75, 65, 100, 50), ("Destructor", "Bofetón Lodo", "Ácido", "Residuos", "Bomba Lodo", "Golpe Cuerpo")),
    "Shellder":   (("agua",), (30, 65, 100, 45, 25, 40), ("Placaje", "Tenaza", "Rayo Aurora", "Hidropulso", "Rayo Hielo")),
    "Cloyster":   (("agua", "hielo"), (50, 95, 180, 85, 45, 70), ("Tenaza", "Rayo Aurora", "Hidropulso", "Surf", "Rayo Hielo", "Hidrobomba")),
    "Gastly":     (("fantasma", "veneno"), (30, 35, 30, 100, 35, 80), ("Lengüetazo", "Puño Sombra", "Bola Sombra", "Bomba Lodo")),
    "Haunter":    (("fantasma", "veneno"), (45, 50, 45, 115, 55, 95), ("Lengüetazo", "Puño Sombra", "Bola Sombra", "Bomba Lodo", "Psíquico")),
    "Gengar":     (("fantasma", "veneno"), (60, 65, 60, 130, 75, 110), ("Lengüetazo", "Puño Sombra", "Bola Sombra", "Bomba Lodo", "Psíquico")),
    "Onix":       (("roca", "tierra"), (35, 45, 160, 30, 45, 70), ("Placaje", "Lanzarrocas", "Tumba Rocas", "Avalancha", "Cola Férrea", "Terremoto")),
    "Drowzee":    (("psiquico",), (60, 48, 45, 43, 90, 42), ("Destructor", "Confusión", "Golpe Cabeza", "Psicorrayo", "Psíquico")),
    "Hypno":      (("psiquico",), (85, 73, 70, 73, 115, 67), ("Destructor", "Confusión", "Golpe Cabeza", "Psicorrayo", "Psíquico")),
    "Krabby":     (("agua",), (30, 105, 90, 25, 25, 50), ("Burbuja", "Rayo Burbuja", "Martillazo", "Hidrobomba")),
    "Kingler":    (("agua",), (55, 130, 115, 50, 50, 75), ("Burbuja", "Rayo Burbuja", "Cuchillada", "Martillazo", "Hidrobomba")),
    "Voltorb":    (("electrico",), (40, 30, 50, 55, 55, 100), ("Placaje", "Impactrueno", "Chispa", "Rayo", "Trueno")),
    "Electrode":  (("electrico",), (60, 50, 70, 80, 80, 140), ("Placaje", "Impactrueno", "Chispa", "Rayo", "Trueno", "Golpe Cuerpo")),
    "Exeggcute":  (("planta", "psiquico"), (60, 40, 80, 60, 45, 40), ("Placaje", "Absorber", "Confusión", "Megaagotar", "Bomba Huevo", "Psíquico")),
    "Exeggutor":  (("planta", "psiquico"), (95, 95, 85, 125, 65, 55), ("Placaje", "Confusión", "Megaagotar", "Bomba Huevo", "Psíquico", "Rayo Solar")),
    "Cubone":     (("tierra",), (50, 50, 95, 40, 50, 35), ("Destructor", "Hueso Palo", "Golpe Cabeza", "Excavar", "Terremoto")),
    "Marowak":    (("tierra",), (60, 80, 110, 50, 80, 45), ("Destructor", "Hueso Palo", "Golpe Cabeza", "Excavar", "Terremoto", "Derribo")),
    "Hitmonlee":  (("lucha",), (50, 120, 53, 35, 110, 87), ("Doble Patada", "Patada Giro", "Patada Salto Alta", "Mega Patada", "Terremoto")),
    "Hitmonchan": (("lucha",), (50, 105, 79, 35, 110, 76), ("Puño Certero", "Puño Fuego", "Puño Hielo", "Puño Trueno", "Megapuño")),
    "Lickitung":  (("normal",), (90, 55, 75, 60, 75, 30), ("Destructor", "Lengüetazo", "Golpe Cuerpo", "Derribo", "Megapuño")),
    "Koffing":    (("veneno",), (40, 65, 95, 60, 45, 35), ("Placaje", "Polución", "Residuos", "Bomba Lodo", "Doble Filo")),
    "Weezing":    (("veneno",), (65, 90, 120, 85, 70, 60), ("Placaje", "Polución", "Residuos", "Bomba Lodo", "Derribo", "Doble Filo")),
    "Rhyhorn":    (("tierra", "roca"), (80, 85, 95, 30, 30, 25), ("Cornada", "Pisotón", "Avalancha", "Derribo", "Terremoto")),
    "Rhydon":     (("tierra", "roca"), (105, 130, 120, 45, 45, 40), ("Cornada", "Pisotón", "Avalancha", "Terremoto", "Doble Filo")),
    "Chansey":    (("normal",), (250, 5, 5, 35, 105, 50), ("Destructor", "Doble Bofetón", "Golpe Cuerpo", "Puño Cometa", "Doble Filo")),
    "Tangela":    (("planta",), (65, 55, 115, 100, 40, 60), ("Atadura", "Látigo Cepa", "Megaagotar", "Gigadrenado", "Rayo Solar")),
    "Kangaskhan": (("normal",), (105, 95, 80, 40, 80, 90), ("Puño Cometa", "Mordisco", "Golpe Cuerpo", "Megapuño", "Doble Filo")),
    "Horsea":     (("agua",), (30, 40, 70, 70, 25, 60), ("Burbuja", "Pistola Agua", "Rayo Burbuja", "Hidropulso", "Hidrobomba")),
    "Seadra":     (("agua",), (55, 65, 95, 95, 45, 85), ("Burbuja", "Pistola Agua", "Rayo Burbuja", "Dragoaliento", "Hidropulso", "Hidrobomba")),
    "Goldeen":    (("agua",), (45, 67, 60, 35, 50, 63), ("Picotazo", "Cornada", "Cascada", "Surf")),
    "Seaking":    (("agua",), (80, 92, 65, 65, 80, 68), ("Picotazo", "Cornada", "Cascada", "Surf", "Rayo Hielo")),
    "Staryu":     (("agua",), (30, 45, 55, 70, 55, 85), ("Placaje", "Pistola Agua", "Hidropulso", "Rayo Aurora", "Hidrobomba")),
    "Starmie":    (("agua", "psiquico"), (60, 75, 85, 100, 85, 115), ("Placaje", "Pistola Agua", "Hidropulso", "Rayo Aurora", "Psíquico", "Hidrobomba")),
    "Mr. Mime":   (("psiquico",), (40, 45, 65, 100, 120, 90), ("Confusión", "Doble Bofetón", "Psicorrayo", "Psíquico")),
    "Scyther":    (("bicho", "volador"), (70, 110, 80, 55, 80, 105), ("Ataque Rápido", "Corte", "Doble Ataque", "Golpe Aéreo", "Cuchillada", "Ala de Acero")),
    "Jynx":       (("hielo", "psiquico"), (65, 50, 35, 115, 95, 95), ("Destructor", "Nieve Polvo", "Confusión", "Rayo Aurora", "Psíquico", "Ventisca")),
    "Electabuzz": (("electrico",), (65, 83, 57, 95, 85, 105), ("Impactrueno", "Puño Certero", "Chispa", "Puño Trueno", "Rayo", "Trueno")),
    "Magmar":     (("fuego",), (65, 95, 57, 100, 85, 93), ("Ascuas", "Puño Certero", "Giro Fuego", "Puño Fuego", "Lanzallamas", "Llamarada")),
    "Pinsir":     (("bicho",), (65, 125, 100, 55, 70, 85), ("Corte", "Golpes Furia", "Cuchillada", "Derribo", "Doble Filo")),
    "Tauros":     (("normal",), (75, 100, 95, 40, 70, 110), ("Placaje", "Pisotón", "Cornada", "Derribo", "Doble Filo", "Terremoto")),
    "Magikarp":   (("agua",), (20, 10, 55, 15, 20, 80), ("Placaje",)),
    "Gyarados":   (("agua", "volador"), (95, 125, 79, 60, 100, 81), ("Mordisco", "Pistola Agua", "Dragoaliento", "Cascada", "Hidrobomba")),
    "Lapras":     (("agua", "hielo"), (130, 85, 80, 85, 95, 60), ("Pistola Agua", "Rayo Aurora", "Golpe Cuerpo", "Surf", "Rayo Hielo", "Hidrobomba")),
    "Ditto":      (("normal",), (48, 48, 48, 48, 48, 48), ("Placaje",)),
    "Eevee":      (("normal",), (55, 55, 50, 45, 65, 55), ("Placaje", "Ataque Rápido", "Mordisco", "Golpe Cuerpo")),
    "Vaporeon":   (("agua",), (130, 65, 60, 110, 95, 65), ("Placaje", "Ataque Rápido", "Pistola Agua", "Mordisco", "Rayo Aurora", "Hidrobomba")),
    "Jolteon":    (("electrico",), (65, 65, 60, 110, 95, 130), ("Placaje", "Ataque Rápido", "Impactrueno", "Rayo", "Trueno")),
    "Flareon":    (("fuego",), (65, 130, 60, 95, 110, 65), ("Placaje", "Ataque Rápido", "Ascuas", "Mordisco", "Lanzallamas", "Llamarada")),
    "Porygon":    (("normal",), (65, 60, 70, 85, 75, 40), ("Placaje", "Psicorrayo", "Rayo Aurora", "Triataque", "Rayo", "Psíquico")),
    "Omanyte":    (("roca", "agua"), (35, 40, 100, 90, 55, 35), ("Pistola Agua", "Tumba Rocas", "Rayo Burbuja", "Hidropulso", "Surf", "Hidrobomba")),
    "Omastar":    (("roca", "agua"), (70, 60, 125, 115, 70, 55), ("Pistola Agua", "Tumba Rocas", "Rayo Burbuja", "Avalancha", "Surf", "Hidrobomba")),
    "Kabuto":     (("roca", "agua"), (30, 80, 90, 55, 45, 55), ("Arañazo", "Absorber", "Tumba Rocas", "Megaagotar", "Avalancha")),
    "Kabutops":   (("roca", "agua"), (60, 115, 105, 65, 70, 80), ("Arañazo", "Absorber", "Cuchillada", "Megaagotar", "Avalancha", "Cascada")),
    "Aerodactyl": (("roca", "volador"), (80, 105, 65, 60, 75, 130), ("Mordisco", "Ataque Ala", "Avalancha", "Golpe Aéreo", "Hiperrayo")),
    "Snorlax":    (("normal",), (160, 110, 65, 65, 110, 30), ("Placaje", "Destructor", "Golpe Cuerpo", "Megapuño", "Terremoto", "Hiperrayo")),
    "Articuno":   (("hielo", "volador"), (90, 85, 100, 95, 125, 85), ("Picotazo", "Nieve Polvo", "Ataque Ala", "Rayo Aurora", "Rayo Hielo", "Ventisca")),
    "Zapdos":     (("electrico", "volador"), (90, 90, 85, 125, 90, 100), ("Picotazo", "Impactrueno", "Ataque Ala", "Pico Taladro", "Rayo", "Trueno")),
    "Moltres":    (("fuego", "volador"), (90, 100, 90, 125, 85, 90), ("Picotazo", "Ascuas", "Ataque Ala", "Lanzallamas", "Golpe Aéreo", "Llamarada")),
    "Dratini":    (("dragon",), (41, 64, 45, 50, 50, 50), ("Atadura", "Dragoaliento", "Golpe Cuerpo", "Garra Dragón", "Hiperrayo")),
    "Dragonair":  (("dragon",), (61, 84, 65, 70, 70, 70), ("Atadura", "Dragoaliento", "Golpe Cuerpo", "Garra Dragón", "Rayo Hielo", "Hiperrayo")),
    "Dragonite":  (("dragon", "volador"), (91, 134, 95, 100, 100, 80), ("Atadura", "Dragoaliento", "Golpe Cuerpo", "Garra Dragón", "Terremoto", "Hiperrayo")),
    "Mewtwo":     (("psiquico",), (106, 110, 90, 154, 90, 130), ("Confusión", "Psicorrayo", "Psíquico", "Rayo Hielo", "Lanzallamas")),
    "Mew":        (("psiquico",), (100, 100, 100, 100, 100, 100), ("Destructor", "Confusión", "Psicorrayo", "Psíquico", "Lanzallamas", "Rayo")),
}

# Estructura pública: sigue el formato original (tipos, movimientos, EVs) pero completa.
# "EVs" contiene las estadísticas base; "exp_base" se usa para la experiencia ganada.
# Creamos un diccionario vacío para almacenar los Pokémon finales
DICCIONARIO_POKEMON = {}

# Recorremos los datos iniciales de los Pokémon uno por uno
for nombre, (tipos, stats, movimientos) in _DATOS_POKEMON.items():
    
    # Guardamos todo en el diccionario principal
    DICCIONARIO_POKEMON[nombre] = {
        "tipos": list(tipos),
        "movimientos": list(movimientos),
        "EVs": dict(zip(_CLAVES_STATS, stats)), # zip(_CLAVES_STATS, stats) empareja "Vida" con stats[0], "ataque" con stats[1], etc.
        "exp_base": sum(stats) // 5 # Sumamos y calculamos la experiencia de forma simple
    }
 
INICIALES = {1: "Charmander", 2: "Squirtle", 3: "Bulbasaur"}

# ============================================================
# RUTAS DE KANTO (progresión de dificultad y pools coherentes)
# ============================================================
 
RUTAS = [
    {"nombre": "Ruta 1 - Pueblo Paleta", "niveles": (2, 5),
     "mensaje": "\n🚶 Caminando en la hierba baja de la Ruta 1...\n",
     "pool": ["Pidgey", "Rattata"]},
    {"nombre": "Bosque Verde", "niveles": (3, 7),
     "mensaje": "\n🌲 Adentrándote entre los árboles del Bosque Verde...\n",
     "pool": ["Caterpie", "Weedle", "Metapod", "Kakuna", "Pidgey", "Rattata", "Pikachu"]},
    {"nombre": "Monte Moon (cueva)", "niveles": (10, 16),
     "mensaje": "\n🌙 Tus pasos resuenan en la oscuridad del Monte Moon...\n",
     "pool": ["Zubat", "Geodude", "Paras", "Clefairy", "Sandshrew", "Jigglypuff"]},
    {"nombre": "Praderas de Kanto (Rutas 5-8)", "niveles": (10, 18),
     "mensaje": "\n🌾 Cruzando las amplias praderas entre ciudades...\n",
     "pool": ["Oddish", "Bellsprout", "Meowth", "Mankey", "Growlithe", "Vulpix", "Abra",
              "Ekans", "Nidoran♀", "Nidoran♂", "Venonat", "Pidgeotto"]},
    {"nombre": "Costa Marina (Rutas 12-19)", "niveles": (14, 22),
     "mensaje": "\n🌊 Cruzando las corrientes de la costa...\n",
     "pool": ["Psyduck", "Poliwag", "Krabby", "Tentacool", "Goldeen", "Horsea", "Staryu",
              "Shellder", "Slowpoke", "Seel", "Magikarp"]},
    {"nombre": "Túnel Roca (cueva)", "niveles": (16, 24),
     "mensaje": "\n🔦 Avanzas a ciegas por el Túnel Roca...\n",
     "pool": ["Zubat", "Golbat", "Geodude", "Graveler", "Machop", "Onix"]},
    {"nombre": "Central de Energía", "niveles": (18, 25),
     "mensaje": "\n⚡ Las chispas saltan por la abandonada Central de Energía...\n",
     "pool": ["Pikachu", "Magnemite", "Voltorb", "Electabuzz", "Electrode", "Magneton"]},
    {"nombre": "Torre Pokémon", "niveles": (18, 25),
     "mensaje": "\n👻 Un escalofrío te recorre al subir por la Torre Pokémon...\n",
     "pool": ["Gastly", "Haunter", "Cubone", "Drowzee"]},
    {"nombre": "Mansión Pokémon", "niveles": (22, 30),
     "mensaje": "\n🔥 Recorres las ruinas calcinadas de la Mansión Pokémon...\n",
     "pool": ["Growlithe", "Vulpix", "Koffing", "Grimer", "Ponyta", "Magmar", "Weezing", "Muk"]},
    {"nombre": "Camino Victoria (cueva)", "niveles": (30, 38),
     "mensaje": "\n⛰️ Subes el peligroso Camino Victoria...\n",
     "pool": ["Machoke", "Golem", "Golbat", "Onix", "Marowak", "Arbok", "Primeape", "Dugtrio"]},
    {"nombre": "Meseta Índigo (Liga Pokémon)", "niveles": (38, 45),
     "mensaje": "\n🏆 ¡Llegando a la Meseta Épica de la Liga Pokémon!\n",
     "pool": ["Charizard", "Blastoise", "Venusaur", "Arcanine", "Alakazam", "Gengar", "Machamp",
              "Gyarados", "Dragonite", "Rhydon", "Nidoking", "Nidoqueen", "Starmie", "Lapras",
              "Ninetales", "Snorlax"]},
]


def _validar_datos():
    """
    Comprueba que todas las bases de datos del juego sean correctas.
    
    Revisa que no existan tipos inventados, movimientos inexistentes
    o rutas con Pokémon que no están registrados en el juego.
    """
    
    # 1) VALIDACIÓN DE LA TABLA DE EFECTIVIDADES
    for atq, grupos in _EFECTIVIDADES.items():
        # Comprobamos si el tipo atacante existe en nuestra lista oficial
        if atq not in TIPOS:
            raise ValueError(f"Tipo atq inválido: {atq}")
            
        # Recorremos cada grupo de defensores (las tuplas de tipos)
        for defensores in grupos.values():
            for defensor in defensores:
                # Comprobamos si cada defensor individual es un tipo válido
                if defensor not in TIPOS:
                    raise ValueError(f"Tipo defensor inválido en {atq}: {defensor}")

    # 2) VALIDACIÓN DEL TOTAL DE LA POKÉDEX
    if len(DICCIONARIO_POKEMON) != 151:
        raise ValueError(f"Se esperaban 151 especies y hay {len(DICCIONARIO_POKEMON)}")

    # 3) VALIDACIÓN DE CADA POKÉMON INDIVIDUAL
    for nombre, datos in DICCIONARIO_POKEMON.items():
        lista_tipos = datos["tipos"]
        cantidad_tipos = len(lista_tipos)
        
        # Un Pokémon solo puede tener 1 o 2 tipos
        if cantidad_tipos < 1 or cantidad_tipos > 2:
            raise ValueError(f"{nombre} debe tener 1 o 2 tipos, pero tiene {cantidad_tipos}")
            
        # Comprobamos que sus tipos existan en la lista oficial
        for tipo in lista_tipos:
            if tipo not in TIPOS:
                raise ValueError(f"El Pokémon {nombre} tiene un tipo inválido: {tipo}")
                
        # Comprobamos que sus movimientos existan en el diccionario de movimientos
        for mov in datos["movimientos"]:
            if mov not in DICCIONARIO_MOVIMIENTOS:
                raise ValueError(f"{nombre} usa un movimiento inexistente: {mov}")

    # 4) VALIDACIÓN DE LOS ENCUENTROS EN LAS RUTAS
    for ruta in RUTAS:
        
        # Comprobamos que cada Pokémon de la ruta exista en la Pokédex
        for especie in ruta["pool"]:
            if especie not in DICCIONARIO_POKEMON:
                raise ValueError(f"{ruta["nombre"]} usa una especie inexistente: {especie}")

_validar_datos()
 
 
def describir_disponibilidad(nombre):
    """Texto de la Pokédex que indica dónde se encuentra la especie."""
    
    # Comprobamos si el Pokémon es un inicial usando el método .values()
    if nombre in INICIALES.values():
        return "Inicial; solo se elige una línea inicial por partida."
        
    # Creamos una lista con datos del recorrido
    # Recorremos todas las rutas de la lista, extrayendo el grupo de encuentros (el pool)
    rutas = [ruta["nombre"] for ruta in RUTAS if nombre in ruta["pool"]]
            
    # Evaluamos el resultado de las rutas encontradas
    if rutas:
        # Unimos los nombres de las rutas con comas usando .join()
        return "Se encuentra en: " + ", ".join(rutas) + "."
        
    # Si la lista quedó vacía, significa que es un Pokémon especial o evolución
    return "No aparece en rutas salvajes (evolución o Pokémon especial)."

# ============================================================
# RETRASO DE TEXTO Y FUNCIONES DE UTILIDAD
# ===========================================================

def imprimir_con_retraso(s):
    '''Imprime una letra a la vez.'''

    for letra in s:
        sys.stdout.write(letra)
        sys.stdout.flush()
        time.sleep(RETRASO_TEXTO)  # Default de 0.05 segundos entre letras


def exp_para_nivel(nivel):
    """Experiencia acumulada necesaria para alcanzar un nivel."""

    return int((nivel ** 3) * 0.8)


def calcular_estadisticas(base, nivel):
    """Estadísticas reales a partir de las base de la especie y el nivel."""

    stats = {}
    # CALCULAMOS LAS ESTADÍSTICAS ESTÁNDAR
    # (Ataque, Defensa, Ataque Especial, Defensa Especial, Velocidad)
    for clave in _CLAVES_STATS:
        # Fórmula oficial simplificada: (Base * 2 * Nivel) / 100 + 5
        stats[clave] = ((base[clave] * 2 * nivel) // 100) + 5
    
    # CALCULAMOS LA VIDA (PS) CON SU FÓRMULA ESPECIAL
    # La vida escala sumando el nivel del Pokémon + 10 puntos fijos
    stats["vida"] = ((base["vida"] * 2 * nivel) // 100) + nivel + 10
    return stats


def generar_movimientos(especie, nivel):
    """
    Determina los 4 movimientos actuales de un Pokémon basándose 
    en su nivel, simulando el olvido de ataques antiguos.
    """

    # OBTENEMOS TODOS LOS MOVIMIENTOS APRENDIBLES POR LA ESPECIE
    lista_completa = DICCIONARIO_POKEMON[especie]["movimientos"]
    
    # CALCULAMOS CUÁNTOS MOVIMIENTOS HA DESBLOQUEADO SEGÚN SU NIVEL
    # Empieza con 2 y gana uno nuevo cada 7 niveles.
    movimientos_disponibles = 2 + (nivel // 7)
    
    # Nos aseguramos de que el número esté entre 1 y el total real de la especie
    cantidad_final = max(1, min(len(lista_completa), movimientos_disponibles))
    
    # APLICAMOS LOS RECORTES
    # Primero: filtramos los que ya puede usar por su nivel
    movimientos_por_nivel = lista_completa[:cantidad_final]
    
    # Segundo: nos quedamos solo con los últimos 4 (los más recientes)
    ultimos_cuatro_nombres = movimientos_por_nivel[-4:]
    
    # CONVERTIMOS LOS NOMBRES EN OBJETOS MOVIMIENTO REALES
    pool_movimientos = []
    for nombre in ultimos_cuatro_nombres:
        objeto_movimiento = DICCIONARIO_MOVIMIENTOS[nombre]
        pool_movimientos.append(objeto_movimiento)
    return pool_movimientos
 
 
def mostrar_barras(jugador, rival):
    """Imprime las barras de vida de ambos Pokémon."""

    print("\n" + "~" * 45)
    print(f" {jugador.nombre:<15} PS [{jugador.barra_de_vida:<20}] ({jugador.salud_actual}/{jugador.salud_maxima})")
    print(f" {rival.nombre:<15} PS [{rival.barra_de_vida:<20}] ({rival.salud_actual}/{rival.salud_maxima})")
    print("~" * 45)
    time.sleep(.5)

# ============================================================
# CLASE PRINCIPAL POKÉMON
# ============================================================

class Pokemon:
    def __init__(self, nombre, nivel=1):
        if nombre not in DICCIONARIO_POKEMON:
            raise ValueError(f"Especie desconocida: {nombre}")
        datos = DICCIONARIO_POKEMON[nombre]
        if not isinstance(nivel, int) or not 1 <= nivel <= NIVEL_MAXIMO:
            raise ValueError(f"El nivel debe estar entre 1 y {NIVEL_MAXIMO}.")
 
        # PROTEGIDOS: Accesibles en herencia, protegidos del exterior
        self._nombre = nombre
        self._tipos = tuple(datos["tipos"])
 
        # PÚBLICOS
        self.nivel = nivel
        self.exp_actual = exp_para_nivel(self.nivel)
        self.movimientos = generar_movimientos(nombre, self.nivel)
 
        # PRIVADOS: estadísticas calculadas y umbral de experiencia
        self.__exp_siguiente_nivel = exp_para_nivel(self.nivel + 1)
        self.__estadisticas = calcular_estadisticas(datos["EVs"], self.nivel)
 
        # PÚBLICO: cambia en cada turno del combate
        self.salud_actual = self.__estadisticas["vida"]

    # ---------------- PROPIEDADES DE SOLO LECTURA ----------------
    @property
    def nombre(self):
        return self._nombre
 
    @property
    def tipos(self):
        return self._tipos
 
    @property
    def salud_maxima(self):
        return self.__estadisticas["vida"]
 
    @property
    def ataque(self):
        return self.__estadisticas["ataque"]
 
    @property
    def defensa(self):
        return self.__estadisticas["defensa"]
 
    @property
    def ataque_especial(self):
        return self.__estadisticas["atq_esp"]
 
    @property
    def defensa_especial(self):
        return self.__estadisticas["def_esp"]
 
    @property
    def velocidad(self):
        return self.__estadisticas["velocidad"]
 
    @property
    def exp_siguiente_nivel(self):
        return self.__exp_siguiente_nivel

    @property
    def barra_de_vida(self):
        '''
        Propiedad dinámica: Calcula cuántas barras "=" mostrar 
        según la salud actual del Pokémon en el combate.
        '''

        total_barras = 20 # El tamaño fijo de tu barra visual

        # Evitamos división por cero si el Pokémon se debilita
        if self.salud_maxima == 0:
            return ""
            
        # Calculamos cuántas barras le quedan proporcionalmente
        barras = int((self.salud_actual / self.salud_maxima) * total_barras)

        # Si le queda al menos 1 PS, mostramos al menos una barra
        if self.salud_actual > 0 and barras == 0:
            barras = 1  
        return "=" * barras

    # ---------------- ENCAPSULAMIENTO Y COMBATE ----------------
    def _recibir_danio(self, cantidad):
        """Método protegido: reduce los PS sin permitir valores negativos."""

        cantidad = max(0, int(cantidad))
        self.salud_actual = max(0, self.salud_actual - cantidad)

    def recibir_danio(self, cantidad):
        """Interfaz pública para recibir daño; puede especializarse en las hijas."""

        self._recibir_danio(cantidad)

    # ---------------- PERSISTENCIA ----------------
    def exportar_datos(self):
        """Datos mínimos (tipos primitivos) para guardar el Pokémon."""

        # Creamos una lista vacía para almacenar solo los nombres de los ataques
        lista_nombres_movimientos = []
        
        # Recorremos los objetos de tipo Movimiento que tiene el Pokémon
        for atq in self.movimientos:
            # Extraemos el texto del nombre del ataque y lo añadimos a la lista
            lista_nombres_movimientos.append(atq.nombre)
            
        # Armamos y devolvemos el diccionario final con los datos básicos
        return {
            "nombre": self._nombre,
            "nivel": self.nivel,
            "exp_actual": self.exp_actual,
            "salud_actual": self.salud_actual,
            "movimientos": lista_nombres_movimientos
        }
    
    @classmethod
    def cargar_datos(cls, datos):
        """Reconstruye un Pokémon guardado; las estadísticas se recalculan siempre."""

        # Extraemos el nombre y el nivel del diccionario para crear el objeto base
        # Usamos .get() por seguridad: si no hay nivel guardado, por defecto será 1
        nivel = datos.get("nivel", 1)

        # Verificamos si el método fue invocado desde la clase padre y si el registro es del jugador
        if cls is Pokemon and datos.get("clase") == "PokemonJugador":
            pokemon = PokemonJugador(
                datos["nombre"], nivel,
                entrenador=datos.get("entrenador", "Entrenador"),
                apodo=datos.get("apodo")
            )
        # Verificamos si fue invocado desde la clase padre y el registro corresponde a un Pokémon salvaje
        elif cls is Pokemon and datos.get("clase") == "PokemonSalvaje":
            # Instanciamos la subclase PokemonSalvaje recuperando su rareza y ruta de origen
            pokemon = PokemonSalvaje(
                datos["nombre"], nivel,
                rareza=datos.get("rareza", "comun"),
                ruta=datos.get("ruta", "Desconocida")
            )
        # Caso por defecto: ocurre cuando es un Pokémon base o cuando se llamó directamente desde una subclase
        else:
            # Creamos la instancia usando la clase exacta que invocó el método (cls)
            pokemon = cls(datos["nombre"], nivel)

        # Asignamos la experiencia actual asegurando que tenga sentido para su nivel
        pokemon.exp_actual = max(datos.get("exp_actual", pokemon.exp_actual), exp_para_nivel(pokemon.nivel))
        
        # 3. Reconstruimos la lista de objetos Movimiento de forma tradicional
        lista_nombres_movimientos = datos.get("movimientos", [])
        lista_objetos_movimientos = []
                
        for nombre_movimiento in lista_nombres_movimientos:
            # Si el ataque existe en nuestra base de datos, recuperamos el objeto completo
            if nombre_movimiento in DICCIONARIO_MOVIMIENTOS:
                objeto_ataque = DICCIONARIO_MOVIMIENTOS[nombre_movimiento]
                lista_objetos_movimientos.append(objeto_ataque)
                        
        # Si encontramos movimientos válidos, le asignamos máximo 4 al Pokémon
        if lista_objetos_movimientos:
            pokemon.movimientos = lista_objetos_movimientos[:4]

         # 4. Recuperamos la salud asegurando que no supere el máximo ni sea menor que 0
        salud = datos.get("salud_actual", pokemon.salud_maxima)
        # Limitamos el valor: min() evita que supere el máximo, max() evita que baje de 0
        pokemon.salud_actual = max(0, min(int(salud), pokemon.salud_maxima))
        # Entregamos el Pokémon completamente restaurado listo para jugar
        return pokemon

    # ---------------- FICHA TÉCNICA ----------------
    def info_pokemon(self):
        '''Muestra la ficha técnica paginada del Pokémon.'''

        # Buscamos en qué rutas aparece este Pokémon para generar el texto de ubicación
        notas_entrenador = describir_disponibilidad(self.nombre)
    
        # PRECALCULAMOS LA BARRA DE EXPERIENCIA
        exp_base_nivel_actual = exp_para_nivel(self.nivel)
        exp_necesaria = max(1, self.exp_siguiente_nivel - exp_base_nivel_actual)
        exp_progresada = self.exp_actual - exp_base_nivel_actual
    
        # Determinamos cuántos caracteres '#' pintar (escala de 0 a 10)
        barras_exp = int(max(0, exp_progresada) / exp_necesaria * 10)
        if exp_progresada > 0 and barras_exp == 0:
            barras_exp = 1  # Ajuste estético mínimo
        
        barra_visual_exp = "#" * min(10, max(0, barras_exp))

        # Configuramos el menú para que se abra siempre en la primera página de información
        pagina_actual = 1

        while True:
            print("\n" + "=" * 58)

            if pagina_actual == 1:
                # --- PÁGINA 1: DATOS BÁSICOS ---
                print("=" * 58)
                print(f" INFO. POKéMON\t\t\tPÁGINA [1/2]")
                print("=" * 58)
                print(f" NOMBRE:   {self.nombre:<20} NIVEL:    {self.nivel}")
                print(f" TIPO:     {" / ".join(nombre_tipo(tipo) for tipo in self._tipos)}")
                print("-" * 58)
                print(" NOTAS DE LA POKÉDEX 📝")
                print(f" {notas_entrenador}")
                print("=" * 58)
                print(" MOVIMIENTOS")
                for mov in self.movimientos:
                    print(f"  {mov.resumen()}")
                print("=" * 58)
                print("\n [ENTER] Ver Habilidades  |  [X] Volver al Menú")

            else:
                # --- PÁGINA 2: ESTADÍSTICAS ---
                print(f" HABIL. POKéMON\t\t\tPÁGINA [2/2]")
                print("=" * 58)
                print(f" Nv.{self.nivel:<13} PS: [{self.barra_de_vida:<20}] {self.salud_actual}/{self.salud_maxima}")
                print(f" ATAQUE    {self.ataque:<6} DEFENSA    {self.defensa}")
                print(f" ATQ. ESP. {self.ataque_especial:<6} DEF.ESP.   {self.defensa_especial:<6} VELOCIDAD {self.velocidad}")
                print("-" * 58)
                print(f" EXPERIENCIA. ✨        EXP [{barra_visual_exp:<10}]")
                print(f" PUNTOS EXP. {self.exp_actual:<10} SIG. NIVEL {self.__exp_siguiente_nivel}")
                print("=" * 58)
                print("\n [ENTER] Ver Datos Básicos  |  [X] Volver al Menú")

            # Captura la entrada del jugador
            accion = input("\n Selecciona una opción: ").strip().lower()
            if accion == 'x':
                break  # Sale del bucle de la ficha y regresa al menú de tu partida
            # Si presiona ENTER (o cualquier otra tecla que no sea X), alterna la página
            pagina_actual = 2 if pagina_actual == 1 else 1

    # ---------------- PROGRESIÓN ----------------
    def comprobar_subida_nivel(self):
        '''
        Verifica si el Pokémon acumuló suficiente experiencia para subir 
        de nivel (uno o varios), actualiza sus estadísticas y gestiona 
        los nuevos movimientos aprendidos.
        '''

        subio_nivel = False
        
        # BUCLE DE SUBIDA DE NIVEL MULTIPLE
        while (self.exp_actual >= self.__exp_siguiente_nivel and self.nivel < NIVEL_MAXIMO):
            self.nivel += 1
            subio_nivel = True
            
            # Recalculamos cuánta EXP necesitará para el próximo nivel
            self.__exp_siguiente_nivel = exp_para_nivel(self.nivel + 1)
            
            imprimir_con_retraso(f"\n ¡Felicidades! ¡{self.nombre} subió al Nivel {self.nivel}! 🎉\n")
            time.sleep(2)
            
        # ACTUALIZACIÓN DE ESTADÍSTICAS (Si subió al menos un nivel)
        if subio_nivel:

            # Guardamos la salud máxima anterior.
            salud_anterior = self.salud_maxima

            # Recalculamos todas las estadísticas reales usando los EVs base
            self.__estadisticas = calcular_estadisticas(DICCIONARIO_POKEMON[self._nombre]["EVs"], self.nivel)

            # Sumamos la diferencia de PS máximos a la salud actual para no "herir" al Pokémon
            self.salud_actual += (self.salud_maxima - salud_anterior)
            imprimir_con_retraso(" ¡Las estadísticas de tu Pokémon han aumentado!\n")

            # GESTIÓN DE NUEVOS MOVIMIENTOS
            # Guardamos los nombres de los ataques que ya conoce en un conjunto eficiente
            conocidos = {m.nombre for m in self.movimientos}
            nuevos = generar_movimientos(self._nombre, self.nivel)

            for mov in nuevos:
                # Si es un movimiento que no conocía antes, lo aprende
                if mov.nombre not in conocidos:
                    imprimir_con_retraso(f" ¡{self.nombre} aprendió {mov.nombre}!\n")
            
            # Actualizamos la lista oficial del Pokémon
            self.movimientos = nuevos

     # ---------------- COMBATE ----------------
    def calcular_danio(self, movimiento, objetivo):
        '''
        Calcula el daño real que causará un movimiento sobre un objetivo,
        aplicando las reglas de categorías, STAB, efectividad y aleatoriedad de la Gen III.
        
        Devuelve un grupo: (daño_final, mult_toal_efectividad).
        '''
        # COMPROBAMOS LA EFECTIVIDAD DE TIPOS
        efectividad = efectividad_tipos(movimiento.tipo, objetivo.tipos)
        if efectividad == 0:
            return 0, 0.0 # El objetivo es inmune a este tipo de ataque

        # SELECCIONAMOS LAS ESTADÍSTICAS SEGÚN LA CATEGORÍA DEL MOVIMIENTO
        if movimiento.categoria == "fisico":
            ataque, defensa = self.ataque, objetivo.defensa
        else:
            ataque, defensa = self.ataque_especial, objetivo.defensa_especial
        
        # CÁLCULO DEL DAÑO BASE (Fórmula Oficial Nintendo)
        # Protegemos contra división por cero en la defensa
        defensa_segura = max(1, defensa)
        
        factor_nivel = (2 * self.nivel) // 5 + 2
        poder_ofensivo = factor_nivel * ataque * movimiento.potencia
        
        daño_base = (poder_ofensivo // defensa_segura) // 50 + 2

        # APLICAMOS LOS MULTIPLICADORES FINALES
        # Bonificación STAB: +50% de daño si el Pokémon comparte tipo con el movimiento
        stab = 1.5 if movimiento.tipo in self._tipos else 1.0

        # Variación aleatoria clásica entre el 85% y el 100% del daño
        variacion = random.uniform(0.85, 1.0)

        # Calculamos el impacto final y Garantizamos que cualquier golpe exitoso inflija como mínimo 1 PS de daño
        return max(1, int(daño_base * efectividad * stab * variacion)), efectividad

    def atacar(self, defensor, movimiento, es_rival=False):
        """
        Ejecuta la secuencia completa de un ataque en combate.
        
        Evalúa de forma ordenada si el movimiento acierta, calcula el daño
        según las efectividades y actualiza los PS del Pokémon defensor.
        """
        # IDENTIFICAMOS QUIÉN ATACA PARA EL TEXTO
        quien = f"El {self.nombre} rival" if es_rival else self.nombre

        imprimir_con_retraso(f"\n {quien} usó {movimiento.nombre}!")
        time.sleep(1)

        # COMPROBAMOS SI EL ATAQUE ACERTA O FALLA (Precisión)
        if not movimiento.impacta():
            imprimir_con_retraso(f" ¡El ataque de {self.nombre} falló!\n")
            return

        # CALCULAMOS EL DAÑO Y VERIFICAMOS INMUNIDADES
        danio, efectividad = self.calcular_danio(movimiento, defensor)
        if efectividad == 0:
            imprimir_con_retraso(f"\n No afecta a {defensor.nombre}...\n")
            return

        # APLICAMOS EL DAÑO REDUCIENDO LOS PS DEL DEFENSOR (Mínimo 0)
        defensor.salud_actual = max(0, defensor.salud_actual - danio)

        # NOTIFICAMOS LA EFECTIVIDAD DEL GOLPE AL JUGADOR
        if efectividad > 1:
            imprimir_con_retraso(" ¡Es muy eficaz!\n")
        elif efectividad < 1:
            imprimir_con_retraso(" No es muy eficaz...\n")
        else:
            imprimir_con_retraso(" ¡El ataque impactó!\n")

    def _elegir_movimiento(self):
        print(f"\n ¡Adelante {self.nombre}!")
        # MOSTRAMOS LA LISTA DE MOVIMIENTOS EN PANTALLA
        for i, mov in enumerate(self.movimientos, start=1):
            print(f" {i}. {mov.resumen()}")
        # BUCLE SEGURO DE CAPTURA DE DATOS
        while True:
            try:
                # Solicitamos la opción al jugador
                indice = int(input("\n Elige un movimiento: "))
                # Verificamos que el número ingresado esté dentro del menú
                if 1 <= indice <= len(self.movimientos):
                    # Convertimos el número humano al índice interno de Python (restamos 1)
                    return self.movimientos[indice - 1]
                print(" ❌ Movimiento fuera de rango. Selecciona uno de la lista.")
            except ValueError:
                print(" ❌ Introduce un número válido.")

    def turno(self, rival):
            '''
            Ejecuta el bucle continuo del combate ronda tras ronda.
            Determina quién es más veloz en cada turno y procesa los ataques.
            El bucle se detiene inmediatamente cuando la salud de cualquiera llega a 0.
            '''
            mostrar_barras(self, rival)
            time.sleep(.5)
            # MIENTRAS AMBOS POKÉMON TENGAN VIDA, EL COMBATE CONTINÚA
            while (self.salud_actual > 0 and rival.salud_actual > 0):
                
                ## INTERFAZ Y DECISIONES
                mov_jugador = self._elegir_movimiento()
                mov_rival = random.choice(rival.movimientos)

                # CALCULO DE PRIORIDAD DE VELOCIDAD
                if self.velocidad == rival.velocidad:
                    # Si empatan en velocidad, decidimos al azar (50% de probabilidad)
                    primero = random.random() < 0.5
                else:
                    primero = self.velocidad > rival.velocidad

                # ORDENAMIENTO DE LAS ACCIONES
                # Formato de la lista: (atacante, defensor, movimiento, es_rival)
                acciones = [(self, rival, mov_jugador, False), (rival, self, mov_rival, True)]
                # Si el rival ganó la prioridad de velocidad, invertimos la lista
                if not primero:
                    acciones.reverse()

                # EJECUCIÓN DE LOS ATAQUES DE LA RONDA
                for atacante, defensor, mov, es_rival in acciones:
                    atacante.atacar(defensor, mov, es_rival)
                    mostrar_barras(self, rival)
                    time.sleep(2)

                    # CONTROL DE DEBILITACIÓN INMEDIATA
                    # Si el defensor cae debilitado por el primer golpe, cortamos la ronda
                    if defensor.salud_actual <= 0:
                        imprimir_con_retraso(f"\n ... ¡{defensor.nombre} se debilitó!\n")
                        break # Rompe el "for" de ataques, lo que hará que el "while" también termine

    def lucha(self, rival):
        """
        Gestiona el flujo global del combate: coordina las rondas de ataque
        y administra las consecuencias de la batalla (victoria o derrota).
        """
        # INICIAMOS EL COMBATE COMPLETO (No saldrá de aquí hasta que alguien tenga 0 PS)
        self.turno(rival)

        # EVALUAMOS EL RESULTADO DE LA BATALLA
        if self.salud_actual > 0:

            # --- ESCENARIO DE VICTORIA ---
            # Generamos la recompensa económica aleatoria (Pokedólares ₽)
            moneda = random.randint(150, 1200)
            imprimir_con_retraso(f"\n ¡Has ganado el combate! Obtuviste ${moneda} ₽.\n")

            # Calculamos la experiencia ganada usando la base del rival y su nivel
            base_exp = DICCIONARIO_POKEMON[rival.nombre]["exp_base"]
            exp_ganada = max(1, int(base_exp * rival.nivel / 7)) # Aseguramos un mínimo de 1 EXP
            imprimir_con_retraso(f" ¡{self.nombre} ganó {exp_ganada} puntos de EXP! ✨\n")

            # Aplicamos la experiencia y verificamos si sube de nivel
            self.exp_actual += exp_ganada
            self.comprobar_subida_nivel()
        else:
            # --- ESCENARIO DE DERROTA ---
            imprimir_con_retraso(f"\n ¡{self.nombre} no puede continuar! Corre al Centro Pokémon...\n")

# ============================================================
# CLASES HIJAS: POKÉMON DEL JUGADOR Y POKÉMON SALVAJE
# ============================================================

class PokemonJugador(Pokemon):
    """Pokémon que pertenece al entrenador y puede tener un apodo."""

    def __init__(self, nombre, nivel=1, entrenador="Entrenador", apodo=None):
        super().__init__(nombre, nivel)
        if not isinstance(entrenador, str) or not entrenador.strip():
            raise ValueError("El nombre del entrenador no puede estar vacío.")
        if apodo is not None:
            if not isinstance(apodo, str) or not apodo.strip():
                raise ValueError("El apodo debe contener texto.")
            if len(apodo.strip()) > 15:
                raise ValueError("El apodo no puede superar los 15 caracteres.")
        self.entrenador = entrenador.strip()
        self.apodo = apodo.strip() if apodo else None

    def recibir_danio(self, cantidad):
        """El Pokémon del jugador recibe daño mediante el método heredado."""

        super().recibir_danio(cantidad)

    def exportar_datos(self):
        datos = super().exportar_datos()
        datos.update({"entrenador": self.entrenador, "apodo": self.apodo})
        return datos


class PokemonSalvaje(Pokemon):
    """Pokémon encontrado durante la exploración de una ruta."""

    RAREZAS_VALIDAS = ("comun", "raro", "muy raro")

    def __init__(self, nombre, nivel=1, rareza="comun", ruta="Desconocida"):
        super().__init__(nombre, nivel)
        if rareza not in self.RAREZAS_VALIDAS:
            raise ValueError(
                f"Rareza inválida. Usa una de estas opciones: {', '.join(self.RAREZAS_VALIDAS)}."
            )
        if not isinstance(ruta, str) or not ruta.strip():
            raise ValueError("La ruta del Pokémon salvaje no puede estar vacía.")
        self.rareza = rareza
        self.ruta = ruta.strip()

    def recibir_danio(self, cantidad):
        """El Pokémon salvaje recibe daño mediante el método heredado."""
        super().recibir_danio(cantidad)

    def exportar_datos(self):
        datos = super().exportar_datos()
        datos.update({"rareza": self.rareza, "ruta": self.ruta})
        return datos

# ============================================================
# PERSISTENCIA (GUARDAR Y CARGAR PARTIDA)
# ============================================================

def guardar_partida(nombre_entrenador, mi_pokemon):
    '''Guarda el entrenador y su Pokémon en un archivo binario.'''

    datos_partida = {
        "nombre_entrenador": nombre_entrenador,
        "pokemon": mi_pokemon.exportar_datos(),
    }
    try:
        with open(ARCHIVO_PARTIDA, "wb") as archivo:
            pickle.dump(datos_partida, archivo)
        print("\n💾 ¡Partida guardada correctamente!")
    except (OSError, pickle.PickleError) as error:
        print(f"❌ No se pudo guardar la partida: {error}")


def cargar_partida():
    """
    Carga la partida guardada. Devuelve None si no existe o está dañada.
    También acepta partidas del formato antiguo (objeto Pokemon completo).
    """
    try:
        with open(ARCHIVO_PARTIDA, "rb") as archivo:
            datos_partida = pickle.load(archivo)
        
        pokemon_guardado = datos_partida["pokemon"]
        
        if isinstance(pokemon_guardado, dict):
            pokemon = Pokemon.cargar_datos(pokemon_guardado)
        else:
            # Doble capa de seguridad: si es un formato antiguo del objeto puro, 
            # extraemos sus datos básicos y usamos tu cargar_datos para reconstruirlo a salvo.
            antiguo = vars(pokemon_guardado)
            datos_adaptados = {
                "nombre": antiguo.get("_nombre"),
                "nivel": antiguo.get("nivel", 5),
                "exp_actual": antiguo.get("exp_actual", 0),
                "salud_actual": antiguo.get("salud_actual"),
                "movimientos": [m.nombre for m in (antiguo.get("movimientos") or [])]
            }
            pokemon = Pokemon.cargar_datos(datos_adaptados)
        
        print(f"\n ¡Bienvenido de nuevo, {datos_partida['nombre_entrenador']}! 👋")
        return {"nombre_entrenador": datos_partida["nombre_entrenador"], "pokemon": pokemon}
    
    except FileNotFoundError:
        return None
    
    except (OSError, pickle.PickleError, EOFError, KeyError, AttributeError, ValueError, TypeError) as error:
        print(f"\n ⚠️ La partida guardada no se pudo leer ({error}).")
        return None

# ============================================================
# EXPLORACIÓN DE RUTAS
# ============================================================
 
def explorar_ruta(numero_ruta):
    """Genera un Pokémon salvaje aleatorio del pool de la ruta elegida (1..len(RUTAS))."""
    
    if not 1 <= numero_ruta <= len(RUTAS):
        return None
    ruta = RUTAS[numero_ruta - 1]
    imprimir_con_retraso(ruta["mensaje"])
    especie = random.choice(ruta["pool"])
    nivel = random.randint(*ruta["niveles"])
    return PokemonSalvaje(especie, nivel, rareza="comun", ruta=ruta["nombre"])
 

# ============================================================
# INICIO DE PARTIDA NUEVA
# ============================================================

def nueva_partida():
    '''Solicita el nombre y permite elegir el Pokémon inicial.'''

    print("\n" + "=" * 45)
    print("          NUEVA PARTIDA POKÉMON")
    print("=" * 45)

    nombre_entrenador = input("\n Primero dime, ¿cómo te llamas? ¡Tu aventura está por comenzar!: ").strip()
    while not nombre_entrenador:
        nombre_entrenador = input(" El nombre no puede estar vacío. Inténtalo de nuevo: ").strip()

    print("\nEl profesor te ofrece elegir a tu compañero inicial:")
    for numero, especie in INICIALES.items():
        print(f"[{numero}] {especie:<11} (Tipo {nombre_tipo(DICCIONARIO_POKEMON[especie]['tipos'][0]).lower()})")

    while True:
        try:
            opcion = int(input("\n Elige tu inicial (1-3): "))
            if opcion in INICIALES:
                break
            print(" Opción no válida. Elige 1, 2 o 3.")
        except ValueError:
            print(" Debes introducir un número entero.")

    especie = INICIALES[opcion]
    mi_pokemon = PokemonJugador(especie, 5, entrenador=nombre_entrenador)

    print(f"\n¡Felicidades, {nombre_entrenador}!")
    print(f"¡{especie} será tu compañero de aventuras!")

    # Guardado inmediato para evitar perder el inicio de la partida.
    guardar_partida(nombre_entrenador, mi_pokemon)

    return nombre_entrenador, mi_pokemon

# ============================================================
# BUCLE PRINCIPAL DEL JUEGO
# ============================================================

def menu_rutas(mi_pokemon):
    """
    Despliega el menú interactivo con las rutas disponibles en la región.
    Permite al jugador seleccionar un destino para iniciar un combate salvaje.
    """
    # Calculamos la opción de salida de forma dinámica basada en el total de rutas
    volver = len(RUTAS) + 1

    while True:
        print("\n" + "🗺️  " + "-" * 13 + " MAPA REGIONAL " + "-" * 13)

        # LISTAMOS LAS RUTAS DISPONIBLES CON SUS NIVELES
        for i, ruta in enumerate(RUTAS, start=1):
            nivel_min, nivel_max = ruta["niveles"]
            print(f" [{i}] {ruta["nombre"]} (Nivel {nivel_min}-{nivel_max})")
        print(f" [{volver}] ↩️ Volver al Menú Principal")
 
        # CAPTURA SEGURA DE LA SELECCIÓN DEL JUGADOR
        try:
            opcion_ruta = int(input("\n ¿A qué destino deseas viajar?: "))
        except ValueError:
            print(f"\n ❌ Introduce un número válido del 1 al {volver}.")
            continue
 
        # CONTROL DE NAVEGACIÓN Y FLUJO
        if opcion_ruta == volver:
            return # Regresa al menú principal sin hacer nada
        
        if 1 <= opcion_ruta <= len(RUTAS):
            # Simulamos la exploración y generación del Pokémon rival en esa ruta
            rival = explorar_ruta(opcion_ruta)

            print(f"\n 🌿 ¡Un {rival.nombre} salvaje apareció (Nivel {rival.nivel})!")
            time.sleep(2)

            # Iniciamos la secuencia de combate completa
            mi_pokemon.lucha(rival)

            # Tras el combate, regresamos obligatoriamente al menú principal para seguridad del jugador
            return
        
        print(f"\n ❌ Destino incorrecto. Elige una opción entre 1 y {volver}.")

def main():
    print("=" * 45)
    print("       ¡BIENVENIDO AL MUNDO POOKÉMON!")
    print("=" * 45)
    print("\n[1] Continuar Partida")
    print("[2] Nueva Partida")

    # CONTROL DE ARRANQUE E INICIALIZACIÓN DE DATOS
    while True:
        try:
            op = int(input("\n Selecciona una opción: "))
            if op in (1, 2):
                break
            print(" ❌ Por favor, selecciona 1 o 2.")
        except ValueError:
            print(" ❌ Introduce un número válido.")

    if op == 1:
        datos_partida = cargar_partida()

        if datos_partida:
            nombre_entrenador = datos_partida["nombre_entrenador"]
            mi_pokemon = datos_partida["pokemon"]
        else:
            print("\n No hay partidas previas. Creando una nueva...")
            nombre_entrenador, mi_pokemon = nueva_partida()
    else:
        nombre_entrenador, mi_pokemon = nueva_partida()

    # BUCLE GENERAL DEL MENÚ PRINCIPAL DEL JUEGO
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
            op_menu = int(input("\n¿Qué deseas hacer?: "))
        except ValueError:
            print("\n ⚠️ Por favor, introduce un número del 1 al 5.")
            continue

        # GESTIÓN DE LAS ACCIONES DEL JUEGO
        match op_menu:
            case 1:
                # Bloqueo de seguridad: Evita combatir si el Pokémon no tiene PS
                if mi_pokemon.salud_actual <= 0:
                    print("\n ⚠️ Tu Pokémon está debilitado. Visita el Centro Pokémon primero.")
                else:
                    menu_rutas(mi_pokemon)
                    
            case 2:
                # Restauración total de salud
                mi_pokemon.salud_actual = mi_pokemon.salud_maxima
                imprimir_con_retraso("\n 🏥 ¡Las enfermeras Joy han curado a tu Pokémon por completo!\n")
                print(f" PS restaurados: [{mi_pokemon.barra_de_vida:<20}] ({mi_pokemon.salud_actual}/{mi_pokemon.salud_maxima}) ")
                time.sleep(2)  # Pequeña pausa para que el jugador vea la recuperación

            case 3:
                # Abre la interfaz del pokemon
                mi_pokemon.info_pokemon()

            case 4:
                # Llama a los sistemas de persistencia binaria con pickle
                guardar_partida(nombre_entrenador, mi_pokemon)
                time.sleep(.5)

            case 5:
                # Cierre seguro del programa
                imprimir_con_retraso("\n 👋 !Gracias por jugar POOKÉMON (o)! !Hasta pronto!\n")
                break

            case _:
                print("\n ⚠️ Opción no válida. Elige del 1 al 5..")
                time.sleep(.5)


def pruebas_basicas():
    """Pruebas sencillas de clases, herencia, validación y efectividad."""
    pokemon = Pokemon("Pikachu", 5)
    assert pokemon.nombre == "Pikachu"
    assert efectividad_tipos("agua", ("fuego",)) == 2.0

    jugador = PokemonJugador("Charmander", 5, entrenador="Prueba")
    assert jugador.entrenador == "Prueba"
    assert isinstance(jugador, Pokemon)

    salvaje = PokemonSalvaje("Rattata", 4, rareza="comun", ruta="Ruta 1")
    assert isinstance(salvaje, Pokemon)

    vida_inicial = jugador.salud_actual
    jugador.recibir_danio(3)
    assert jugador.salud_actual == max(0, vida_inicial - 3)

    try:
        PokemonJugador("Charmander", 5, entrenador="")
    except ValueError:
        pass
    else:
        raise AssertionError("La validación del entrenador no rechazó un nombre vacío.")

    print("✓ Pruebas básicas superadas.\n")


if __name__ == "__main__":
    pruebas_basicas()
    main()
