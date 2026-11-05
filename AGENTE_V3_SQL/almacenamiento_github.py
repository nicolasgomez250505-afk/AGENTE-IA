
import os
import json
import base64
import urllib.request
import urllib.error

from pathlib import Path
from urllib.parse import quote


BASE_DIR = Path(__file__).resolve().parent

GITHUB_OWNER = "nicolasgomez250505-afk"
GITHUB_REPO = "AGENTE-IA"
GITHUB_BRANCH = "main"

RUTA_REPOSITORIO = "AGENTE_V3"


def obtener_token():
    """
    Obtiene el token privado desde Streamlit Secrets
    o desde una variable de entorno local.
    """

    token = None

    try:
        import streamlit as st
        token = st.secrets.get("GITHUB_TOKEN")
    except Exception:
        pass

    if not token:
        token = os.getenv("GITHUB_TOKEN")

    return token


def validar_ruta(ruta_relativa):
    """
    Evita que se acceda a archivos fuera de AGENTE_V3.
    """

    ruta = Path(ruta_relativa)

    if ruta.is_absolute() or ".." in ruta.parts:
        raise ValueError("Ruta de archivo no válida.")

    return ruta.as_posix()


def solicitar_github(metodo, ruta, datos=None):
    """
    Realiza una solicitud a la API de GitHub.
    """

    token = obtener_token()

    if not token:
        raise RuntimeError("No se configuró GITHUB_TOKEN.")

    url = (
        "https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/"
        f"{quote(ruta, safe='/')}"
    )

    contenido = None

    if datos is not None:
        contenido = json.dumps(
            datos,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

    solicitud = urllib.request.Request(
        url,
        data=contenido,
        method=metodo
    )

    solicitud.add_header(
        "Authorization",
        f"Bearer {token}"
    )

    solicitud.add_header(
        "Accept",
        "application/vnd.github+json"
    )

    solicitud.add_header(
        "X-GitHub-Api-Version",
        "2022-11-28"
    )

    solicitud.add_header(
        "User-Agent",
        "AGENTE-V3"
    )

    if metodo == "PUT":
        solicitud.add_header(
            "Content-Type",
            "application/json"
        )

    try:
        with urllib.request.urlopen(
            solicitud,
            timeout=20
        ) as respuesta:
            return json.loads(
                respuesta.read().decode("utf-8")
            )

    except urllib.error.HTTPError:
        raise


def leer_json(ruta_relativa, valor_por_defecto=None):
    """
    Lee primero desde GitHub cuando existe token.
    Si no existe token, utiliza el archivo local.
    """

    ruta_relativa = validar_ruta(ruta_relativa)

    ruta_local = BASE_DIR / ruta_relativa

    token = obtener_token()

    if token:
        ruta_remota = (
            f"{RUTA_REPOSITORIO}/{ruta_relativa}"
        )

        try:
            respuesta = solicitar_github(
                "GET",
                ruta_remota
            )

            contenido = base64.b64decode(
                respuesta["content"]
            )

            return json.loads(
                contenido.decode("utf-8")
            )

        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise RuntimeError(
                    "No fue posible leer el archivo "
                    "desde GitHub."
                ) from error

        except Exception as error:
            raise RuntimeError(
                "No fue posible leer el archivo "
                "desde GitHub."
            ) from error

    if ruta_local.exists():
        with ruta_local.open(
            "r",
            encoding="utf-8"
        ) as archivo:
            return json.load(archivo)

    return valor_por_defecto


def guardar_json(ruta_relativa, datos):
    """
    Guarda los datos localmente y, si existe token,
    también actualiza el archivo en GitHub.
    """

    ruta_relativa = validar_ruta(ruta_relativa)

    ruta_local = BASE_DIR / ruta_relativa

    ruta_local.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with ruta_local.open(
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    token = obtener_token()

    if not token:
        return "Guardado localmente."

    ruta_remota = (
        f"{RUTA_REPOSITORIO}/{ruta_relativa}"
    )

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    contenido_codificado = base64.b64encode(
        contenido
    ).decode("utf-8")

    try:
        # Averigua si el archivo ya existe en GitHub.
        try:
            existente = solicitar_github(
                "GET",
                ruta_remota
            )

            sha = existente["sha"]

        except urllib.error.HTTPError as error:
            if error.code == 404:
                sha = None
            else:
                raise

        # Prepara la actualización o creación.
        token = obtener_token()

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/"
            f"{quote(ruta_remota, safe='/')}"
        )

        datos_commit = {
            "message": (
                f"Actualización de {ruta_relativa} "
                "desde AGENTE_V3"
            ),
            "content": contenido_codificado,
            "branch": GITHUB_BRANCH
        }

        if sha:
            datos_commit["sha"] = sha

        solicitud = urllib.request.Request(
            url,
            data=json.dumps(
                datos_commit
            ).encode("utf-8"),
            method="PUT"
        )

        solicitud.add_header(
            "Authorization",
            f"Bearer {token}"
        )

        solicitud.add_header(
            "Accept",
            "application/vnd.github+json"
        )

        solicitud.add_header(
            "X-GitHub-Api-Version",
            "2022-11-28"
        )

        solicitud.add_header(
            "User-Agent",
            "AGENTE-V3"
        )

        with urllib.request.urlopen(
            solicitud,
            timeout=20
        ) as respuesta:
            json.loads(
                respuesta.read().decode("utf-8")
            )

        return "Guardado localmente y sincronizado con GitHub."

    except Exception as error:
        raise RuntimeError(
            "El archivo se guardó localmente, pero no se "
            f"pudo sincronizar con GitHub: {error}"
        ) from error
