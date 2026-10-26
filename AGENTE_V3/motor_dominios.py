"""Motor de los agentes especializados por dominio.

Política:
1. Resolver primero con la base local.
2. Usar Gemini únicamente cuando la base local no tenga respuesta suficiente
   y el usuario permita el apoyo de IA.
3. Cuando Gemini sea usado, guardar la respuesta como APRENDIZAJE PENDIENTE.
4. El estudiante debe revisar, editar si lo desea y aceptar explícitamente
   antes de incorporar ese conocimiento a la base local.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from conocimiento_dominios import (
    cargar_conocimiento,
    buscar_concepto,
    normalizar_texto,
)

from modelo_ia import preguntar_ia


BASE_DIR = Path(__file__).resolve().parent
RUTA_USO_IA = BASE_DIR / "uso_ia.json"
RUTA_APRENDIZAJES = BASE_DIR / "aprendizajes_pendientes.json"


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _leer_json(ruta: Path, default):
    if not ruta.exists():
        return default

    try:
        return json.loads(
            ruta.read_text(encoding="utf-8")
        )
    except Exception:
        return default


def _guardar_json(ruta: Path, datos) -> None:
    ruta.write_text(
        json.dumps(
            datos,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def _leer_uso_ia() -> dict:
    return _leer_json(
        RUTA_USO_IA,
        {
            "total": 0,
            "por_dominio": {},
            "historial": [],
            "respuestas_locales": 0,
            "respuestas_locales_por_dominio": {}
        }
    )


def _registrar_respuesta_local(
    dominio: str,
    capacidad: str,
    consulta: str
) -> None:

    datos = _leer_uso_ia()

    datos["respuestas_locales"] = (
        int(datos.get("respuestas_locales", 0)) + 1
    )

    por = datos.setdefault(
        "respuestas_locales_por_dominio",
        {}
    )

    por[dominio] = int(
        por.get(dominio, 0)
    ) + 1

    historial = datos.setdefault(
        "historial",
        []
    )

    historial.append(
        {
            "fecha_hora": _ahora(),
            "dominio": dominio,
            "capacidad": capacidad,
            "consulta": consulta,
            "origen": "base local",
            "motivo": (
                "La base local contenía "
                "conocimiento suficiente."
            )
        }
    )

    datos["historial"] = historial[-200:]

    _guardar_json(
        RUTA_USO_IA,
        datos
    )


def _leer_aprendizajes() -> list[dict]:
    return _leer_json(
        RUTA_APRENDIZAJES,
        []
    )


def _crear_id_aprendizaje(
    aprendizajes: list[dict]
) -> str:

    max_id = 0

    for item in aprendizajes:

        numero = str(
            item.get("id", "")
        ).replace("A", "")

        if numero.isdigit():
            max_id = max(
                max_id,
                int(numero)
            )

    return f"A{max_id + 1:04d}"


def _quitar_prefijo(texto: str) -> str:

    prefijos = [
        "qué es ",
        "que es ",
        "explica ",
        "explícame ",
        "explicame ",
        "define "
    ]

    texto_minuscula = texto.lower()

    for prefijo in prefijos:

        if texto_minuscula.startswith(
            prefijo
        ):
            return texto[len(prefijo):]

    return texto


def _sugerir_concepto(
    consulta: str
) -> str:

    texto = (
        consulta or ""
    ).strip()

    texto = _quitar_prefijo(
        texto
    )

    texto = texto.strip(
        " ¿?¡!.,:;"
    )

    if texto:
        return texto[:120]

    return "Nuevo concepto"


def _crear_aprendizaje_pendiente(
    dominio: str,
    capacidad: str,
    consulta: str,
    respuesta_ia: str,
    motivo: str
) -> str:

    aprendizajes = _leer_aprendizajes()

    nuevo_id = _crear_id_aprendizaje(
        aprendizajes
    )

    aprendizajes.append(
        {
            "id": nuevo_id,
            "fecha_hora": _ahora(),
            "dominio": dominio,
            "capacidad": capacidad,
            "consulta": consulta,
            "concepto_sugerido": (
                _sugerir_concepto(
                    consulta
                )
            ),
            "respuesta_ia": respuesta_ia,
            "motivo": motivo,
            "estado": "pendiente",
            "concepto_final": "",
            "contenido_final": "",
            "fecha_revision": ""
        }
    )

    _guardar_json(
        RUTA_APRENDIZAJES,
        aprendizajes
    )

    return nuevo_id


def _registrar_uso_ia(
    dominio: str,
    capacidad: str,
    consulta: str,
    respuesta: str,
    motivo: str
) -> str:

    datos = _leer_uso_ia()

    datos["total"] = (
        int(datos.get("total", 0)) + 1
    )

    por = datos.setdefault(
        "por_dominio",
        {}
    )

    por[dominio] = int(
        por.get(dominio, 0)
    ) + 1

    historial = datos.setdefault(
        "historial",
        []
    )

    historial.append(
        {
            "fecha_hora": _ahora(),
            "dominio": dominio,
            "capacidad": capacidad,
            "consulta": consulta,
            "origen": "Gemini",
            "motivo": motivo
        }
    )

    datos["historial"] = historial[-200:]

    _guardar_json(
        RUTA_USO_IA,
        datos
    )

    return _crear_aprendizaje_pendiente(
        dominio=dominio,
        capacidad=capacidad,
        consulta=consulta,
        respuesta_ia=respuesta,
        motivo=motivo
    )


def obtener_uso_ia() -> dict:
    return _leer_uso_ia()


def obtener_aprendizajes(
    dominio: str | None = None,
    estado: str | None = None
) -> list[dict]:

    aprendizajes = _leer_aprendizajes()

    salida = []

    for item in aprendizajes:

        if (
            dominio
            and item.get("dominio") != dominio
        ):
            continue

        if (
            estado
            and item.get("estado") != estado
        ):
            continue

        salida.append(
            item
        )

    return salida


def obtener_aprendizaje_por_id(
    aprendizaje_id: str
) -> dict | None:

    for item in _leer_aprendizajes():

        if item.get("id") == aprendizaje_id:
            return item

    return None


def actualizar_aprendizaje(
    aprendizaje_id: str,
    estado: str,
    concepto_final: str = "",
    contenido_final: str = ""
) -> bool:

    aprendizajes = _leer_aprendizajes()

    actualizado = False

    for item in aprendizajes:

        if item.get("id") == aprendizaje_id:

            item["estado"] = estado

            item["concepto_final"] = (
                concepto_final.strip()
            )

            item["contenido_final"] = (
                contenido_final.strip()
            )

            item["fecha_revision"] = (
                _ahora()
            )

            actualizado = True

            break

    if actualizado:

        _guardar_json(
            RUTA_APRENDIZAJES,
            aprendizajes
        )

    return actualizado


def _resultado(
    capacidad: str,
    respuesta: str,
    origen: str,
    uso_ia: bool = False,
    aprendizaje_id: str | None = None
) -> dict:

    return {
        "capacidad": capacidad,
        "respuesta": respuesta,
        "origen": origen,
        "uso_ia": uso_ia,
        "aprendizaje_id": aprendizaje_id
    }


def ensenar(
    dominio: str,
    concepto: str,
    permitir_ia: bool = True
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    encontrado, explicacion = (
        buscar_concepto(
            dominio,
            concepto
        )
    )

    if explicacion:

        _registrar_respuesta_local(
            dominio,
            "enseñar",
            concepto
        )

        concepto_mostrado = encontrado or concepto

        texto = "\n".join(
            [
                concepto_mostrado.upper(),
                "",
                explicacion,
                "",
                (
                    "Origen: conocimiento "
                    "cargado por el grupo."
                )
            ]
        )

        return _resultado(
            "enseñar",
            texto,
            "base local"
        )

    if not permitir_ia:

        return _resultado(
            "enseñar",
            (
                "La base local todavía no "
                "contiene ese concepto. "
                "Agrégalo en «Alimentar dominio» "
                "o habilita el apoyo de IA."
            ),
            "base local"
        )

    contexto = json.dumps(
        {
            "dominio": datos["nombre"],
            "conceptos_disponibles": list(
                datos["ensenar"].keys()
            )
        },
        ensure_ascii=False,
        indent=2
    )

    respuesta_ia = preguntar_ia(
        (
            "Explica de forma pedagógica, "
            "clara y verificable el concepto "
            f"«{concepto}» dentro del dominio "
            f"{datos['nombre']}. "
            "No indiques que el conocimiento "
            "ya fue incorporado a la base local."
        ),
        contexto
    )

    respuesta = respuesta_ia or (
        "Gemini no devolvió contenido para esta consulta."
    )

    aprendizaje_id = _registrar_uso_ia(
        dominio=dominio,
        capacidad="enseñar",
        consulta=concepto,
        respuesta=respuesta,
        motivo=(
            "El concepto no fue encontrado "
            "en la base local."
        )
    )

    return _resultado(
        "enseñar",
        respuesta,
        "Gemini",
        True,
        aprendizaje_id
    )


def generar_arquitectura(
    dominio: str,
    nombre_proyecto: str,
    descripcion: str = ""
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    lineas = [
        (
            "PROPUESTA INICIAL · "
            f"{datos['nombre'].upper()}"
        ),
        (
            "Proyecto: "
            f"{nombre_proyecto or 'Proyecto sin nombre'}"
        ),
        "=" * 55
    ]

    if descripcion.strip():

        lineas += [
            "",
            (
                "Necesidad descrita: "
                f"{descripcion.strip()}"
            )
        ]

    lineas += [
        "",
        "ELEMENTOS PROPUESTOS"
    ]

    for i, elemento in enumerate(
        datos["arquitectura"],
        start=1
    ):

        lineas.append(
            f"{i}. {elemento['nombre']}"
        )

        lineas.append(
            f"   {elemento['descripcion']}"
        )

    lineas += [
        "",
        (
            "Esta propuesta se generó "
            "con conocimiento local del grupo."
        ),
        (
            "Debe ajustarse al contexto "
            "real del proyecto."
        )
    ]

    _registrar_respuesta_local(
        dominio,
        "generar arquitectura",
        nombre_proyecto
        or descripcion
        or "Generación de arquitectura"
    )

    return _resultado(
        "generar arquitectura",
        "\n".join(lineas),
        "base local"
    )


def _normalizar_lista(
    texto_o_lista
) -> list[str]:

    if isinstance(
        texto_o_lista,
        (list, tuple, set)
    ):

        items = list(
            texto_o_lista
        )

    else:

        items = str(
            texto_o_lista or ""
        ).replace(
            ";",
            ","
        ).split(",")

    salida = []

    for item in items:

        limpio = normalizar_texto(
            str(item)
        )

        if (
            limpio
            and limpio not in salida
        ):
            salida.append(
                limpio
            )

    return salida


def validar_arquitectura(
    dominio: str,
    elementos_presentes
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    presentes = _normalizar_lista(
        elementos_presentes
    )

    faltantes = []

    for requisito in datos["requisitos"]:

        req_n = normalizar_texto(
            requisito
        )

        existe = any(
            req_n == p
            or req_n in p
            or p in req_n
            for p in presentes
        )

        if not existe:
            faltantes.append(
                requisito
            )

    if not presentes:

        respuesta = (
            "No se recibieron elementos "
            "para validar."
        )

    elif not faltantes:

        respuesta = (
            "Arquitectura válida según "
            "los requisitos locales del grupo."
        )

    else:

        respuesta = (
            "Faltan los siguientes elementos:\n- "
            + "\n- ".join(
                faltantes
            )
        )

    _registrar_respuesta_local(
        dominio,
        "validar arquitectura",
        ", ".join(presentes)
    )

    return {
        **_resultado(
            "validar arquitectura",
            respuesta,
            "base local"
        ),
        "faltantes": faltantes,
        "presentes": presentes
    }


def corregir_arquitectura(
    dominio: str,
    elementos_presentes
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    validacion = validar_arquitectura(
        dominio,
        elementos_presentes
    )

    faltantes = validacion[
        "faltantes"
    ]

    if not faltantes:

        respuesta = (
            "No se requieren correcciones "
            "según los requisitos locales actuales."
        )

        return _resultado(
            "corregir arquitectura",
            respuesta,
            "base local"
        )

    lineas = [
        "RECOMENDACIONES DE CORRECCIÓN"
    ]

    for requisito in faltantes:

        recomendacion = (
            datos["correcciones"].get(
                requisito,
                (
                    "Agregue o defina "
                    f"el elemento «{requisito}» "
                    "en la arquitectura."
                )
            )
        )

        lineas.append(
            f"- {requisito}: {recomendacion}"
        )

    _registrar_respuesta_local(
        dominio,
        "corregir arquitectura",
        ", ".join(
            _normalizar_lista(
                elementos_presentes
            )
        )
    )

    return _resultado(
        "corregir arquitectura",
        "\n".join(lineas),
        "base local"
    )


def integrar_arquitectura(
    dominio: str,
    nombre_proyecto: str = ""
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    lineas = [
        (
            "INTEGRACIÓN · "
            f"{datos['nombre'].upper()}"
        ),
        (
            "Proyecto: "
            f"{nombre_proyecto or 'Proyecto sin nombre'}"
        ),
        "=" * 55,
        ""
    ]

    lineas.extend(
        f"- {x}"
        for x in datos["integracion"]
    )

    lineas += [
        "",
        (
            "Origen: conocimiento "
            "local del grupo."
        )
    ]

    _registrar_respuesta_local(
        dominio,
        "integrar arquitectura",
        nombre_proyecto
        or "Integración del proyecto"
    )

    return _resultado(
        "integrar arquitectura",
        "\n".join(lineas),
        "base local"
    )


def consulta_libre(
    dominio: str,
    pregunta: str,
    permitir_ia: bool = True
) -> dict:

    datos = cargar_conocimiento(
        dominio
    )

    concepto, explicacion = (
        buscar_concepto(
            dominio,
            pregunta
        )
    )

    if explicacion:

        _registrar_respuesta_local(
            dominio,
            "consulta libre",
            pregunta
        )

        concepto_mostrado = concepto or pregunta

        return _resultado(
            "consulta libre",
            (
                f"{concepto_mostrado.upper()}\n\n"
                f"{explicacion}\n\n"
                "Origen: conocimiento "
                "cargado por el grupo."
            ),
            "base local"
        )

    if not permitir_ia:

        return _resultado(
            "consulta libre",
            (
                "No encontré una respuesta "
                "suficiente en la base local. "
                "El grupo puede alimentar "
                "este conocimiento antes de usar IA."
            ),
            "base local"
        )

    contexto = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2
    )

    respuesta_ia = preguntar_ia(
        (
            "Responde la siguiente consulta "
            f"dentro del dominio {datos['nombre']}: "
            f"{pregunta}. "
            "La respuesta será revisada por "
            "un estudiante antes de poder "
            "incorporarse a la base local."
        ),
        contexto
    )

    respuesta = respuesta_ia or (
        "Gemini no devolvió contenido para esta consulta."
    )

    aprendizaje_id = _registrar_uso_ia(
        dominio=dominio,
        capacidad="consulta libre",
        consulta=pregunta,
        respuesta=respuesta,
        motivo=(
            "La base local no contenía "
            "una respuesta suficiente."
        )
    )

    return _resultado(
        "consulta libre",
        respuesta,
        "Gemini",
        True,
        aprendizaje_id)