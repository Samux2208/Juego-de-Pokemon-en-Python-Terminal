# ==================================================
# ARCHIVO: servicios/descargar_datos.py
# ==================================================
import json
from config import BASE_DIR
from servicios.pokeapi import descargar_pokemon_kanto, descargar_movimientos

DATOS_DIR = BASE_DIR / "datos"
DATOS_DIR.mkdir(exist_ok=True)


def ejecutar_descarga():
    print("Iniciando descarga de Kanto (151 Pokémon - Gen 3 Rojo Fuego / Verde Hoja)...")
    pokedex, urls_movs = descargar_pokemon_kanto(151)
    movimientos, mapa_urls = descargar_movimientos(urls_movs)

    # Reemplazar URLs por nombres reales en español en movimientos y learnset
    for poke in pokedex.values():
        poke["movimientos"] = [
            mapa_urls[url] for url in poke.pop("movimientos_url", []) if url in mapa_urls
        ]
        poke["learnset"] = [
            {"nivel": lvl, "movimiento": mapa_urls[url]}
            for lvl, url in poke.pop("movimientos_nivel", []) if url in mapa_urls
        ]

    (DATOS_DIR / "movimientos_gen3.json").write_text(
        json.dumps(movimientos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (DATOS_DIR / "pokemon_gen3.json").write_text(
        json.dumps(pokedex, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("✅ Archivos JSON generados correctamente en /datos con reglas Gen III.")


if __name__ == "__main__":
    ejecutar_descarga()