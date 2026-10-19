from agente import analizar_proyecto
 
print("AGENTE ARQUITECTO DIGITAL")
 
nombre_proyecto = input("Escribe el nombre del proyecto: ")
 
resultado = analizar_proyecto(nombre_proyecto)
 
print("Proyecto analizado:")
print(resultado)
