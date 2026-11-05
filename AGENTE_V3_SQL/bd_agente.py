"""Persistencia SQL del historial del Agente Arquitecto Digital.

Esta capa utiliza SQLite, incluido con Python, para guardar de forma
persistente las consultas realizadas a los agentes especializados.
"""

from __future__ import annotations

import sqlite3
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable


BASE_DIR = Path(__file__).resolve().parent
RUTA_BD = BASE_DIR / "agente_historial.db"

_NIVEL_REGISTRO: ContextVar[int] = ContextVar(
    "nivel_registro_sql",
    default=0,
)


def conectar() -> sqlite3.Connection:
    """Abre la conexión y permite leer las filas como diccionarios."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos() -> None:
    """Crea la tabla e índices si todavía no existen."""
    with conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas_agente (
                id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                dominio TEXT NOT NULL,
                capacidad TEXT NOT NULL,
                consulta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                origen TEXT NOT NULL,
                uso_ia INTEGER NOT NULL DEFAULT 0,
                aprendizaje_id TEXT,
                estado_aprendizaje TEXT NOT NULL DEFAULT 'no_aplica'
            )
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_consultas_dominio
            ON consultas_agente(dominio)
            """
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_consultas_fecha
            ON consultas_agente(fecha_hora)
            """
        )

        conexion.commit()


def registrar_consulta(
    dominio: str,
    capacidad: str,
    consulta: str,
    respuesta: str,
    origen: str,
    uso_ia: bool = False,
    aprendizaje_id: str | None = None,
) -> int:
    """Guarda una interacción y devuelve el identificador creado."""
    crear_base_datos()

    estado = (
        "pendiente"
        if aprendizaje_id
        else "no_aplica"
    )

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO consultas_agente (
                fecha_hora,
                dominio,
                capacidad,
                consulta,
                respuesta,
                origen,
                uso_ia,
                aprendizaje_id,
                estado_aprendizaje
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                str(dominio),
                str(capacidad),
                str(consulta),
                str(respuesta),
                str(origen),
                1 if uso_ia else 0,
                aprendizaje_id,
                estado,
            ),
        )

        conexion.commit()
        return int(cursor.lastrowid)


def listar_consultas(
    dominio: str | None = None,
    limite: int = 200,
) -> list[dict[str, Any]]:
    """Devuelve las consultas más recientes."""
    crear_base_datos()

    limite = max(1, min(int(limite), 1000))

    consulta_sql = """
        SELECT
            id_consulta,
            fecha_hora,
            dominio,
            capacidad,
            consulta,
            origen,
            uso_ia,
            aprendizaje_id,
            estado_aprendizaje
        FROM consultas_agente
    """

    parametros: list[Any] = []

    if dominio:
        consulta_sql += " WHERE dominio = ?"
        parametros.append(dominio)

    consulta_sql += " ORDER BY id_consulta DESC LIMIT ?"
    parametros.append(limite)

    with conectar() as conexion:
        filas = conexion.execute(
            consulta_sql,
            parametros,
        ).fetchall()

    return [
        dict(fila)
        for fila in filas
    ]


def obtener_resumen() -> dict[str, int]:
    """Calcula indicadores generales a partir de la base SQL."""
    crear_base_datos()

    with conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN uso_ia = 0 THEN 1 ELSE 0 END) AS locales,
                SUM(CASE WHEN uso_ia = 1 THEN 1 ELSE 0 END) AS gemini,
                SUM(
                    CASE
                        WHEN estado_aprendizaje = 'pendiente'
                        THEN 1 ELSE 0
                    END
                ) AS pendientes,
                SUM(
                    CASE
                        WHEN estado_aprendizaje = 'aceptado'
                        THEN 1 ELSE 0
                    END
                ) AS aceptados,
                SUM(
                    CASE
                        WHEN estado_aprendizaje = 'rechazado'
                        THEN 1 ELSE 0
                    END
                ) AS rechazados
            FROM consultas_agente
            """
        ).fetchone()

    if fila is None:
        return {
            "total": 0,
            "locales": 0,
            "gemini": 0,
            "pendientes": 0,
            "aceptados": 0,
            "rechazados": 0,
        }

    return {
        "total": int(fila["total"] or 0),
        "locales": int(fila["locales"] or 0),
        "gemini": int(fila["gemini"] or 0),
        "pendientes": int(fila["pendientes"] or 0),
        "aceptados": int(fila["aceptados"] or 0),
        "rechazados": int(fila["rechazados"] or 0),
    }


