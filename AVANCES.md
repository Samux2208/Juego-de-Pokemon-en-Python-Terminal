# 🚀 AVANCES — Pokémon RPG de Kanto (Edición Terminal)
### **Pokémon Consola Adventure (Gen III - FRLG)** 🎮⚡

> **Repositorio Oficial:** [Juego-de-Pokemon-en-Python-Terminal](https://github.com/Samux2208/Juego-de-Pokemon-en-Python-Terminal)  
> **Desarrolladores:** `Samux2208` & `Adrian Fernando Caicedo`  
> **Estado Actual:** 🟢 En desarrollo activo (Arquitectura Modular Gen III + Integración con PokéAPI)

---

## 📊 Resumen de Evolución del Proyecto

| Sprint / Fase | Periodo | Enfoque Principal | Estado |
| :--- | :--- | :--- | :--- |
| **Sprint 1 — Definición y Estructura** | 07 Nov – 11 Nov 2026 | Prototipo inicial basado en tutorial, definición de reglas y arquitectura modular POO. | ✅ Completado |
| **Sprint 2 — Diseño POO, PokéAPI y Menú** | 12 Nov – 18 Nov 2026 | Integración de datos desde PokéAPI (5 días), encapsulamiento, herencia y menús en consola. | ✅ Completado |
| **Entrega 1 y Próximos Pasos** | En curso | Pruebas unitarias, revisión de diagrama de clases y preparación para Entrega 2. | 🔄 En progreso |

---

## 🛠️ Sprint 1 — Definición y estructura (07 Nov – 11 Nov 2026)

### Qué hicimos
* **Punto de partida y transición:** Comenzamos tomando como referencia un video tutorial de YouTube sobre POO básica en Python, aprendiendo a usar `sys` y `time` para simular texto con retraso en la consola (`Demo1 jugable`, commit `fabee4b`). Sin embargo, los métodos del tutorial eran muy limitados, por lo que descartamos la mayor parte y reestructuramos todo desde cero (`Versión 2 POO`, commit `25e9b84`).
* **Definición del juego:** Establecimos el proyecto como un RPG de Pokémon ambientado en la región de Kanto ejecutado íntegramente desde la terminal, cuyo objetivo es formar un equipo, explorar rutas, capturar, entrenar y evolucionar criaturas.
* **Arquitectura por responsabilidades:** Dividimos el proyecto en módulos claros (`modelos`, `sistemas`, `servicios`, `interfaz`, `mundo`, `persistencia` y `tests`), logrando una refactorización modular completa estilo Gen III FRLG (commit `696662f`).
* **Jerarquía de clases:** Identificamos `Pokemon` como clase madre y diseñamos `PokemonJugador` y `PokemonSalvaje` como clases hijas, además de la composición con `Equipo`.

### Quién hizo qué
* **Samux2208 / Adrian Fernando Caicedo:** Configuración inicial del repositorio (`F744EE7`), implementación de la base en `game.py` (`30ba1a9`), reestructuración a POO v2 (`25e9b84`), refactorización modular Gen III (`696662f`) y actualización de guardado (`92365c5`).
* **[Nombre del integrante 2]:** [Actividad realizada y archivo trabajado, ej. diseño de menús o pruebas].
* **[Nombre del integrante 3]:** [Actividad realizada y archivo trabajado, ej. diagramas o documentación].

---

## ⚙️ Sprint 2 — Diseño POO, PokéAPI y primer menú (12 Nov – 18 Nov 2026)

### Qué hicimos
* **Extracción y limpieza de datos con PokéAPI:** Entre el 12 y el 18 de noviembre invertimos cerca de **5 días** desarrollando `servicios/descargar_datos.py` para extraer la información real de Pokémon y movimientos desde **PokéAPI** hacia `datos/pokemon_gen3.json` y `datos/movimientos_gen3.json`, evitando la carga manual.
* **Herencia y polimorfismo:** Implementamos `PokemonJugador(Pokemon)` y `PokemonSalvaje(Pokemon)`. Los constructores de ambas clases hijas invocan `super().__init__()` y validan sus atributos propios (entrenador/apodo vs. rareza/ruta).
* **Encapsulamiento y propiedades:** Aplicamos visibilidad pública (`+`), protegida (`_nombre`, `_tipos`, `_salud_actual`, `_estados`) y privada (`__naturaleza`, `__exp_siguiente_nivel`, `__estadisticas`). Incorporamos decoradores `@property` para consultar estadísticas calculadas sin exponer los datos internos.
* **Persistencia:** Creamos el método protegido heredado `_restaurar_estado_comun()` en la clase madre para que las hijas reconstruyan su estado al cargar una partida guardada.
* **Interfaz y pruebas:** Construimos el menú principal del RPG y la opción independiente **Demostración POO I** (jugar un turno, ver estado y salir) para la evaluación académica, respaldado por pruebas con `assert` en `tests/test_basicos.py` y `tests/test_entrega1.py`.

### Quién hizo qué
* **Samux2208 / Adrian Fernando Caicedo:** Integración y depuración del script de descarga con PokéAPI, implementación de herencia/encapsulamiento en `modelos/pokemon.py` y actualización de `README.md` (`e6e67bb`, `9034bac`).
* **[Nombre del integrante 2]:** [Actividad realizada y archivo trabajado].
* **[Nombre del integrante 3]:** [Actividad realizada y archivo trabajado].

---

## ⚠️ Qué falló (Errores encontrados y correcciones)

Durante el desarrollo enfrentamos varios retos técnicos que resolvimos mediante depuración iterativa:

* **Fallas en la descarga y filtrado de la PokéAPI:** Al conectar con la API, la extracción inicial fallaba y resultaba muy complejo filtrar únicamente los datos necesarios de la Tercera Generación (stats base, tipos, evoluciones y movimientos). Se solucionó estructurando un script dedicado (`servicios/descargar_datos.py`) que limpia y guarda los diccionarios en formato JSON local.
* **Exceso de métodos y errores de indentación (tabs vs. espacios):** Al crecer el proyecto con múltiples archivos, métodos y funciones interconectadas, surgieron fallos de ejecución por problemas de indentación (`IndentationError`) y referencias cruzadas entre módulos que se fueron depurando paso a paso.
* **Ajuste visual en la terminal a prueba y error:** Lograr que los textos con retraso (`sys`/`time`), menús y barras de estado se vieran ordenados en la consola requirió constantes pruebas y ajustes manuales hasta conseguir una visualización limpia.
* **Bug en el listado del PC (`interfaz/menus.py`):** El recorrido de Pokémon almacenados utilizaba una variable (`p`) que no coincidía con la variable del bucle (`pokemon`). Se corrigió la referencia y se añadió el cálculo del indicador de estado de cada criatura.
* **Separación del menú académico:** Se detectó que la demostración rápida de tres opciones podía alterar el flujo o los datos de una partida normal, por lo que se aisló en `interfaz/demo_entrega1.py` sin afectar el guardado principal.

---

## 🔭 Qué sigue

### Lista de verificación antes de la entrega
- [ ] Confirmar que `datos/pokemon_gen3.json` y `datos/movimientos_gen3.json` estén actualizados dentro del repositorio.
- [ ] Ejecutar `python main.py` en el equipo donde se realizará la sustentación para validar tiempos y visualización en terminal.
- [ ] Ejecutar `python -m tests.test_basicos` y `python -m tests.test_entrega1` verificando que todos los `assert` pasen sin errores.
- [ ] Abrir `DIAGRAMA_CLASES_ENTREGA1.drawio` en diagrams.net para comprobar que las relaciones de herencia y composición estén bien trazadas.
- [ ] Completar los nombres y aportes exactos de todos los integrantes en este documento.

### Próximos desarrollos (Entrega 2)
* **Ensayo de demostración:** Preparar la presentación de dos minutos y las explicaciones técnicas sobre herencia, `super()`, encapsulamiento y `@property`.
* **Expansión de mecánicas:** Continuar con los requisitos de la Entrega 2 (nuevos eventos de combate, evolución en partida y mejoras en la exploración de rutas) manteniendo intacta la arquitectura modular actual.