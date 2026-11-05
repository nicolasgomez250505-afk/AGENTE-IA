def analizar_proyecto(nombre_proyecto):
    """Crea la estructura inicial de un proyecto de arquitectura digital.
 
    Parámetros:
        nombre_proyecto: nombre escrito por el usuario.
 
    Retorna:
        Un diccionario con el nombre del proyecto y cinco dominios vacíos.
    """
    proyecto = {
        "proyecto": nombre_proyecto,
        "base de datos": [],
        "ciberseguridad": [],
        "web": [],
        "movil": [],
        "integracion": []
    }
 
    return proyecto
 
 
 
def generar_arquitectura(nombre_proyecto):
    """Genera una propuesta básica de arquitectura para un proyecto.
 
    Parámetros:
        nombre_proyecto: nombre del sistema que se desea diseñar.
 
    Retorna:
        Un texto con los cinco componentes principales y un flujo general.
    """
    arquitectura = "\n".join([
        f"ARQUITECTURA PROPUESTA: {nombre_proyecto}",
        "========================================",
        "",
        "1. BASE DE DATOS",
        "   Almacena y organiza la información del sistema.",
        "",
        "2. CIBERSEGURIDAD",
        "   Protege usuarios, datos y servicios.",
        "",
        "3. APLICACIÓN WEB",
        "   Permite acceder al sistema desde un navegador.",
        "",
        "4. APLICACIÓN MÓVIL",
        "   Permite utilizar el sistema desde dispositivos móviles.",
        "",
        "5. INTEGRACIÓN",
        "   Permite comunicar los diferentes componentes.",
        "",
        "FLUJO GENERAL",
        "=============",
        "WEB / MÓVIL -> API -> BACKEND -> BASE DE DATOS",
        "Ciberseguridad: transversal a toda la solución."
    ])
 
    return arquitectura
 
 
 
def ensenar_componente(componente):
    """Explica de forma breve un componente de arquitectura.
 
    Parámetros:
        componente: nombre del componente que se desea estudiar.
 
    Retorna:
        Una explicación textual del componente o un mensaje de error.
    """
    explicaciones = {
        "base de datos": "\n".join([
            "BASE DE DATOS",
            "",
            "Permite almacenar y organizar la información del sistema.",
            "Ejemplos: usuarios, productos, préstamos, citas o pedidos."
        ]),
        "ciberseguridad": "\n".join([
            "CIBERSEGURIDAD",
            "",
            "Busca proteger los sistemas, usuarios y datos.",
            "",
            "Algunos elementos importantes son:",
            "- autenticación",
            "- autorización",
            "- protección de información",
            "- control de accesos",
            "- registro de eventos",
            "",
            "La seguridad debe considerarse durante todo el desarrollo del sistema."
        ]),
        "web": "\n".join([
            "APLICACIÓN WEB",
            "",
            "Es la parte del sistema a la que se accede desde un navegador.",
            "Puede incluir formularios, paneles, consultas y reportes."
        ]),
        "movil": "\n".join([
            "APLICACIÓN MÓVIL",
            "",
            "Permite acceder al sistema desde un dispositivo móvil.",
            "Normalmente se comunica con el backend mediante una API."
        ]),
        "integracion": "\n".join([
            "INTEGRACIÓN",
            "",
            "Permite que los componentes intercambien información.",
            "Un mecanismo frecuente de integración es una API."
        ])
    }
 
    return explicaciones.get(
        componente,
        "Componente no reconocido."
    )
 
 
 
COMPONENTES_REQUERIDOS = [
    "base de datos",
    "ciberseguridad",
    "web",
    "movil",
    "integracion"
]
 
 
def normalizar_componentes(texto):
    """Convierte una lista escrita por el usuario a nombres estándar.
 
    Parámetros:
        texto: componentes separados por comas.
 
    Retorna:
        Una lista limpia y normalizada.
    """
    alias = {
        "bd": "base de datos",
        "base datos": "base de datos",
        "bases de datos": "base de datos",
        "seguridad": "ciberseguridad",
        "móvil": "movil",
        "aplicacion movil": "movil",
        "aplicación móvil": "movil",
        "integración": "integracion"
    }
 
    componentes = []
 
    for elemento in texto.split(","):
        limpio = elemento.strip().lower()
 
        if limpio == "":
            continue
 
        limpio = alias.get(limpio, limpio)
 
        if limpio not in componentes:
            componentes.append(limpio)
 
    return componentes
 
 
 
def validar_arquitectura(componentes_proyecto):
    """Comprueba si el proyecto contiene los cinco componentes requeridos.
 
    Parámetros:
        componentes_proyecto: lista normalizada de componentes.
 
    Retorna:
        Un mensaje de validación o la lista de componentes faltantes.
    """
    if not componentes_proyecto:
        return "No se recibieron componentes para validar."
 
    faltantes = [
        componente
        for componente in COMPONENTES_REQUERIDOS
        if componente not in componentes_proyecto
    ]
 
    if not faltantes:
        return "Arquitectura válida: contiene todos los componentes requeridos."
 
    return "Faltan los siguientes componentes: " + ", ".join(faltantes)
 
 
 
