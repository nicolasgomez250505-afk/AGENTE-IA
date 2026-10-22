from google import genai
 
from prompt_sistema import PROMPT_SISTEMA
 
cliente = genai.Client()
 
 
def preguntar_ia(pregunta, contexto=""):
    """Envía una solicitud a Gemini usando identidad y contexto.
 
    Parámetros:
        pregunta: solicitud actual del usuario.
        contexto: información previa que puede ayudar a responder.
 
    Retorna:
        El texto generado por Gemini.
    """
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
