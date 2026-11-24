from config import INICIALES
from mundo.rutas import RUTAS

# ==  CONSULTA DE DATOS ==========================
# describir_disponibilidad() | Indica en qué rutas o eventos se obtiene un Pokémon.
# ============================================================

def describir_disponibilidad(nombre):
    '''Devuelve un texto de Pokédex indicando dónde encontrar la especie.'''    
    # Comprobamos si el Pokémon es un inicial usando el método .values()
    if nombre in INICIALES.values():
        return "Pokémon inicial entregado por el profesor al comenzar la aventura."
        
    # Buscamos todas las rutas en cuyo pool aparezca este Pokémon
    rutas = [ruta["nombre"] for ruta in RUTAS if nombre in ruta["pool"]]
            
    # Evaluamos el resultado de las rutas encontradas
    if rutas:
        # Unimos los nombres de las rutas con comas usando .join()
        return "Se encuentra en: " + ", ".join(rutas) + "."
        
    # Si la lista quedó vacía, significa que es un Pokémon especial o evolución
    return "No aparece en rutas salvajes (evolución o Pokémon especial)."