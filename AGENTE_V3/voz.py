
"""Funciones de voz del Agente Arquitecto Digital.

- transcribir_audio(): convierte audio en texto.
- limpiar_para_voz(): limpia el texto antes de leerlo.
- html_voz(): lee la respuesta con la mejor voz disponible
  en español, priorizando español colombiano y voz masculina.
"""

from __future__ import annotations

import io
import json
import re

import speech_recognition as sr

IDIOMA = "es-CO"


def transcribir_audio(audio_bytes: bytes) -> tuple[str, str]:
    """Convierte un archivo de audio en texto."""
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
        return (
            "",
            "No pude entender el audio. Intenta hablar "
            "más cerca del micrófono y más despacio.",
        )

    except sr.RequestError:
        return (
            "",
            "No pude conectar con el servicio de "
            "reconocimiento de voz. Revisa tu conexión.",
        )

    except Exception as error:
        return "", f"No se pudo leer el audio: {error}"


def limpiar_para_voz(texto: str) -> str:
    """Elimina símbolos que dificultan la lectura en voz alta."""
    limpio = re.sub(r"[`*#_>|=~-]{2,}", " ", texto)
    limpio = re.sub(r"[`*#_>|]", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio)

    return limpio.strip()


PLANTILLA_HTML = """
<div style="
    font-family: sans-serif;
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
">
    <button id="hablar" style="
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
    ">
        🔊 Escuchar respuesta
    </button>

    <button id="parar" style="
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
    ">
        ⏹️ Detener
    </button>

    <span id="estado"
        style="font-size: 0.85rem; color: #cfe3ff;">
    </span>
</div>

<script>
(function () {
    const texto = __TEXTO__;
    const automatico = __AUTOMATICO__;

    const botonHablar = document.getElementById("hablar");
    const botonParar = document.getElementById("parar");
    const estado = document.getElementById("estado");

    let vocesDisponibles = [];
    let solicitudAutomaticaPendiente = automatico;

    function cargarVoces() {
        if (!("speechSynthesis" in window)) {
            estado.textContent =
                "Este navegador no permite leer en voz alta.";
            return;
        }

        vocesDisponibles = window.speechSynthesis.getVoices();
    }

    function seleccionarVoz() {
        cargarVoces();

        if (!vocesDisponibles.length) {
            return null;
        }

        const vocesEspanol = vocesDisponibles.filter(
            voz => voz.lang &&
                voz.lang.toLowerCase().startsWith("es")
        );

        // Primero se buscan voces colombianas cuyos nombres
        // sugieran una voz masculina.
        const nombresMasculinos = [
            "male", "masculino", "jorge", "andres",
            "andrés", "diego", "carlos", "miguel",
            "juan", "pablo"
        ];

        const colombianas = vocesEspanol.filter(
            voz => voz.lang.toLowerCase() === "es-co"
        );

        const colombianaMasculina = colombianas.find(
            voz => nombresMasculinos.some(
                nombre => voz.name.toLowerCase().includes(nombre)
            )
        );

        if (colombianaMasculina) {
            return colombianaMasculina;
        }

        // Si no hay una voz colombiana identificable como masculina,
        // se prioriza cualquier voz colombiana disponible.
        if (colombianas.length) {
            return colombianas[0];
        }

        // Después se intenta con español latinoamericano.
        const latinoamericana = vocesEspanol.find(
            voz => ["es-mx", "es-419", "es-us", "es-ar",
                    "es-cl", "es-pe"].includes(
                voz.lang.toLowerCase()
            )
        );

        if (latinoamericana) {
            return latinoamericana;
        }

        // Última alternativa: cualquier voz en español.
        return vocesEspanol[0] || null;
    }

    function hablar() {
        if (!("speechSynthesis" in window)) {
            estado.textContent =
                "Tu navegador no permite leer en voz alta.";
            return;
        }

        if (!texto.trim()) {
            estado.textContent = "No hay texto para leer.";
            return;
        }

        window.speechSynthesis.cancel();

        const lectura = new SpeechSynthesisUtterance(texto);
        const voz = seleccionarVoz();

        lectura.lang = voz ? voz.lang : "es-CO";

        if (voz) {
            lectura.voice = voz;
        }

        // Velocidad y tono moderados para una lectura conversacional.
        lectura.rate = 0.96;
        lectura.pitch = 0.92;
        lectura.volume = 1;

        lectura.onstart = () => {
            estado.textContent = voz
                ? "Leyendo con la voz: " + voz.name
                : "Leyendo con la voz predeterminada...";
        };

        lectura.onend = () => {
            estado.textContent = "";
        };

        lectura.onerror = () => {
            estado.textContent =
                "No se pudo reproducir la voz.";
        };

        window.speechSynthesis.speak(lectura);
    }

    function detener() {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
        }

        estado.textContent = "";
    }

    botonHablar.addEventListener("click", hablar);
    botonParar.addEventListener("click", detener);

    if ("speechSynthesis" in window) {
        cargarVoces();

        // Algunos navegadores cargan las voces después de abrir
        // la página, por eso se actualiza la lista cuando están listas.
        window.speechSynthesis.addEventListener(
            "voiceschanged",
            function () {
                cargarVoces();

                if (solicitudAutomaticaPendiente) {
                    solicitudAutomaticaPendiente = false;
                    hablar();
                }
            }
        );

        if (automatico) {
            setTimeout(function () {
                if (solicitudAutomaticaPendiente) {
                    solicitudAutomaticaPendiente = false;
                    hablar();
                }
            }, 600);
        }
    }
})();
</script>
"""


def html_voz(
    texto: str,
    leer_automaticamente: bool = True,
) -> str:
    """Construye el reproductor de voz para Streamlit."""

    texto_seguro = json.dumps(
        texto,
        ensure_ascii=False,
    ).replace("<", "\\u003c")

    automatico = (
        "true" if leer_automaticamente else "false"
    )

    return (
        PLANTILLA_HTML
        .replace("__TEXTO__", texto_seguro)
        .replace("__AUTOMATICO__", automatico)
    )
