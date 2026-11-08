# 🎮 Pokémon Console Adventure

¡Bienvenido! Este es un videojuego de rol interactivo desarrollado completamente en **Python** para ejecutarse desde la terminal. El proyecto fue diseñado y programado como parte de nuestro aprendizaje en el **segundo semestre de la carrera de Ingeniería**.

El objetivo del proyecto fue aplicar conceptos sólidos de programación estructurada, control de flujo y los pilares iniciales de la Programación Orientada a Objetos (POO).

---

## 👥 Autores y Colaboradores
Este proyecto fue realizado en equipo por:
* **Samuel Alberto Castañeda Barros** - [@Samux2208](https://github.com/Samux2208)
* **Adrian Fernando Caicedo Cejia** - [@usuario_github_compañero](https://github.com)

---

## 🛠️ Características Técnicas del Código
Para el desarrollo de este juego implementamos:
* **Programación Orientada a Objetos (POO):** Uso de clases (`Pokemon`) y encapsulamiento mediante atributos privados (`__ataque`, `__defensa`) y propiedades dinámicas (`@property`) para la gestión de barras de salud y experiencia.
* **Persistencia de Datos:** Implementación del módulo nativo `pickle` para guardar y cargar el estado de la partida de forma binaria (`partida_pokemon.dat`).
* **Control de Flujo Avanzado:** Uso de estructuras `match-case` (disponibles desde Python 3.10) para el manejo de rutas y menús anidados.
* **Interfaz de Consola Fluida:** Control de tiempos con el módulo `time` y simulación de escritura en tiempo real con `sys.stdout.flush`.

---

## 🚀 Cómo Ejecutar el Juego

### Requisitos previos
* Tener instalado **Python 3.10** o superior.

### Pasos para jugar
1. Clona o descarga este repositorio en tu computadora.
2. Abre tu terminal o línea de comandos en la carpeta donde guardaste el archivo.
3. Ejecuta el juego con el siguiente comando:

```bash
game.py
```

---

## 🧠 Aprendizajes Clave
* Trabajo en equipo y control de versiones.
* Manejo de la lógica de combate matemática (fórmulas basadas en estadísticas base y niveles).
* Gestión de errores en lectura de archivos externos.
