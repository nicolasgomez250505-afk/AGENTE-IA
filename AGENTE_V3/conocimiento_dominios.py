"""Base de conocimiento editable para los cuatro grupos del curso."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATOS_DIR = BASE_DIR / "datos_dominios"
DOMINIOS = {
    "base_datos": "Bases de Datos",
    "ciberseguridad": "Ciberseguridad",
    "web": "Aplicaciones Web",
    "movil": "Aplicaciones Móviles",
}


def _ruta(dominio: str) -> Path:
    if dominio not in DOMINIOS:
        raise ValueError(f"Dominio no válido: {dominio}")
    return DATOS_DIR / f"{dominio}.json"


def normalizar_texto(texto: str) -> str:
    texto = (texto or "").strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())


def cargar_conocimiento(dominio: str) -> dict:
    with _ruta(dominio).open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    datos.setdefault("ensenar", {})
    datos.setdefault("arquitectura", [])
    datos.setdefault("requisitos", [])
    datos.setdefault("correcciones", {})
    datos.setdefault("integracion", [])
    return datos


def guardar_conocimiento(dominio: str, datos: dict) -> None:
    ruta = _ruta(dominio)
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def agregar_concepto(dominio: str, concepto: str, explicacion: str) -> None:
    datos = cargar_conocimiento(dominio)
    concepto = concepto.strip()
    explicacion = explicacion.strip()
    if not concepto or not explicacion:
        raise ValueError("Concepto y explicación son obligatorios.")
    datos["ensenar"][concepto] = explicacion
    guardar_conocimiento(dominio, datos)


def agregar_elemento_arquitectura(dominio: str, nombre: str, descripcion: str) -> None:
    datos = cargar_conocimiento(dominio)
    nombre = nombre.strip()
    descripcion = descripcion.strip()
    if not nombre or not descripcion:
        raise ValueError("Nombre y descripción son obligatorios.")

    # Si existe, se actualiza en vez de duplicarlo.
    for elemento in datos["arquitectura"]:
        if normalizar_texto(elemento.get("nombre", "")) == normalizar_texto(nombre):
            elemento["nombre"] = nombre
            elemento["descripcion"] = descripcion
            guardar_conocimiento(dominio, datos)
            return

    datos["arquitectura"].append({"nombre": nombre, "descripcion": descripcion})
    guardar_conocimiento(dominio, datos)


def agregar_requisito(dominio: str, requisito: str, recomendacion: str = "") -> None:
    datos = cargar_conocimiento(dominio)
    requisito = requisito.strip()
    if not requisito:
        raise ValueError("El requisito es obligatorio.")

    existentes = {normalizar_texto(x): x for x in datos["requisitos"]}
    if normalizar_texto(requisito) not in existentes:
        datos["requisitos"].append(requisito)

    if recomendacion.strip():
        datos["correcciones"][requisito] = recomendacion.strip()

    guardar_conocimiento(dominio, datos)


def actualizar_integracion(dominio: str, lineas: list[str]) -> None:
    datos = cargar_conocimiento(dominio)
    datos["integracion"] = [x.strip() for x in lineas if x.strip()]
    guardar_conocimiento(dominio, datos)


def buscar_concepto(dominio: str, consulta: str) -> tuple[str | None, str | None]:
    datos = cargar_conocimiento(dominio)
    consulta_n = normalizar_texto(consulta)

    # 1. Coincidencia exacta normalizada.
    for concepto, explicacion in datos["ensenar"].items():
        if normalizar_texto(concepto) == consulta_n:
            return concepto, explicacion

    # 2. Coincidencia por inclusión.
    candidatos = []
    for concepto, explicacion in datos["ensenar"].items():
        c = normalizar_texto(concepto)
        if c in consulta_n or consulta_n in c:
            candidatos.append((len(c), concepto, explicacion))

    if candidatos:
        candidatos.sort(reverse=True)
        _, concepto, explicacion = candidatos[0]
        return concepto, explicacion

    return None, None


