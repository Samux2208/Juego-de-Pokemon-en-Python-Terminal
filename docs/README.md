# 🎮 Pokémon Console Adventure — Edición Rojo Fuego / Verde Hoja (Gen III)

¡Bienvenido! Este es un videojuego de rol (RPG) interactivo desarrollado completamente en **Python** para ejecutarse desde la terminal. El proyecto está ambientado fielmente en las mecánicas clásicas de **Pokémon Rojo Fuego y Verde Hoja (Generación III)** en la región de Kanto.

Diseñado como proyecto de **Ingeniería** para aplicar arquitectura modular, diseño orientado a objetos (POO), encapsulamiento estricto, manejo de excepciones y persistencia segura de datos.

---

## 🎯 Definición del Juego

### Nombre del Juego
**Pokémon Console Adventure — Edición Rojo Fuego / Verde Hoja (Gen III)**

### Objetivo del Juego
El jugador asume el papel de un entrenador Pokémon que inicia su aventura en la región de Kanto. Su objetivo es explorar las distintas rutas, capturar Pokémon salvajes, formar y entrenar un equipo competitivo, evolucionar a sus criaturas y superar los combates y desafíos de la región gestionando estratégicamente sus recursos.

### Reglas del Juego
1. **Elección inicial:** Al comenzar una nueva partida, el entrenador debe elegir un Pokémon inicial entre **Charmander**, **Squirtle** o **Bulbasaur** entregado por el Profesor Oak.
2. **Límite de equipo activo:** El entrenador puede llevar un máximo de **6 Pokémon activos** en su equipo; cualquier Pokémon adicional capturado se envía automáticamente al almacenamiento del **PC de Bill**.
3. **Combate por turnos y PP:** Las batallas se desarrollan por turnos. Cada ataque consume **Puntos de Poder (PP)** y el daño se calcula según estadísticas base, naturalezas, bonificación por mismo tipo (**STAB**) y efectividad elemental de Gen III (si se agotan todos los PP, el Pokémon usa *Forcejeo* y recibe daño de retroceso).
4. **Debilitamiento y recuperación:** Un Pokémon cuya salud (`PS`) llega a `0` queda debilitado y no puede combatir hasta ser curado con objetos de la mochila o recuperado en un **Centro Pokémon**.
5. **Captura exclusiva de salvajes:** Solo es posible capturar Pokémon salvajes (nunca Pokémon de otros entrenadores) utilizando **Poké Balls** de la mochila; la probabilidad de éxito depende de la salud restante del objetivo, su estado alterado y su ratio de captura.
6. **Economía y persistencia:** El jugador gana pokémonedas (`₽`) al vencer en combate para comprar objetos en la tienda y puede guardar o cargar su partida en cualquier momento desde el menú principal.

---

## ✨ Características Principales

* **Base de Datos Oficial Gen III (151 Pokémon de Kanto):** Estadísticas base, experiencias base (tope 255), ratios de captura, descripciones en español y *learnsets* oficiales por nivel extraídos y adaptados desde PokéAPI.
* **Sistema de Combate Fiel a Gen III:**
  * División clásica de daño **Físico / Especial** según el tipo elemental del ataque.
  * Cálculo oficial de daño con **STAB**, efectividad de tipos (17 tipos), naturalezas (25 naturalezas con ±10%) y variación aleatoria.
  * Gestión de **Puntos de Poder (PP)** por movimiento y activación automática de **Forcejeo** con retroceso al agotar todos los ataques.
  * **Estados alterados y modificadores en combate:** Quemadura, parálisis, envenenamiento, sueño, congelación, confusión y etapas de estadísticas (-6 a +6 en ataque, defensa, velocidad, precisión y evasión).
* **Gestión de Equipo y PC de Bill:** Equipo activo de hasta 6 Pokémon, intercambio de posiciones, almacenamiento en caja del PC y apodos personalizados.
* **Economía, Mochila y Tienda Pokémon:** Sistema de pokémonedas (`₽`), compra de Poké Balls, pociones y piedras evolutivas, además de captura de Pokémon salvajes en 11 rutas de Kanto.
* **Progresión y Evolución:** Subida de nivel, aprendizaje automático de movimientos y evolución por nivel o por objeto.
* **Persistencia Segura en JSON:** Guardado atómico mediante archivos temporales, respaldo automático (`backup`), validación de esquemas y sistema de migraciones de versión.

---

## 🧱 Diseño Orientado a Objetos (POO)

La jerarquía principal de entidades del proyecto aplica herencia, polimorfismo y encapsulamiento:

* **`Pokemon` (abuela):** Define estadísticas, movimientos, salud, estados alterados, recuperación de PP y el comportamiento de turno común.
* **`PokemonCapturable(Pokemon)` (madre):** Agrega rareza y ruta de origen, usando `super()` para exportar y reconstruir los datos heredados.
* **`PokemonSalvaje(PokemonCapturable)` y `PokemonAtrapado(PokemonCapturable)` (nietas):** El Pokémon salvaje puede capturarse; el atrapado conserva entrenador, apodo y su comportamiento de compañero. `PokemonJugador` se mantiene como alias compatible.

