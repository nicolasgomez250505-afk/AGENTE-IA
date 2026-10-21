from google import genai
 
cliente = genai.Client()
 
 
def preguntar_ia(pregunta):
    """Envía una pregunta a Gemini y devuelve la respuesta generada.
 
    Parámetros:
        pregunta: texto escrito por el usuario.
 
    Retorna:
        El texto generado por Gemini.
    """
    respuesta = cliente.models.generate_content(
        model="gemini-3.5-flash-lite",

        contents=pregunta
    )
 
    return respuesta.text
