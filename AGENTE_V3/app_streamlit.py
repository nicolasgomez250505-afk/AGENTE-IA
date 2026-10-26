"""Interfaz gráfica del Agente Arquitecto Digital.

Esta interfaz permite:
- Probar el agente por dominio.
- Alimentar conocimiento desde formularios.
- Consultar la biblioteca local.
- Revisar aprendizajes propuestos por Gemini.
- Auditar el uso de IA.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import streamlit as st

from conocimiento_dominios import (
    DOMINIOS,
    agregar_concepto,
    agregar_elemento_arquitectura,
    agregar_requisito,
    actualizar_integracion,
    cargar_conocimiento,
)

from motor_dominios import (
    actualizar_aprendizaje,
    consulta_libre,
    corregir_arquitectura,
    ensenar,
    generar_arquitectura,
    integrar_arquitectura,
    obtener_aprendizaje_por_id,
    obtener_aprendizajes,
    obtener_uso_ia,
    validar_arquitectura,
)


BASE_DIR = Path(__file__).resolve().parent
RUTA_LOGO = BASE_DIR / "kick.png"


st.set_page_config(
    page_title="Nuestro Agente Arquitecto Digital",
    page_icon="🤖",
    layout="wide",
)


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2.4rem;
            padding-bottom: 3rem;
        }

        .big-title {
            font-size: clamp(2rem, 4vw, 3.25rem);
            font-weight: 750;
            line-height: 1.05;
            margin-top: 0.4rem;
            margin-bottom: 0.35rem;
        }

        .subtitle {
            color: #5b6472;
            font-size: 1.05rem;
            margin-bottom: 1rem;
        }

        div[data-baseweb="tab-list"] {
            gap: 0.35rem;
            flex-wrap: wrap !important;
        }

        button[data-baseweb="tab"] {
            min-width: 170px;
            flex: 1 1 170px;
        }

        button[data-baseweb="tab"] p {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        @media (max-width: 900px) {
            button[data-baseweb="tab"] {
                flex: 1 1 30%;
            }
        }

        @media (max-width: 650px) {
            button[data-baseweb="tab"] {
                flex: 1 1 45%;
            }
        }

        @media (max-width: 430px) {
            button[data-baseweb="tab"] {
                flex: 1 1 100%;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _texto(valor: Any) -> str:
    """Convierte cualquier valor a texto seguro."""
    if valor is None:
        return ""
    return str(valor)


def _lista(valor: Any) -> list[Any]:
    """Garantiza que el valor sea una lista."""
    if isinstance(valor, list):
        return valor
    return []


def _diccionario(valor: Any) -> dict[str, Any]:
    """Garantiza que el valor sea un diccionario."""
    if isinstance(valor, dict):
        return valor
    return {}


def _formatear_dominio(codigo: str) -> str:
    """Devuelve siempre un nombre de dominio en formato texto."""
    nombre = DOMINIOS.get(codigo)

    if nombre is None:
        return codigo

    return str(nombre)


def _mostrar_origen(resultado: dict[str, Any]) -> None:
    """Muestra si la respuesta vino de la base local o de Gemini."""
    origen = _texto(
        resultado.get("origen")
    ).strip().lower()

    uso_ia = bool(
        resultado.get("uso_ia", False)
    )

    if uso_ia or origen == "gemini":
        st.warning(
            "Origen: Gemini · IA utilizada"
        )
    else:
        st.success(
            "Origen: base local · sin IA"
        )


def _mostrar_resultado(
    resultado: dict[str, Any]
) -> None:
    """Muestra una respuesta estándar del motor de dominios."""
    _mostrar_origen(resultado)

    respuesta = _texto(
        resultado.get("respuesta")
    ).strip()

    if respuesta:
        st.code(
            respuesta,
            language=None
        )
    else:
        st.info(
            "El agente no devolvió contenido."
        )

    aprendizaje_id = _texto(
        resultado.get("aprendizaje_id")
    ).strip()

    if aprendizaje_id:
        st.info(
            "Se creó el aprendizaje pendiente "
            f"{aprendizaje_id}. Revísalo en "
            "«🧠 Revisar aprendizajes IA»."
        )


def _dominio_actual() -> str:
    """Permite seleccionar el dominio activo."""
    opciones: list[str] = list(
        DOMINIOS.keys()
    )

    seleccionado = st.sidebar.selectbox(
        "Grupo / dominio",
        options=opciones,
        format_func=_formatear_dominio,
    )

    return cast(str, seleccionado)


# ---------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------

if (
    RUTA_LOGO.exists()
    and RUTA_LOGO.stat().st_size > 0
):
    try:
        st.sidebar.image(
            str(RUTA_LOGO),
            use_container_width=True
        )
    except Exception:
        st.sidebar.caption(
            "Universitaria de Colombia"
        )


st.sidebar.markdown(
    "## Agente Arquitecto Digital"
)


PAGINAS: list[str] = [
    "🏠 Inicio",
    "🧪 Probar agente",
    "📚 Alimentar dominio",
    "📖 Biblioteca del grupo",
    "🧠 Revisar aprendizajes IA",
    "🤖 Uso de IA",
]


pagina_seleccionada = st.sidebar.radio(
    "Navegación",
    options=PAGINAS,
)

pagina = cast(
    str,
    pagina_seleccionada
)

dominio = _dominio_actual()

nombre_dominio = _formatear_dominio(
    dominio
)

st.sidebar.caption(
    f"Dominio activo: {nombre_dominio}"
)


# ---------------------------------------------------------
# INICIO
# ---------------------------------------------------------

if pagina == "🏠 Inicio":

    st.markdown(
        '<div class="big-title">'
        "Agente Arquitecto Digital"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "Interfaz gráfica para probar, alimentar "
        "y auditar el conocimiento de los "
        "agentes especializados."
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "Regla central del proyecto: "
        "la base local responde primero. "
        "Gemini se utiliza únicamente cuando "
        "el conocimiento local no es suficiente."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. Alimentar")

        st.write(
            "Cada grupo incorpora conceptos, "
            "arquitectura, requisitos, correcciones "
            "y reglas de integración."
        )

    with col2:
        st.subheader("2. Probar")

        st.write(
            "El agente intenta resolver las "
            "solicitudes utilizando primero "
            "la base local."
        )

    with col3:
        st.subheader("3. Aprender")

        st.write(
            "Cuando Gemini aporta conocimiento "
            "nuevo, un estudiante lo revisa "
            "antes de incorporarlo."
        )

    st.markdown("---")

    st.markdown(
        "**Gemini propone → el estudiante revisa → "
        "solo el conocimiento aceptado pasa "
        "a la base local.**"
    )


# ---------------------------------------------------------
# PROBAR AGENTE
# ---------------------------------------------------------

elif pagina == "🧪 Probar agente":

    st.markdown(
        f'<div class="big-title">'
        f"{nombre_dominio}"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Prueba las capacidades del agente "
        "especializado."
    )

    permitir_ia = st.toggle(
        "Permitir Gemini únicamente cuando "
        "la base local no tenga una respuesta "
        "suficiente",
        value=True,
    )

    tabs = st.tabs(
        [
            "📘 Enseñar",
            "🏗️ Generar arquitectura",
            "✅ Validar arquitectura",
            "🛠️ Corregir arquitectura",
            "🔗 Integrar arquitectura",
            "💬 Consulta libre",
        ]
    )

    with tabs[0]:

        concepto = st.text_input(
            "Concepto que deseas consultar",
            key="probar_ensenar_concepto",
            placeholder="Ejemplo: clave primaria",
        )

        if st.button(
            "Enseñar",
            key="btn_probar_ensenar",
            type="primary",
        ):

            if not concepto.strip():

                st.warning(
                    "Escribe un concepto."
                )

            else:

                resultado = ensenar(
                    dominio,
                    concepto,
                    permitir_ia=permitir_ia,
                )

                _mostrar_resultado(
                    resultado
                )

    with tabs[1]:

        nombre_proyecto = st.text_input(
            "Nombre del proyecto",
            key="probar_generar_nombre",
            placeholder="Ejemplo: Biblioteca Universitaria",
        )

        necesidad = st.text_area(
            "Necesidad del proyecto",
            key="probar_generar_necesidad",
            placeholder=(
                "Ejemplo: gestionar préstamos, "
                "devoluciones y disponibilidad "
                "de libros."
            ),
        )

        if st.button(
            "Generar arquitectura",
            key="btn_probar_generar",
            type="primary",
        ):

            resultado = generar_arquitectura(
                dominio,
                nombre_proyecto,
                necesidad,
            )

            _mostrar_resultado(
                resultado
            )

    with tabs[2]:

        presentes = st.text_area(
            "Elementos presentes en la arquitectura",
            key="probar_validar",
            placeholder=(
                "Escríbelos separados por comas.\n"
                "Ejemplo: entidades, clave primaria, relaciones"
            ),
        )

        if st.button(
            "Validar arquitectura",
            key="btn_probar_validar",
            type="primary",
        ):

            resultado = validar_arquitectura(
                dominio,
                presentes,
            )

            _mostrar_resultado(
                resultado
            )

    with tabs[3]:

        presentes_corregir = st.text_area(
            "Elementos presentes actualmente",
            key="probar_corregir",
            placeholder=(
                "Escríbelos separados por comas "
                "para que el agente detecte faltantes."
            ),
        )

        if st.button(
            "Corregir arquitectura",
            key="btn_probar_corregir",
            type="primary",
        ):

            resultado = corregir_arquitectura(
                dominio,
                presentes_corregir,
            )

            _mostrar_resultado(
                resultado
            )

    with tabs[4]:

        proyecto_integrar = st.text_input(
            "Nombre del proyecto",
            key="probar_integrar_nombre",
            placeholder="Ejemplo: Biblioteca Universitaria",
        )

        if st.button(
            "Integrar arquitectura",
            key="btn_probar_integrar",
            type="primary",
        ):

            resultado = integrar_arquitectura(
                dominio,
                proyecto_integrar,
            )

            _mostrar_resultado(
                resultado
            )

    with tabs[5]:

        pregunta = st.text_area(
            "Pregunta libre",
            key="probar_consulta_libre",
            placeholder=(
                "Escribe una pregunta relacionada "
                "con el dominio."
            ),
        )

        if st.button(
            "Consultar",
            key="btn_consulta_libre",
            type="primary",
        ):

            if not pregunta.strip():

                st.warning(
                    "Escribe una pregunta."
                )

            else:

                resultado = consulta_libre(
                    dominio,
                    pregunta,
                    permitir_ia=permitir_ia,
                )

                _mostrar_resultado(
                    resultado
                )


# ---------------------------------------------------------
# ALIMENTAR DOMINIO
# ---------------------------------------------------------

elif pagina == "📚 Alimentar dominio":

    st.markdown(
        f'<div class="big-title">'
        f"Alimentar · {nombre_dominio}"
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        "En esta página el grupo construye "
        "su base local de conocimiento sin "
        "editar manualmente los archivos JSON."
    )

    tabs = st.tabs(
        [
            "📘 ENSEÑAR",
            "🏗️ GENERAR",
            "✅ VALIDAR",
            "🛠️ CORREGIR",
            "🔗 INTEGRAR",
        ]
    )

    with tabs[0]:

        concepto_nuevo = st.text_input(
            "Concepto",
            key="alimentar_concepto",
            placeholder="Ejemplo: clave primaria",
        )

        explicacion_nueva = st.text_area(
            "Explicación",
            key="alimentar_explicacion",
            placeholder=(
                "Explica el concepto de forma "
                "clara, académica y comprensible."
            ),
        )

        if st.button(
            "Guardar concepto",
            key="btn_guardar_concepto",
            type="primary",
        ):

            try:

                agregar_concepto(
                    dominio,
                    concepto_nuevo,
                    explicacion_nueva,
                )

                st.success(
                    "Concepto guardado correctamente."
                )

            except ValueError as error:

                st.error(
                    str(error)
                )

    with tabs[1]:

        elemento_nombre = st.text_input(
            "Elemento de arquitectura",
            key="alimentar_arq_nombre",
            placeholder="Ejemplo: Entidades",
        )

        elemento_descripcion = st.text_area(
            "Descripción del elemento",
            key="alimentar_arq_descripcion",
        )

        if st.button(
            "Guardar elemento de arquitectura",
            key="btn_guardar_arquitectura",
            type="primary",
        ):

            try:

                agregar_elemento_arquitectura(
                    dominio,
                    elemento_nombre,
                    elemento_descripcion,
                )

                st.success(
                    "Elemento de arquitectura guardado."
                )

            except ValueError as error:

                st.error(
                    str(error)
                )

    with tabs[2]:

        requisito_nuevo = st.text_input(
            "Requisito que el agente debe validar",
            key="alimentar_requisito",
            placeholder="Ejemplo: clave primaria",
        )

        recomendacion_inicial = st.text_area(
            "Recomendación de corrección (opcional)",
            key="alimentar_recomendacion_inicial",
            placeholder=(
                "Ejemplo: definir una clave primaria "
                "para cada entidad."
            ),
        )

        if st.button(
            "Guardar requisito",
            key="btn_guardar_requisito",
            type="primary",
        ):

            try:

                agregar_requisito(
                    dominio,
                    requisito_nuevo,
                    recomendacion_inicial,
                )

                st.success(
                    "Requisito guardado correctamente."
                )

            except ValueError as error:

                st.error(
                    str(error)
                )

    with tabs[3]:

        datos = cargar_conocimiento(
            dominio
        )

        requisitos = [
            _texto(item)
            for item in _lista(
                datos.get("requisitos")
            )
            if _texto(item).strip()
        ]

        if not requisitos:

            st.info(
                "Primero agrega al menos "
                "un requisito en la pestaña VALIDAR."
            )

        else:

            requisito_seleccionado_raw = st.selectbox(
                "Requisito que deseas corregir",
                options=requisitos,
                key="corregir_requisito_select",
            )

            requisito_seleccionado = cast(
                str,
                requisito_seleccionado_raw
            )

            correcciones = _diccionario(
                datos.get("correcciones")
            )

            recomendacion_actual = _texto(
                correcciones.get(
                    requisito_seleccionado,
                    "",
                )
            )

            recomendacion_nueva = st.text_area(
                "Recomendación",
                value=recomendacion_actual,
                key="alimentar_correccion",
            )

            if st.button(
                "Guardar recomendación",
                key="btn_guardar_correccion",
                type="primary",
            ):

                try:

                    agregar_requisito(
                        dominio,
                        requisito_seleccionado,
                        recomendacion_nueva,
                    )

                    st.success(
                        "Recomendación guardada."
                    )

                except ValueError as error:

                    st.error(
                        str(error)
                    )

    with tabs[4]:

        datos = cargar_conocimiento(
            dominio
        )

        reglas_actuales = "\n".join(
            _texto(item)
            for item in _lista(
                datos.get("integracion")
            )
        )

        reglas_texto = st.text_area(
            "Reglas de integración",
            value=reglas_actuales,
            height=220,
            key="alimentar_integracion",
            placeholder="Escribe una regla por línea.",
        )

        if st.button(
            "Guardar reglas de integración",
            key="btn_guardar_integracion",
            type="primary",
        ):

            reglas = [
                linea.strip()
                for linea in reglas_texto.splitlines()
                if linea.strip()
            ]

            actualizar_integracion(
                dominio,
                reglas,
            )

            st.success(
                "Reglas de integración guardadas."
            )


# ---------------------------------------------------------
# BIBLIOTECA
# ---------------------------------------------------------

elif pagina == "📖 Biblioteca del grupo":

    st.markdown(
        f'<div class="big-title">'
        f"Biblioteca · {nombre_dominio}"
        "</div>",
        unsafe_allow_html=True,
    )

    datos = cargar_conocimiento(
        dominio
    )

    conceptos = _diccionario(
        datos.get("ensenar")
    )

    arquitectura = _lista(
        datos.get("arquitectura")
    )

    requisitos = _lista(
        datos.get("requisitos")
    )

    correcciones = _diccionario(
        datos.get("correcciones")
    )

    integracion = _lista(
        datos.get("integracion")
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Conceptos",
        len(conceptos),
    )

    col2.metric(
        "Elementos de arquitectura",
        len(arquitectura),
    )

    col3.metric(
        "Requisitos",
        len(requisitos),
    )

    st.markdown(
        "### 📘 Conceptos"
    )

    if conceptos:

        for concepto, explicacion in conceptos.items():

            with st.expander(
                _texto(concepto)
            ):

                st.write(
                    _texto(explicacion)
                )

    else:

        st.info(
            "Todavía no hay conceptos guardados."
        )

    st.markdown(
        "### 🏗️ Arquitectura"
    )

    if arquitectura:

        for elemento in arquitectura:

            if isinstance(
                elemento,
                dict
            ):

                nombre = _texto(
                    elemento.get("nombre")
                )

                descripcion = _texto(
                    elemento.get("descripcion")
                )

                st.markdown(
                    f"**{nombre}**"
                )

                st.write(
                    descripcion
                )

            else:

                st.write(
                    f"- {_texto(elemento)}"
                )

    else:

        st.info(
            "Todavía no hay elementos "
            "de arquitectura."
        )

    st.markdown(
        "### ✅ Requisitos"
    )

    if requisitos:

        for requisito in requisitos:

            req = _texto(
                requisito
            )

            st.write(
                f"- {req}"
            )

            recomendacion = _texto(
                correcciones.get(
                    req,
                    ""
                )
            )

            if recomendacion:

                st.caption(
                    "Corrección: "
                    + recomendacion
                )

    else:

        st.info(
            "Todavía no hay requisitos."
        )

    st.markdown(
        "### 🔗 Integración"
    )

    if integracion:

        for regla in integracion:

            st.write(
                f"- {_texto(regla)}"
            )

    else:

        st.info(
            "Todavía no hay reglas "
            "de integración."
        )

    contenido_descarga = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ Descargar JSON del dominio",
        data=contenido_descarga,
        file_name=f"{dominio}.json",
        mime="application/json",
    )


# ---------------------------------------------------------
# REVISAR APRENDIZAJES IA
# ---------------------------------------------------------

elif pagina == "🧠 Revisar aprendizajes IA":

    st.markdown(
        '<div class="big-title">'
        "Revisar aprendizajes obtenidos con IA"
        "</div>",
        unsafe_allow_html=True,
    )

    pendientes = obtener_aprendizajes(
        dominio=dominio,
        estado="pendiente",
    )

    if not pendientes:

        st.success(
            "No hay aprendizajes pendientes "
            "de revisión para este dominio."
        )

    else:

        ids: list[str] = [
            _texto(
                item.get("id")
            )
            for item in pendientes
            if _texto(
                item.get("id")
            ).strip()
        ]

        if not ids:

            st.info(
                "No hay identificadores válidos "
                "de aprendizajes pendientes."
            )

        else:

            aprendizaje_id_raw = st.selectbox(
                "Aprendizaje pendiente",
                options=ids,
            )

            aprendizaje_id = cast(
                str,
                aprendizaje_id_raw
            ).strip()

            aprendizaje = obtener_aprendizaje_por_id(
                aprendizaje_id
            )

            if aprendizaje is None:

                st.error(
                    "No fue posible recuperar "
                    "el aprendizaje seleccionado."
                )

            else:

                st.markdown(
                    "#### Consulta original"
                )

                st.write(
                    _texto(
                        aprendizaje.get(
                            "consulta"
                        )
                    )
                )

                st.markdown(
                    "#### Respuesta propuesta por Gemini"
                )

                st.write(
                    _texto(
                        aprendizaje.get(
                            "respuesta_ia"
                        )
                    )
                )

                concepto_inicial = _texto(
                    aprendizaje.get(
                        "concepto_final"
                    )
                ).strip()

                if not concepto_inicial:

                    concepto_inicial = _texto(
                        aprendizaje.get(
                            "concepto_sugerido"
                        )
                    ).strip()

                contenido_inicial = _texto(
                    aprendizaje.get(
                        "contenido_final"
                    )
                ).strip()

                if not contenido_inicial:

                    contenido_inicial = _texto(
                        aprendizaje.get(
                            "respuesta_ia"
                        )
                    ).strip()

                concepto_final = st.text_input(
                    "Nombre final del concepto",
                    value=concepto_inicial,
                )

                contenido_final = st.text_area(
                    "Contenido final",
                    value=contenido_inicial,
                    height=260,
                )

                confirmacion = st.checkbox(
                    "Confirmo que revisé el contenido."
                )

                col1, col2 = st.columns(2)

                with col1:

                    aceptar = st.button(
                        "✅ Aceptar e incorporar",
                        type="primary",
                        use_container_width=True,
                    )

                with col2:

                    rechazar = st.button(
                        "❌ Rechazar conocimiento",
                        use_container_width=True,
                    )

                if aceptar:

                    if not confirmacion:

                        st.warning(
                            "Debes confirmar la revisión."
                        )

                    elif not concepto_final.strip():

                        st.warning(
                            "Define el nombre del concepto."
                        )

                    elif not contenido_final.strip():

                        st.warning(
                            "El contenido no puede estar vacío."
                        )

                    else:

                        concepto_guardar = concepto_final.strip()
                        contenido_guardar = contenido_final.strip()

                        agregar_concepto(
                            dominio,
                            concepto_guardar,
                            contenido_guardar,
                        )

                        actualizado = actualizar_aprendizaje(
                            aprendizaje_id=aprendizaje_id,
                            estado="aceptado",
                            concepto_final=concepto_guardar,
                            contenido_final=contenido_guardar,
                        )

                        if actualizado:

                            st.success(
                                "Aprendizaje incorporado "
                                "a la base local."
                            )

                            st.rerun()

                if rechazar:

                    if not confirmacion:

                        st.warning(
                            "Debes confirmar la revisión."
                        )

                    else:

                        actualizado = actualizar_aprendizaje(
                            aprendizaje_id=aprendizaje_id,
                            estado="rechazado",
                            concepto_final=concepto_final.strip(),
                            contenido_final=contenido_final.strip(),
                        )

                        if actualizado:

                            st.info(
                                "Conocimiento rechazado."
                            )

                            st.rerun()


# ---------------------------------------------------------
# USO DE IA
# ---------------------------------------------------------

elif pagina == "🤖 Uso de IA":

    st.markdown(
        '<div class="big-title">'
        "Uso de IA"
        "</div>",
        unsafe_allow_html=True,
    )

    uso = obtener_uso_ia()

    total_ia = int(
        uso.get(
            "total",
            0
        ) or 0
    )

    total_local = int(
        uso.get(
            "respuestas_locales",
            0
        ) or 0
    )

    total_general = (
        total_ia
        + total_local
    )

    porcentaje_ia = (
        total_ia
        / total_general
        * 100
        if total_general
        else 0.0
    )

    porcentaje_local = (
        total_local
        / total_general
        * 100
        if total_general
        else 0.0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Respuestas locales",
        total_local,
    )

    c2.metric(
        "Consultas a Gemini",
        total_ia,
    )

    c3.metric(
        "% local",
        f"{porcentaje_local:.1f} %",
    )

    c4.metric(
        "% IA",
        f"{porcentaje_ia:.1f} %",
    )

    st.markdown(
        "### Uso por dominio"
    )

    locales_por_dominio = _diccionario(
        uso.get(
            "respuestas_locales_por_dominio"
        )
    )

    ia_por_dominio = _diccionario(
        uso.get(
            "por_dominio"
        )
    )

    filas: list[dict[str, Any]] = []

    for codigo, nombre in DOMINIOS.items():

        filas.append(
            {
                "Dominio": str(nombre),
                "Respuestas locales": int(
                    locales_por_dominio.get(
                        codigo,
                        0
                    ) or 0
                ),
                "Gemini": int(
                    ia_por_dominio.get(
                        codigo,
                        0
                    ) or 0
                ),
            }
        )

    st.dataframe(
        filas,
        use_container_width=True,
        hide_index=True,
    )

    aprendizajes = obtener_aprendizajes(
        dominio=dominio
    )

    pendientes_n = sum(
        1
        for item in aprendizajes
        if _texto(
            item.get("estado")
        ) == "pendiente"
    )

    aceptados_n = sum(
        1
        for item in aprendizajes
        if _texto(
            item.get("estado")
        ) == "aceptado"
    )

    rechazados_n = sum(
        1
        for item in aprendizajes
        if _texto(
            item.get("estado")
        ) == "rechazado"
    )

    st.markdown(
        f"### Aprendizajes de {nombre_dominio}"
    )

    a1, a2, a3 = st.columns(3)

    a1.metric(
        "Pendientes",
        pendientes_n,
    )

    a2.metric(
        "Aceptados",
        aceptados_n,
    )

    a3.metric(
        "Rechazados",
        rechazados_n,
    )

    st.info(
        "Principio del proyecto: "
        "Gemini propone; el estudiante revisa; "
        "solo el conocimiento aceptado "
        "pasa a la base local."
    )
