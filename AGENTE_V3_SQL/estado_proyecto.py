from memoria_agente import (
    memoria,
    guardar_memoria,
    obtener_proyecto
)
 
 
def inicializar_estado_proyecto():
    """Crea la ficha estructurada del proyecto si todavía no existe."""
    if "datos_proyecto" not in memoria:
        memoria["datos_proyecto"] = {
            "nombre": None,
            "tipo": None,
            "componentes": [],
            "tecnologias": [],
            "estado": "en definición"
        }
 
        guardar_memoria()
 
    return memoria["datos_proyecto"]
 
 
def sincronizar_nombre_proyecto():
    """Copia el nombre del proyecto actual a la ficha estructurada."""
    datos = inicializar_estado_proyecto()
    proyecto_actual = obtener_proyecto()
 
    if proyecto_actual:
        datos["nombre"] = proyecto_actual
        guardar_memoria()
 
    return datos
 
 
def registrar_componente(componente):
    """Agrega un componente a la ficha si todavía no está registrado."""
    datos = inicializar_estado_proyecto()
 
    if componente not in datos["componentes"]:
        datos["componentes"].append(componente)
        guardar_memoria()
 
 
def registrar_tecnologia(tecnologia):
    """Agrega una tecnología a la ficha si todavía no está registrada."""
    datos = inicializar_estado_proyecto()
 
    if tecnologia not in datos["tecnologias"]:
        datos["tecnologias"].append(tecnologia)
        guardar_memoria()
 
 
def actualizar_estado_desde_solicitud(solicitud):
    """Extrae componentes, tecnologías, tipo y estado desde una solicitud."""
    datos = sincronizar_nombre_proyecto()
    texto = solicitud.lower()
 
    componentes = {
        "base de datos": [
            "base de datos",
            "bases de datos",
            "bd"
        ],
        "ciberseguridad": [
            "ciberseguridad",
            "seguridad"
        ],
        "web": [
            "aplicación web",
            "aplicacion web",
            "sitio web",
            "página web",
            "pagina web"
        ],
        "movil": [
            "aplicación móvil",
            "aplicacion movil",
            "app móvil",
            "app movil"
        ],
        "integracion": [
            "integración",
            "integracion",
            "api"
        ]
    }
 
    for componente, palabras in componentes.items():
        for palabra in palabras:
            if palabra in texto:
                registrar_componente(componente)
                break
 
    tecnologias = {
        "python": "Python",
        "javascript": "JavaScript",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "sqlite": "SQLite",
        "react": "React",
        "flutter": "Flutter",
        "django": "Django",
        "fastapi": "FastAPI",
        "node.js": "Node.js",
        "spring boot": "Spring Boot"
    }
 
    for palabra, tecnologia in tecnologias.items():
        if palabra in texto:
            registrar_tecnologia(tecnologia)
 
    if (
        "java" in texto
        and "javascript" not in texto
    ):
        registrar_tecnologia("Java")
 
    tipos = {
        "aplicación web": "Aplicación web",
        "aplicacion web": "Aplicación web",
        "aplicación móvil": "Aplicación móvil",
        "aplicacion movil": "Aplicación móvil",
        "sistema de información": "Sistema de información",
        "sistema de informacion": "Sistema de información",
        "plataforma web": "Plataforma web"
    }
 
    for expresion, tipo in tipos.items():
        if expresion in texto:
            datos["tipo"] = tipo
            guardar_memoria()
            break
 
    if "en desarrollo" in texto:
        datos["estado"] = "en desarrollo"
        guardar_memoria()
 
    elif "en pruebas" in texto:
        datos["estado"] = "en pruebas"
        guardar_memoria()
 
    elif (
        "proyecto terminado" in texto
        or "proyecto finalizado" in texto
    ):
        datos["estado"] = "finalizado"
        guardar_memoria()
 
    return datos
 
 
def obtener_estado_proyecto():
    """Devuelve la ficha estructurada del proyecto."""
    return sincronizar_nombre_proyecto()
 
 
def construir_resumen_proyecto():
    """Convierte la ficha del proyecto en un resumen legible."""
    datos = obtener_estado_proyecto()
 
    nombre = datos["nombre"] or "No definido"
    tipo = datos["tipo"] or "No definido"
 
    if datos["componentes"]:
        texto_componentes = ", ".join(
            datos["componentes"]
        )
    else:
        texto_componentes = (
            "Aún no se han identificado componentes."
        )
 
    if datos["tecnologias"]:
        texto_tecnologias = ", ".join(
            datos["tecnologias"]
        )
    else:
        texto_tecnologias = (
            "Aún no se han definido tecnologías."
        )
 
    return "\n".join([
        "FICHA ACTUAL DEL PROYECTO",
        "=========================",
        "",
        f"Nombre: {nombre}",
        f"Tipo de solución: {tipo}",
        f"Componentes: {texto_componentes}",
        f"Tecnologías: {texto_tecnologias}",
        f"Estado: {datos['estado']}"
    ])
