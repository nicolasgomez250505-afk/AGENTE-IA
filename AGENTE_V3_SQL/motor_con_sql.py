"""Capa de integración entre el motor de dominios y la persistencia SQL.

No reemplaza motor_dominios.py. Lo reutiliza y agrega el registro
automático de las consultas en agente_historial.db.
"""

from __future__ import annotations

from bd_agente import (
    actualizar_estado_aprendizaje_sql,
    registrar_interaccion_sql,
)

from motor_dominios import (
    actualizar_aprendizaje as _actualizar_aprendizaje,
    consulta_libre as _consulta_libre,
    corregir_arquitectura as _corregir_arquitectura,
    ensenar as _ensenar,
    generar_arquitectura as _generar_arquitectura,
    integrar_arquitectura as _integrar_arquitectura,
    obtener_aprendizaje_por_id,
    obtener_aprendizajes,
    obtener_uso_ia,
    validar_arquitectura as _validar_arquitectura,
)


ensenar = registrar_interaccion_sql(
    _ensenar
)

generar_arquitectura = registrar_interaccion_sql(
    _generar_arquitectura
)

validar_arquitectura = registrar_interaccion_sql(
    _validar_arquitectura
)

corregir_arquitectura = registrar_interaccion_sql(
    _corregir_arquitectura
)

integrar_arquitectura = registrar_interaccion_sql(
    _integrar_arquitectura
)

consulta_libre = registrar_interaccion_sql(
    _consulta_libre
)


def actualizar_aprendizaje(
    aprendizaje_id: str,
    estado: str,
    concepto_final: str = "",
    contenido_final: str = "",
) -> bool:
    """Actualiza el JSON de aprendizajes y sincroniza su estado en SQL."""

    actualizado = _actualizar_aprendizaje(
        aprendizaje_id=aprendizaje_id,
        estado=estado,
        concepto_final=concepto_final,
        contenido_final=contenido_final,
    )

    if actualizado:
        actualizar_estado_aprendizaje_sql(
            aprendizaje_id,
            estado,
        )

    return actualizado