def actualizar_estado_aprendizaje_sql(
    aprendizaje_id: str,
    estado: str,
) -> int:
    """Actualiza en SQL el estado de un aprendizaje aceptado o rechazado."""
    crear_base_datos()

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            UPDATE consultas_agente
            SET estado_aprendizaje = ?
            WHERE aprendizaje_id = ?
            """,
            (
                estado,
                aprendizaje_id,
            ),
        )

        conexion.commit()
        return int(cursor.rowcount)


def _extraer_consulta(
    nombre_funcion: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Obtiene una descripción legible de la solicitud original."""
    segundo = (
        args[1]
        if len(args) > 1
        else ""
    )

    if nombre_funcion == "generar_arquitectura":
        nombre_proyecto = kwargs.get(
            "nombre_proyecto",
            segundo,
        )

        descripcion = kwargs.get(
            "descripcion",
            args[2] if len(args) > 2 else "",
        )

        partes = [
            f"Proyecto: {nombre_proyecto}"
            if nombre_proyecto
            else "",
            f"Necesidad: {descripcion}"
            if descripcion
            else "",
        ]

        return " | ".join(
            parte
            for parte in partes
            if parte
        ) or "Generación de arquitectura"

    if nombre_funcion == "integrar_arquitectura":
        nombre_proyecto = kwargs.get(
            "nombre_proyecto",
            segundo,
        )

        return (
            str(nombre_proyecto)
            if nombre_proyecto
            else "Integración del proyecto"
        )

    return str(
        kwargs.get(
            "concepto",
            kwargs.get(
                "pregunta",
                kwargs.get(
                    "elementos_presentes",
                    segundo,
                ),
            ),
        )
    )


def registrar_interaccion_sql(
    funcion: Callable[..., dict[str, Any]],
) -> Callable[..., dict[str, Any]]:
    """Decorador que guarda una llamada externa al motor en SQLite.

    Las llamadas internas entre funciones del motor no se duplican.
    """

    @wraps(funcion)
    def envoltura(
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:

        nivel_actual = _NIVEL_REGISTRO.get()
        token = _NIVEL_REGISTRO.set(
            nivel_actual + 1
        )

        try:
            resultado = funcion(
                *args,
                **kwargs,
            )
        finally:
            _NIVEL_REGISTRO.reset(
                token
            )

        if (
            nivel_actual == 0
            and isinstance(
                resultado,
                dict,
            )
        ):
            dominio = str(
                kwargs.get(
                    "dominio",
                    args[0] if args else "",
                )
            )

            consulta = _extraer_consulta(
                funcion.__name__,
                args,
                kwargs,
            )

            registrar_consulta(
                dominio=dominio,
                capacidad=str(
                    resultado.get(
                        "capacidad",
                        funcion.__name__,
                    )
                ),
                consulta=consulta,
                respuesta=str(
                    resultado.get(
                        "respuesta",
                        "",
                    )
                ),
                origen=str(
                    resultado.get(
                        "origen",
                        "",
                    )
                ),
                uso_ia=bool(
                    resultado.get(
                        "uso_ia",
                        False,
                    )
                ),
                aprendizaje_id=(
                    str(
                        resultado.get(
                            "aprendizaje_id"
                        )
                    )
                    if resultado.get(
                        "aprendizaje_id"
                    )
                    else None
                ),
            )

        return resultado

    return envoltura


crear_base_datos()
