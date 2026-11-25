# 🎮 Pokémon Console Adventure — Edición Rojo Fuego / Verde Hoja (Gen III)

¡Bienvenido! Este es un videojuego de rol (RPG) interactivo desarrollado completamente en **Python** para ejecutarse desde la terminal. El proyecto está ambientado fielmente en las mecánicas clásicas de **Pokémon Rojo Fuego y Verde Hoja (Generación III)** en la región de Kanto.

Diseñado como proyecto de **Ingeniería de Sistemas** para aplicar arquitectura modular, diseño orientado a objetos (POO), polimorfismo, encapsulamiento estricto y persistencia segura de datos sin depender de librerías externas.

---

## 🎯 Definición y Reglas del Juego

### Objetivo del Juego
El jugador asume el papel de un entrenador Pokémon que inicia su aventura en la región de Kanto. Su objetivo es explorar las distintas rutas, capturar Pokémon salvajes, entrenar y evolucionar su equipo y superar los desafíos de la región gestionando estratégicamente sus recursos.

### Reglas Principales
1. **Elección inicial:** Al comenzar una nueva partida, el entrenador elige su Pokémon inicial entre **Charmander**, **Squirtle** o **Bulbasaur** entregado por el Profesor Oak.
2. **Límite de equipo activo:** El entrenador puede llevar un máximo de **6 Pokémon activos**; cualquier Pokémon adicional capturado se envía automáticamente al almacenamiento del **PC de Bill**.
3. **Combate por turnos y PP:** Las batallas se desarrollan por turnos. Cada ataque consume **Puntos de Poder (PP)** y el daño se calcula según estadísticas base, naturalezas, bonificación por mismo tipo (**STAB**) y efectividad elemental Gen III (si se agotan todos los PP, el Pokémon usa *Forcejeo* y recibe retroceso).
4. **Debilitamiento y recuperación:** Un Pokémon con `0 PS` queda debilitado y no puede combatir hasta ser curado con medicinas o en un **Centro Pokémon**.
5. **Captura exclusiva de salvajes:** Solo se pueden capturar Pokémon salvajes (nunca de otros entrenadores) mediante **Poké Balls**; la probabilidad depende de la salud restante, estado alterado y ratio de captura.
6. **Economía y persistencia:** El jugador gana pokémonedas (`₽`) al vencer entrenadores para comprar objetos en la tienda y puede guardar o cargar su partida de forma atómica.

### 🏆 Condiciones de Victoria y Derrota
* **Victoria:** Desde el menú del pueblo (**opción 5**), desafía a **Brock** en el Gimnasio de Ciudad Plateada. Al derrotarlo obtienes la **Medalla Roca**, aparece el mensaje **🏆 ¡VICTORIA! Has completado el desafío de Kanto** y la partida concluye.
* **Derrota:** Si todo el equipo activo y el PC quedan sin Pokémon conscientes y no cuentas con un *Revivir*, o si pierdes el combate contra Brock, el juego anuncia **💀 DERROTA** y concluye la partida.

---

## ✨ Características Principales

* **Base de Datos Oficial Gen III (151 Pokémon de Kanto):** Estadísticas base, experiencias base (tope 255), ratios de captura, habilidades y descripciones en español y *learnsets* por nivel extraídos y adaptados desde PokéAPI.
* **Sistema de Combate Fiel a Gen III:**
  * División clásica de daño **Físico / Especial** según el tipo elemental del ataque.
  * Cálculo oficial de daño con **STAB**, efectividad entre 17 tipos, 25 naturalezas (±10%) y variación aleatoria.
  * Gestión de **Puntos de Poder (PP)** y activación automática de **Forcejeo** con daño de retroceso.
  * **Estados alterados y etapas:** Quemadura, parálisis, envenenamiento, sueño, congelación, confusión y modificadores de estadísticas (-6 a +6).
* **Gestión de Equipo y PC de Bill:** Equipo activo de hasta 6 Pokémon, intercambio de posiciones, almacenamiento en caja del PC y apodos personalizados.
* **Economía, Mochila y Tienda Pokémon:** Sistema de pokémonedas (`₽`), compra de Poké Balls, medicinas y piedras evolutivas, además de encuentros en 11 rutas de Kanto.
* **Persistencia Segura en JSON:** Guardado atómico con archivos temporales, respaldo automático (`backup`), validación de esquemas y migraciones de versión.

---

## 🧱 Diseño Orientado a Objetos (POO)

La arquitectura aplica herencia multinivel, polimorfismo puro (sin inspección de tipos en turnos) y encapsulamiento:

* **Herencia Multinivel (`modelos/pokemon.py`):**
  * **`Pokemon` (abuela):** Define estadísticas, movimientos, salud, estados alterados, recuperación de PP y el comportamiento de turno base.
  * **`PokemonCapturable(Pokemon)` (madre):** Añade rareza y ruta de origen, usando `super()` para serializar y reconstruir datos heredados.
  * **`PokemonSalvaje` y `PokemonAtrapado` (nietas):** Especializan la capturabilidad (`es_capturable`), entrenador, apodo (`nombre_visible`) y comportamiento en batalla (`PokemonJugador` se mantiene como alias compatible).
