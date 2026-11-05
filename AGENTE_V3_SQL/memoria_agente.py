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
 
 
def detectar_proyecto(solicitud):
    """Detecta si el usuario está definiendo un proyecto y guarda su nombre.
 
    Parámetros:
        solicitud: texto escrito por el usuario.
 
    Retorna:
        El nombre detectado o None.
    """
    texto = solicitud.strip()
    texto_minuscula = texto.lower()
 
    expresiones = [
        "estoy desarrollando ",
        "estoy diseñando ",
        "estoy construyendo ",
        "estoy creando ",
        "mi proyecto es ",
        "mi proyecto consiste en "
    ]
 
    for expresion in expresiones:
        if expresion in texto_minuscula:
            posicion = texto_minuscula.find(
                expresion
            )
 
            proyecto = texto[
                posicion + len(expresion):
            ]
 
            cortes = [
                " para ",
                " que permita ",
                " que permite ",
                ".",
                ","
            ]
 
            proyecto_minuscula = proyecto.lower()
 
            for corte in cortes:
                if corte in proyecto_minuscula:
                    posicion_corte = (
                        proyecto_minuscula.find(corte)
                    )
 
                    proyecto = proyecto[
                        :posicion_corte
                    ]
 
                    break
 
            proyecto = proyecto.strip()
 
            if proyecto.lower().startswith("un "):
                proyecto = proyecto[3:]
 
            elif proyecto.lower().startswith("una "):
                proyecto = proyecto[4:]
 
            if proyecto != "":
                guardar_proyecto(proyecto)
                return proyecto
 
    return None
 
 
def construir_contexto(limite=5):
    """Construye contexto con proyecto actual e historial reciente."""
    historial = memoria["historial"]
    proyecto_actual = memoria["proyecto_actual"]
    contexto = ""
 
    if proyecto_actual:
        contexto += (
            "\nPROYECTO ACTUAL:\n"
            + proyecto_actual
            + "\n"
        )
 
    if not historial:
        if contexto != "":
            return contexto
 
        return "No existen conversaciones anteriores."
 
    interacciones_recientes = historial[-limite:]
 
    for interaccion in interacciones_recientes:
        contexto += (
            "\nUsuario: "
            + interaccion["solicitud"]
            + "\nAgente: "
            + str(interaccion["respuesta"])
            + "\n"
        )
 
    return contexto
