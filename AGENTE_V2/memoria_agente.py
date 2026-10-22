import json
import os
 
 
RUTA_MEMORIA = os.path.join(
    os.path.dirname(__file__),
    "memoria.json"
)
 
 
MEMORIA_INICIAL = {
    "proyecto_actual": None,
    "historial": []
}
 
 
def cargar_memoria():
    """Carga la memoria desde memoria.json o crea una memoria inicial."""
    if os.path.exists(RUTA_MEMORIA):
        try:
            with open(
                RUTA_MEMORIA,
                "r",
                encoding="utf-8"
            ) as archivo:
                return json.load(archivo)
 
        except (
            json.JSONDecodeError,
            OSError
        ):
            return MEMORIA_INICIAL.copy()
 
    return MEMORIA_INICIAL.copy()
 
 
memoria = cargar_memoria()
 
 
def guardar_memoria():
    """Guarda el contenido actual de memoria en memoria.json."""
    with open(
        RUTA_MEMORIA,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            memoria,
            archivo,
            ensure_ascii=False,
            indent=4
        )
 
 
def guardar_proyecto(nombre_proyecto):
    """Guarda el nombre del proyecto actual y persiste el cambio."""
    memoria["proyecto_actual"] = nombre_proyecto
    guardar_memoria()
 
 
def obtener_proyecto():
    """Devuelve el nombre del proyecto actual."""
    return memoria["proyecto_actual"]
 
 
def guardar_interaccion(solicitud, respuesta):
    """Guarda una interacción y actualiza memoria.json."""
    interaccion = {
        "solicitud": solicitud,
        "respuesta": respuesta
    }
 
    memoria["historial"].append(interaccion)
    guardar_memoria()
 
 
def obtener_historial():
    """Devuelve el historial completo."""
    return memoria["historial"]
 
 
def construir_contexto(limite=5):
    """Convierte las últimas interacciones en contexto de texto."""
    historial = memoria["historial"]
 
    if not historial:
        return "No existen conversaciones anteriores."
 
    interacciones_recientes = historial[-limite:]
    contexto = ""
 
    for interaccion in interacciones_recientes:
        contexto += (
            "\nUsuario: "
            + interaccion["solicitud"]
            + "\nAgente: "
            + str(interaccion["respuesta"])
            + "\n"
        )
 
    return contexto