### Encapsulamiento en `Pokemon`
* **Público (`+`):** `nivel`, `exp_actual`, `movimientos`, `estado_alterado` y propiedades (`@property`) como `nombre`, `salud_actual` y `salud_maxima`.
* **Protegido (`#`):** `_nombre`, `_tipos`, `_salud_actual`, `_estados` y el método de clase `_restaurar_estado_comun()`.
* **Privado (`-`):** `__naturaleza`, `__exp_siguiente_nivel` y `__estadisticas`.

---

## 📂 Arquitectura del Proyecto

```text
pokemon_frlg/
├── main.py                  # Punto de entrada de la aplicación
├── juego.py                 # Bucle principal y flujo de estados del juego
├── config.py                # Constantes globales, tabla de tipos y reglas Gen III
├── modelos/                 # Entidades POO con encapsulamiento y validaciones
│   ├── pokemon.py           # Clase base Pokemon y subclases (Jugador / Salvaje)
│   ├── movimiento.py        # Clase Movimiento con validación de PP y precisión
│   ├── equipo.py            # Gestión de equipo activo (máx. 6) y PC de Bill
│   ├── mochila.py           # Inventario encapsulado y control de saldo
│   └── objeto.py            # Poké Balls, Pociones y Piedras Evolutivas
├── sistemas/                # Lógica de negocio y reglas del juego
│   ├── combate.py           # Motor de batallas salvajes y contra entrenadores
│   ├── efectos.py           # Estados alterados y modificadores de estadísticas
│   ├── estadisticas.py      # Fórmulas Gen III de stats, naturalezas y tipos
│   ├── experiencia.py       # Cálculo de EXP ganada y subida de nivel
│   ├── evolucion.py         # Evolución por nivel y por objetos
│   └── captura.py           # Fórmula oficial de captura con Poké Balls
├── servicios/               # Integración con API y acceso a datos
│   ├── pokeapi.py           # Cliente HTTP con reintentos y ajuste histórico Gen III
│   ├── descargar_datos.py   # Generador de los catálogos JSON locales
│   ├── repositorio.py       # Carga en memoria de Pokémon y movimientos
│   └── nueva_partida.py     # Flujo inicial con el Profesor Oak
├── persistencia/            # Almacenamiento seguro en disco
│   ├── guardado.py          # Guardado atómico en JSON y recuperación de respaldo
│   ├── migraciones.py       # Actualización automática de versiones de partida
│   └── validacion.py        # Verificación de integridad de archivos guardados
├── interfaz/                # Capa de presentación en consola
│   ├── menus.py             # Menús interactivos (Rutas, Pueblo, PC, Tienda)
│   ├── demo_entrega1.py     # Menú académico reducido de demostración POO
│   ├── pokedex_ui.py        # Ficha técnica paginada de cada Pokémon
│   └── mensajes.py          # Efectos de texto y alineación exacta con emojis
├── datos/                   # Bases de datos generadas en formato JSON
│   ├── pokemon_gen3.json
│   └── movimientos_gen3.json
├── tests/                   # Pruebas automatizadas con assert
│   ├── test_basicos.py
│   └── test_entrega1.py
├── README.md                # Documentación principal del proyecto
└── AVANCES.md               # Bitácora de sprints, arquitectura y evolución
```

---

## 🚀 Cómo Ejecutar el Juego

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Samux2208/Juego-de-Pokemon-en-Python-Terminal.git
   cd Juego-de-Pokemon-en-Python-Terminal
   ```

2. **Requisitos:** Python **3.10 o superior** (no requiere librerías externas; usa únicamente la biblioteca estándar de Python).

3. **Preparar los datos (solo si faltan los archivos JSON en `datos/`):**
   ```bash
   python -m servicios.descargar_datos
   ```

4. **Inicia la aventura:**
   ```bash
   python main.py
   ```

5. **Ejecuta las pruebas con `assert`:**
   ```bash
   python -m tests.test_entrega2
   ```

## 🏆 Reglas para ganar o perder

* **Victoria:** Desde el menú principal (opción 7) o el menú del pueblo (opción 5), desafía a Brock en el Gimnasio Plateada. Al vencerlo obtienes la **Medalla Roca**, aparece el mensaje **🏆 ¡VICTORIA! Has completado el desafío de Kanto** y la partida concluye.
* **Derrota:** Si todo el equipo activo y el PC quedan sin Pokémon conscientes y no tienes Revivir, el juego anuncia **💀 DERROTA**. Perder el combate contra Brock también declara derrota y concluye la partida.

---

## 👥 Autores y Colaboradores

Este proyecto fue realizado en equipo por:

* **Samuel Alberto Castañeda Barros** — [@Samux2208](https://github.com/Samux2208)
* **Adrian Fernando Caicedo Cejia** — [@anADRIAN18](https://github.com/anADRIAN18)