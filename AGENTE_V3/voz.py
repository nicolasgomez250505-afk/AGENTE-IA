"""Funciones de voz del Agente Arquitecto Digital.

- transcribir_audio(): convierte un audio WAV en texto (escuchar).
- limpiar_para_voz(): quita símbolos que sonarían raro al leer en voz alta.
- html_voz(): crea el reproductor que habla dentro del navegador (hablar).
"""

from __future__ import annotations

import io
import json
import re

import speech_recognition as sr


IDIOMA = "es-CO"


def transcribir_audio(audio_bytes: bytes) -> tuple[str, str]:
    """Convierte audio WAV en texto.

    Parámetros:
        audio_bytes: contenido del audio grabado.

    Retorna:
        Una pareja (texto, error). Si todo sale bien, error es "".
    """
    reconocedor = sr.Recognizer()

    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as fuente:
            audio = reconocedor.record(fuente)

        texto = reconocedor.recognize_google(
            audio,
            language=IDIOMA,
        )

        return str(texto).strip(), ""

    except sr.UnknownValueError:
        return "", (
            "No pude entender el audio. Intenta hablar "
            "más cerca del micrófono y más despacio."
        )

    except sr.RequestError:
        return "", (
            "No pude conectar con el servicio de "
            "reconocimiento de voz. Revisa tu conexión a internet."
        )

    except Exception as error:
        return "", f"No se pudo leer el audio: {error}"


def limpiar_para_voz(texto: str) -> str:
    """Quita símbolos de formato para que la lectura suene natural."""
    limpio = re.sub(r"[`*#_>|=~-]{2,}", " ", texto)
    limpio = re.sub(r"[`*#_>|]", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio)

    return limpio.strip()


PLANTILLA_HTML = """
<div style="font-family: sans-serif; display: flex;
            gap: 8px; align-items: center;">
  <button id="hablar" style="padding: 6px 12px; cursor: pointer;">
    🔊 Escuchar respuesta
  </button>
  <button id="parar" style="padding: 6px 12px; cursor: pointer;">
    ⏹️ Detener
  </button>
  <span id="estado" style="font-size: 0.85rem; color: #666;"></span>
</div>

<script>
  const texto = __TEXTO__;
  const automatico = __AUTOMATICO__;
  const estado = document.getElementById("estado");

  function hablar() {
    if (!("speechSynthesis" in window)) {
      estado.textContent = "Tu navegador no permite leer en voz alta.";
      return;
    }

    window.speechSynthesis.cancel();

    const lectura = new SpeechSynthesisUtterance(texto);
    lectura.lang = "es-CO";
    lectura.onstart = () => { estado.textContent = "Leyendo..."; };
    lectura.onend = () => { estado.textContent = ""; };

    window.speechSynthesis.speak(lectura);
  }

  function detener() {
    window.speechSynthesis.cancel();
    estado.textContent = "";
  }

  document.getElementById("hablar").addEventListener("click", hablar);
  document.getElementById("parar").addEventListener("click", detener);

  if (automatico) {
    setTimeout(hablar, 400);
  }
</script>
"""


def html_voz(texto: str, leer_automaticamente: bool = True) -> str:
    """Crea el HTML con botones para escuchar la respuesta.

    El texto se convierte con json.dumps para que sea un dato seguro
    dentro del JavaScript y no se interprete como código.
    """
    texto_seguro = json.dumps(
        texto,
        ensure_ascii=False,
    ).replace("<", "\\u003c")

    automatico = "true" if leer_automaticamente else "false"

    return (
        PLANTILLA_HTML
        .replace("__TEXTO__", texto_seguro)
        .replace("__AUTOMATICO__", automatico)
    )