from agente import (
    generar_arquitectura,
    ensenar_componente,
    validar_arquitectura,
    corregir_arquitectura,
    integrar_arquitectura,
    normalizar_componentes
)
 
print("AGENTE ARQUITECTO DIGITAL")
print("=========================")
print("1. Enseñar")
print("2. Generar")
print("3. Validar")
print("4. Corregir")
print("5. Integrar")
 
opcion = input("\nSelecciona una opción del 1 al 5: ")
 
if opcion == "1":
    componente = input(
        "\nEscribe el componente: "
    ).strip().lower()
 
    print(
        ensenar_componente(componente)
    )
 
elif opcion == "2":
    nombre = input(
        "\nEscribe el nombre del proyecto: "
    )
 
    print(
        generar_arquitectura(nombre)
    )
 
elif opcion == "3":
    entrada = input(
        "\nEscribe los componentes separados por comas: "
    )
 
    componentes = normalizar_componentes(
        entrada
    )
 
    print(
        validar_arquitectura(componentes)
    )
 
elif opcion == "4":
    entrada = input(
        "\nEscribe los componentes separados por comas: "
    )
 
    componentes = normalizar_componentes(
        entrada
    )
 
    print(
        corregir_arquitectura(componentes)
    )
 
elif opcion == "5":
    nombre = input(
        "\nEscribe el nombre del proyecto: "
    )
 
    print(
        integrar_arquitectura(nombre)
    )
 
else:
    print(
        "\nOpción no válida. Selecciona una opción entre 1 y 5."
    )