* **Polimorfismo en Objetos y Turnos:**
  * Todas las subclases de `Objeto` (`Pokeball`, `Pocion`, `Revivir`, `CuraEstado`, `PiedraEvolutiva`) redefinen `usar(contexto)`.
  * El turno de combate recorre los participantes y ejecuta sus acciones redefinidas sin emplear `type()` ni `isinstance()`.
* **Encapsulamiento en `Pokemon`:**
  * **Público (`+`):** `nivel`, `exp_actual`, `movimientos`, `estado_alterado` y propiedades (`@property`) como `nombre`, `salud_actual` y `salud_maxima`.
  * **Protegido (`#`):** `_nombre`, `_tipos`, `_salud_actual`, `_estados` y `_restaurar_estado_comun()`.
  * **Privado (`-`):** `__naturaleza`, `__exp_siguiente_nivel` y `__estadisticas`.

---

## 📂 Arquitectura del Proyecto

```text
pokemon_frlg/
├── main.py                  # Punto de entrada y validación inicial de catálogos
├── juego.py                 # Bucle principal y flujo de estados del juego
├── config.py                # Constantes globales, rutas y configuración base
├── .gitignore               # Archivos temporales y caché ignorados por Git
├── datos/                   # Bases de datos Gen III y reglas del juego
│   ├── pokemon_gen3.json
│   ├── movimientos_gen3.json
│   └── tipos_evoluciones.py
├── docs/                    # Documentación y bitácora del proyecto
│   ├── README.md
│   ├── DIAGRAMA_CLASES_ENTREGA1.drawio
│   ├── DIAGRAMA_CLASES_ENTREGA1.jpg
|   └── AVANCES.md
├── interfaz/                # Capa de presentación e interacción en consola
│   ├── inicio.py
│   ├── menus.py
│   ├── demo_entrega1.py
│   ├── pokedex_ui.py
│   └── mensajes.py
├── modelos/                 # Entidades POO con encapsulamiento y polimorfismo
│   ├── pokemon.py           # Jerarquía multinivel: Pokemon -> Capturable -> Salvaje/Atrapado
│   ├── movimiento.py        # Movimientos con validación de PP y precisión
│   ├── equipo.py            # Composición: equipo activo (máx. 6) y PC de Bill
│   ├── mochila.py           # Composición: inventario encapsulado y saldo en ₽
│   ├── objeto.py            # Jerarquía polimórfica: Poké Balls, Medicinas y Piedras
│   └── entrenador.py        # Entrenador jugador y rivales (Cazabichos, LiderGimnasio)
├── mundo/                   # Servicios y localizaciones de Kanto
│   ├── localizaciones.py    # TiendaPokemon y CentroPokemon
│   └── rutas.py             # Definición de rutas y zonas explorables de Kanto
├── partidas/                # Guardados locales y copias de seguridad
├── persistencia/            # Almacenamiento seguro en disco
│   ├── __init__.py
│   ├── guardado.py          # Guardado atómico en JSON y respaldo automático
│   ├── migraciones.py       # Actualización automática de versiones de partida
│   └── validacion.py        # Verificación de integridad de archivos guardados
├── servicios/               # Integración con API y acceso a datos
│   ├── pokeapi.py           # Cliente HTTP con reintentos y ajuste histórico Gen III
│   ├── descargar_datos.py   # Generador de los catálogos JSON locales
│   ├── catalogos.py         # Carga en memoria de Pokémon y movimientos
│   ├── validador_datos.py   # Validación de consistencia de catálogos
│   └── nueva_partida.py     # Flujo inicial con el Profesor Oak
├── sistemas/                # Motor de reglas y mecánicas de juego
│   ├── combate.py           # Motor de batallas salvajes y contra entrenadores
│   ├── efectos.py           # Estados alterados y modificadores de estadísticas
│   ├── estadisticas.py      # Fórmulas Gen III de stats, naturalezas y tipos
│   ├── experiencia.py       # Cálculo de EXP ganada y subida de nivel
│   ├── evolucion.py         # Evolución por nivel y por objetos
│   └── captura.py           # Fórmula oficial de captura con Poké Balls
└── tests/                   # Pruebas automatizadas con assert
    ├── test_basicos.py
    ├── test_entrega1.py
    └── test_entrega2.py
```

---

## 🚀 Cómo Ejecutar el Juego

1. **Clona el repositorio y entra a la carpeta del proyecto:**
   ```bash
   git clone https://github.com/Samux2208/Juego-de-Pokemon-en-Python-Terminal.git
   cd Juego-de-Pokemon-en-Python-Terminal/pokemon_frlg
   ```

2. **Requisitos:** Python **3.10 o superior** (utiliza únicamente la biblioteca estándar de Python, sin instalaciones adicionales).

3. **Preparar los datos (solo si faltan los archivos JSON en `datos/`):**
   ```bash
   python -m servicios.descargar_datos
   ```

4. **Inicia la aventura:**
   ```bash
   python main.py
   ```

5. **Ejecuta las pruebas automatizadas (`assert`):**
   ```bash
   python -m tests.test_entrega2
   python -m tests.test_entrega1
   python -m tests.test_basicos
   ```

---

## 👥 Autores y Colaboradores

Proyecto desarrollado en equipo por:

* **Samuel Alberto Castañeda Barros** — [@Samux2208](https://github.com/Samux2208)
* **Adrian Fernando Caicedo Cejia** — [@anADRIAN18](https://github.com/anADRIAN18)
