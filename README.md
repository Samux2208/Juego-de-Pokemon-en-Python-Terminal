# 🎮 Pokémon Console Adventure — Edición Rojo Fuego / Verde Hoja (Gen III)

¡Bienvenido! Este es un videojuego de rol (RPG) interactivo desarrollado completamente en **Python** para ejecutarse desde la terminal. El proyecto está ambientado fielmente en las mecánicas clásicas de **Pokémon Rojo Fuego y Verde Hoja (Generación III)** en la región de Kanto.

Diseñado como proyecto de **Ingeniería** para aplicar arquitectura modular, diseño orientado a objetos (POO), encapsulamiento estricto, manejo de excepciones y persistencia segura de datos.

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
│   ├── pokedex_ui.py        # Ficha técnica paginada de cada Pokémon
│   └── mensajes.py          # Efectos de texto y alineación exacta con emojis
└── datos/                   # Bases de datos generadas en formato JSON
    ├── pokemon_gen3.json
    └── movimientos_gen3.json
```

---

## 🚀 Cómo Ejecutar el Juego

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com
   cd Juego-de-Pokemon-en-Python-Terminal
   ```

2. **Requisitos:** Python **3.10 o superior** (no requiere librerías externas; usa únicamente la biblioteca estándar de Python).

3. **Inicia la aventura:**
   ```bash
   python main.py
   ```

*(Opcional) Si deseas regenerar las bases de datos desde PokéAPI:*
```bash
python -m servicios.descargar_datos
```

---

## 👥 Autores y Colaboradores

Este proyecto fue realizado en equipo por:

* **Samuel Alberto Castañeda Barros** — [@Samux2208](https://github.com)
* **Adrian Fernando Caicedo Cejia** — [@anADRIAN18](https://github.com)
