'''Generador de catálogos JSON locales para Pokémon Rojo Fuego / Verde Hoja.

Coordina la descarga desde PokéAPI, traduce las referencias de movimientos
a nombres en español y guarda `pokemon_gen3.json` y `movimientos_gen3.json`
en la carpeta `datos/`.
'''

import json
from config import DATOS_DIR
from servicios.pokeapi import descargar_movimientos, descargar_pokemon_kanto


def ejecutar_descarga() -> None:
    '''Descarga los datos de Kanto y movimientos Gen III y genera los JSON.'''
    DATOS_DIR.mkdir(exist_ok=True)

    print("Iniciando descarga de Kanto (151 Pokémon - Gen 3 Rojo Fuego / Verde Hoja)...")
    pokedex, urls_movs = descargar_pokemon_kanto(151)
    movimientos, mapa_urls = descargar_movimientos(urls_movs)

    # Reemplaza las URLs de movimientos por sus nombres en español y arma el learnset
    for poke in pokedex.values():
        movs_en = [
            mapa_urls[url]
            for url in poke.pop("movimientos_url", [])
            if url in mapa_urls
        ]
        poke["movimientos"] = list(dict.fromkeys(movs_en))

        poke["learnset"] = [
            {"nivel": lvl, "movimiento": mapa_urls[url]}
            for lvl, url in poke.pop("movimientos_nivel", [])
            if url in mapa_urls
        ]

    (DATOS_DIR / "movimientos_gen3.json").write_text(
        json.dumps(movimientos, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (DATOS_DIR / "pokemon_gen3.json").write_text(
        json.dumps(pokedex, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("✅ Archivos JSON generados correctamente en /datos con reglas Gen III.")


if __name__ == "__main__":
    ejecutar_descarga()