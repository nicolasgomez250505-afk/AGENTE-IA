from agente import (
    decidir_herramienta,
    detectar_componente,
    ensenar_componente,
    generar_arquitectura,
    validar_arquitectura,
    corregir_arquitectura,
    integrar_arquitectura,
    normalizar_componentes
)
 
from modelo_ia import preguntar_ia
 
from memoria_agente import (
    guardar_interaccion,
    construir_contexto,
    detectar_proyecto
)
 
from estado_proyecto import (
    actualizar_estado_desde_solicitud,
    construir_resumen_proyecto
)
 
 
 
def construir_contexto_completo():
    """Une el estado estructurado del proyecto con el historial reciente."""
    resumen_proyecto = construir_resumen_proyecto()
    contexto_conversacion = construir_contexto()
 
    contexto_completo = (
        resumen_proyecto
        + "\n\nHISTORIAL RECIENTE\n"
        + "=================\n"
        + contexto_conversacion
    )
 
    return contexto_completo
 
 
def crear_resultado(
    solicitud,
    herramienta,
    origen,
    respuesta,
    requiere_componentes=False
):
    """Crea el resultado estándar y guarda la interacción en memoria."""
    guardar_interaccion(
        solicitud,
        respuesta
    )
 
    return {
        "herramienta": herramienta,
        "origen": origen,
        "requiere_componentes": requiere_componentes,
        "respuesta": respuesta
    }
 
 
def ejecutar_agente(
    solicitud,
    entrada_componentes=None
):
    """Coordina la solicitud y utiliza reglas, herramientas o Gemini."""
    if solicitud.strip() == "":
        return {
            "herramienta": "ninguna",
            "origen": "python",
            "requiere_componentes": False,
            "respuesta": "Debes escribir una solicitud."
        }
 
    detectar_proyecto(
        solicitud
    )
 
    actualizar_estado_desde_solicitud(
        solicitud
    )
 
    herramienta = decidir_herramienta(
        solicitud
    )
 
    if herramienta == "ensenar":
        componente = detectar_componente(
            solicitud
        )
 
        if componente:
            respuesta = ensenar_componente(
                componente
            )
 
            return crear_resultado(
                solicitud,
                "ensenar",
                "python",
                respuesta
            )
 
        contexto = construir_contexto_completo()
 
        respuesta = preguntar_ia(
            solicitud,
            contexto
        )
 
        return crear_resultado(
            solicitud,
            "ensenar",
            "gemini",
            respuesta
        )
 
    elif herramienta == "generar":
        respuesta = generar_arquitectura(
            solicitud
        )
 
        return crear_resultado(
            solicitud,
            "generar",
            "python",
            respuesta
        )
 
    elif herramienta == "validar":
        if (
            entrada_componentes is None
            or entrada_componentes.strip() == ""
        ):
            return {
                "herramienta": "validar",
                "origen": "python",
                "requiere_componentes": True,
                "respuesta": (
                    "Para validar necesito conocer "
                    "los componentes actuales del proyecto."
                )
            }
 
        componentes = normalizar_componentes(
            entrada_componentes
        )
 
        respuesta = validar_arquitectura(
            componentes
        )
 
        return crear_resultado(
            solicitud,
            "validar",
            "python",
            respuesta
        )
 
    elif herramienta == "corregir":
        if (
            entrada_componentes is None
            or entrada_componentes.strip() == ""
        ):
            return {
                "herramienta": "corregir",
                "origen": "python",
                "requiere_componentes": True,
                "respuesta": (
                    "Para corregir necesito conocer "
                    "los componentes actuales del proyecto."
                )
            }
 
        componentes = normalizar_componentes(
            entrada_componentes
        )
 
        respuesta = corregir_arquitectura(
            componentes
        )
 
        return crear_resultado(
            solicitud,
            "corregir",
            "python",
            respuesta
        )
 
    elif herramienta == "integrar":
        respuesta = integrar_arquitectura(
            solicitud
        )
 
        return crear_resultado(
            solicitud,
            "integrar",
            "python",
            respuesta
        )
 
    else:
        contexto = construir_contexto_completo()
 
        respuesta = preguntar_ia(
            solicitud,
            contexto
        )
 
        return crear_resultado(
            solicitud,
            "ia",
            "gemini",
            respuesta
        )