def corregir_arquitectura(componentes_proyecto):
    """Propone correcciones para los componentes que faltan en la arquitectura.
 
    Parámetros:
        componentes_proyecto: lista normalizada de componentes.
 
    Retorna:
        Recomendaciones concretas para completar la arquitectura.
    """
    if not componentes_proyecto:
        return "No se recibieron componentes para corregir."
 
    recomendaciones = {
        "base de datos": "Agregar una base de datos para almacenar la información.",
        "ciberseguridad": "Agregar controles de autenticación, autorización y protección de datos.",
        "web": "Agregar una interfaz web cuando el sistema requiera acceso desde navegador.",
        "movil": "Agregar una aplicación móvil cuando se requiera acceso desde dispositivos móviles.",
        "integracion": "Agregar una API o mecanismo de integración entre los componentes."
    }
 
    faltantes = [
        componente
        for componente in COMPONENTES_REQUERIDOS
        if componente not in componentes_proyecto
    ]
 
    if not faltantes:
        return "No se requieren correcciones: la arquitectura está completa."
 
    lineas = ["RECOMENDACIONES DE CORRECCIÓN"]
 
    for componente in faltantes:
        lineas.append(f"- {componente}: {recomendaciones[componente]}")
 
    return "\n".join(lineas)

def integrar_arquitectura(nombre_proyecto):
    """Muestra cómo se conectan los componentes principales del proyecto.
 
    Parámetros:
        nombre_proyecto: nombre del sistema que se desea integrar.
 
    Retorna:
        Un texto con el flujo general de integración.
    """
    return "\n".join([
        f"INTEGRACIÓN DEL PROYECTO: {nombre_proyecto}",
        "========================================",
        "",
        "WEB / MÓVIL",
        "     |",
        "     v",
        "    API",
        "     |",
        "     v",
        "  BACKEND",
        "     |",
        "     v",
        "BASE DE DATOS",
        "",
        "CIBERSEGURIDAD: transversal a toda la solución."
    ])

def decidir_herramienta(solicitud):
    """Decide qué capacidad debe utilizar el agente.
 
    Parámetros:
        solicitud: texto escrito por el usuario.
 
    Retorna:
        El nombre de la herramienta seleccionada.
    """
    texto = solicitud.lower()
 
    if (
        "qué sabes de mi proyecto" in texto
        or "que sabes de mi proyecto" in texto
        or "qué sabes actualmente de mi proyecto" in texto
        or "que sabes actualmente de mi proyecto" in texto
        or "mostrar estado del proyecto" in texto
        or "muestra el estado del proyecto" in texto
        or "resumen del proyecto" in texto
        or "información del proyecto" in texto
        or "informacion del proyecto" in texto
    ):
        return "estado"
 
    elif (
        "enseña" in texto
        or "enseñar" in texto
        or "explica" in texto
        or "qué es" in texto
    ):
        return "ensenar"
 
    elif (
        "generar" in texto
        or "crear arquitectura" in texto
        or "diseñar arquitectura" in texto
        or "proponer arquitectura" in texto
    ):
        return "generar"
 
    elif (
        "validar" in texto
        or "verificar" in texto
        or "revisar componentes" in texto
    ):
        return "validar"
 
    elif (
        "corregir" in texto
        or "mejorar arquitectura" in texto
        or "qué falta" in texto
    ):
        return "corregir"
 
    elif (
        "integrar" in texto
        or "conectar componentes" in texto
        or "integración" in texto
    ):
        return "integrar"
 
    else:
        return "ia"

 
 
def detectar_componente(solicitud):
    """Identifica el componente de arquitectura mencionado por el usuario.
 
    Parámetros:
        solicitud: texto escrito por el usuario.
 
    Retorna:
        El nombre normalizado del componente o None.
    """
    texto = solicitud.lower()
 
    if (
        "base de datos" in texto
        or "bases de datos" in texto
        or "bd" in texto
    ):
        return "base de datos"
 
    elif (
        "ciberseguridad" in texto
        or "seguridad" in texto
    ):
        return "ciberseguridad"
 
    elif (
        "aplicación web" in texto
        or "aplicacion web" in texto
        or " web" in texto
    ):
        return "web"
 
    elif (
        "aplicación móvil" in texto
        or "aplicacion movil" in texto
        or "móvil" in texto
        or "movil" in texto
    ):
        return "movil"
 
    elif (
        "integración" in texto
        or "integracion" in texto
        or "api" in texto
    ):
        return "integracion"
 
    else:
        return None
