from agente import (
    generar_arquitectura,
    ensenar_componente,
    validar_arquitectura,
    corregir_arquitectura,
    integrar_arquitectura,
    normalizar_componentes
)
 
from modelo_ia import preguntar_ia
from orquestador import ejecutar_agente
 
print("AGENTE ARQUITECTO DIGITAL")
print("=========================")
print("1. Enseñar")
print("2. Generar")
print("3. Validar")
print("4. Corregir")
print("5. Integrar")
print("6. Consultar IA")
print("7. Agente automático")
 
opcion = input("\nSelecciona una opción del 1 al 7: ")
 
if opcion == "1":
    componente = input(
        "\nEscribe el componente: "
    ).strip().lower()
 
    print(ensenar_componente(componente))
 
elif opcion == "2":
    nombre = input(
        "\nEscribe el nombre del proyecto: "
    )
 
    print(generar_arquitectura(nombre))
 
elif opcion == "3":
    entrada = input(
        "\nEscribe los componentes separados por comas: "
    )
 
    componentes = normalizar_componentes(entrada)
 
    print(validar_arquitectura(componentes))
 
elif opcion == "4":
    entrada = input(
        "\nEscribe los componentes separados por comas: "
    )
 
    componentes = normalizar_componentes(entrada)
 
    print(corregir_arquitectura(componentes))
 
elif opcion == "5":
    nombre = input(
        "\nEscribe el nombre del proyecto: "
    )
 
    print(integrar_arquitectura(nombre))
 
elif opcion == "6":
    pregunta = input(
        "\nEscribe la pregunta que deseas realizar: "
    )
 
    if pregunta.strip() == "":
        print("\nDebes escribir una pregunta.")
    else:
        print(
            preguntar_ia(pregunta)
        )
 
elif opcion == "7":
    print("\nHas seleccionado: AGENTE AUTOMÁTICO")
    print("\nPuedes conversar con el agente.")
    print("Escribe 'salir' cuando quieras terminar.")
 
    while True:
        solicitud = input("\nTú: ")
 
        if solicitud.lower().strip() == "salir":
            print("\nConversación finalizada.")
            break
 
        resultado = ejecutar_agente(solicitud)
 
        if resultado["requiere_componentes"]:
            print(
                "\nAgente:",
                resultado["respuesta"]
            )
 
            entrada_componentes = input(
                "\nComponentes: "
            )
 
            resultado = ejecutar_agente(
                solicitud,
                entrada_componentes
            )
 
        print("\nPROCESO DEL AGENTE")
        print("==================")
        print(
            "Herramienta:",
            resultado["herramienta"]
        )
        print(
            "Origen:",
            resultado["origen"]
        )
 
        print("\nAgente:")
        print(resultado["respuesta"])
 
else:
    print(
        "\nOpción no válida. Selecciona una opción entre 1 y 7."
    )
