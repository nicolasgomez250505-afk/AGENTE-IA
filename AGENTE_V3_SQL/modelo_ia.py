
import os
from google import genai

from prompt_sistema import PROMPT_SISTEMA


def obtener_cliente():
    """
    Obtiene la clave de Gemini desde los secretos de Streamlit
    o desde las variables de entorno del sistema.
    """

    api_key = None

    # Primero intenta obtener la clave desde Streamlit.
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

    # Si no está en Streamlit, intenta obtenerla del sistema.
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    # Si existe una clave, la utiliza para crear el cliente.
    if api_key:
        return genai.Client(api_key=api_key)

    # Si no existe, conserva el comportamiento local anterior.
    return genai.Client()


cliente = obtener_cliente()


def preguntar_ia(pregunta, contexto=""):
    """Envía una solicitud a Gemini usando identidad y contexto."""

    mensaje = f"""
{PROMPT_SISTEMA}

CONTEXTO DE LA CONVERSACIÓN:

{contexto}

SOLICITUD ACTUAL DEL USUARIO:

{pregunta}

INSTRUCCIÓN IMPORTANTE:

Utiliza el contexto anterior solamente cuando sea relevante.
No inventes información que no aparezca en el contexto
o en la solicitud del usuario.
"""

    respuesta = cliente.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=mensaje
    )

    return respuesta.text
