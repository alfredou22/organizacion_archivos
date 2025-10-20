import csv
import os
from datetime import datetime

# Nombre del archivo CSV donde se guardarán los datos
NOMBRE_ARCHIVO = 'equipos.csv'

def agregar_equipo(nombre_archivo):
    """
    Añade un nuevo equipo al archivo CSV.
    """
    print("\n--- Agregar Nuevo Equipo de Control ---")
    try:
        # Solicitar y validar datos del usuario
        id_equipo = int(input("Ingrese el ID del equipo: "))
        nombre = input("Ingrese el nombre del equipo: ")
        tipo = input("Ingrese el tipo de equipo (e.g., Sensor, Actuador): ")
        valor_calibracion = float(input("Ingrese el valor de calibración: "))
        
        while True:
            fecha_mantenimiento_str = input("Ingrese la fecha del último mantenimiento (formato YYYY-MM-DD): ")
            try:
                # Validar el formato de la fecha
                datetime.strptime(fecha_mantenimiento_str, '%Y-%m-%d')
                break
            except ValueError:
                print("Error: Formato de fecha incorrecto. Inténtelo de nuevo.")

        # Definir los encabezados si el archivo es nuevo
        encabezados = ['ID', 'Nombre', 'Tipo', 'Valor de Calibracion', 'Ultimo Mantenimiento']
        
        # Comprobar si el archivo ya existe para no reescribir los encabezados
        escribir_encabezado = not os.path.exists(nombre_archivo)

        # Abrir el archivo en modo 'append' (añadir)
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            if escribir_encabezado:
                writer.writerow(encabezados)
            writer.writerow([id_equipo, nombre, tipo, valor_calibracion, fecha_mantenimiento_str])
        
        print(f"\n✅ ¡Equipo '{nombre}' agregado exitosamente!")

    except ValueError:
        print("\n❌ Error: ID y Valor de Calibración deben ser números. Inténtelo de nuevo.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")

def listar_equipos(nombre_archivo):
    """
    Muestra todos los equipos registrados en el archivo CSV.
    """
    print("\n--- Listado de Todos los Equipos ---")
    try:
        with open(nombre_archivo, mode='r', newline='', encoding='utf-8') as archivo_csv:
            reader = csv.reader(archivo_csv)
            encabezado = next(reader)  # Omitir el encabezado
            
            print(f"{' | '.join(encabezado)}")
            print("-" * 70)
            
            contador = 0
            for fila in reader:
                print(f"{fila[0]:<5} | {fila[1]:<20} | {fila[2]:<15} | {fila[3]:<20} | {fila[4]}")
                contador += 1
            
            if contador == 0:
                print("No hay equipos registrados todavía.")

    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no existe. Agregue un equipo primero.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")


def leer_secuencial(nombre_archivo):
    """
    Lee el archivo secuencialmente e imprime cada registro (línea) completo tal como está en el archivo.
    Esto muestra el contenido completo del archivo, línea por línea, incluyendo el encabezado.
    """
    print("\n--- Lectura Secuencial del Archivo (línea por línea) ---")
    try:
        with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
            contador = 0
            for linea in archivo:
                # Imprimir la línea tal cual, eliminando sólo el salto de línea final
                print(linea.rstrip('\n'))
                contador += 1

            if contador == 0:
                print("El archivo está vacío.")

    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no existe. Agregue un equipo primero.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo secuencialmente: {e}")

def buscar_mantenimiento_por_fecha(nombre_archivo):
    """
    Busca y lista los equipos que necesitan mantenimiento en un rango de fechas.
    """
    print("\n--- Buscar Equipos por Fecha de Mantenimiento ---")
    try:
        # Solicitar rango de fechas al usuario
        fecha_inicio_str = input("Ingrese la fecha de inicio del rango (YYYY-MM-DD): ")
        fecha_fin_str = input("Ingrese la fecha de fin del rango (YYYY-MM-DD): ")

        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        print("\nEquipos que necesitan mantenimiento entre {} y {}:".format(fecha_inicio_str, fecha_fin_str))
        encontrados = []
        
        with open(nombre_archivo, mode='r', newline='', encoding='utf-8') as archivo_csv:
            reader = csv.DictReader(archivo_csv)
            for fila in reader:
                fecha_mantenimiento = datetime.strptime(fila['Ultimo Mantenimiento'], '%Y-%m-%d').date()
                if fecha_inicio <= fecha_mantenimiento <= fecha_fin:
                    encontrados.append(fila)

        if encontrados:
            encabezados = ['ID', 'Nombre', 'Tipo', 'Valor de Calibracion', 'Ultimo Mantenimiento']
            print(f"{' | '.join(encabezados)}")
            print("-" * 70)
            for equipo in encontrados:
                print(f"{equipo['ID']:<5} | {equipo['Nombre']:<20} | {equipo['Tipo']:<15} | {equipo['Valor de Calibracion']:<20} | {equipo['Ultimo Mantenimiento']}")
        else:
            print("No se encontraron equipos que requieran mantenimiento en ese rango de fechas.")

    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no existe. Agregue un equipo primero.")
    except ValueError:
        print("Error: Formato de fecha incorrecto. Use YYYY-MM-DD.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def buscar_equipo_por_id_acceso_directo(nombre_archivo, id_buscar=None):
    """
    Construye un índice simple de ID -> offset en el archivo y utiliza seek()
    para saltar directamente a la línea donde está el equipo y mostrar su información completa.

    Si id_buscar es None, solicita el ID al usuario.
    """
    print("\n--- Buscar Equipo por ID (acceso directo usando seek) ---")
    try:
        with open(nombre_archivo, mode='r', encoding='utf-8', newline='') as archivo:
            # Leer encabezado y obtener nombres de columnas
            encabezado_line = archivo.readline()
            if not encabezado_line:
                print("El archivo está vacío.")
                return
            encabezados = next(csv.reader([encabezado_line.strip()]))

            # Construir índice de offsets: ID (int) -> offset (posición del comienzo de la línea)
            indice = {}
            while True:
                offset = archivo.tell()
                linea = archivo.readline()
                if not linea:
                    break
                try:
                    fila = next(csv.reader([linea]))
                except Exception:
                    # Si la línea no es válida CSV, la saltamos
                    continue
                if len(fila) == 0:
                    continue
                try:
                    id_int = int(fila[0])
                except ValueError:
                    # No es un ID válido
                    continue
                # Guardar offset donde comienza la línea
                indice[id_int] = offset

            # Obtener ID a buscar (si no se pasó por parámetro)
            if id_buscar is None:
                entrada = input("Ingrese el ID del equipo a buscar: ")
                try:
                    id_buscar = int(entrada)
                except ValueError:
                    print("ID inválido. Debe ser un número entero.")
                    return

            # Buscar en índice
            if id_buscar in indice:
                archivo.seek(indice[id_buscar])
                linea_equipo = archivo.readline()
                try:
                    datos = next(csv.reader([linea_equipo]))
                except Exception:
                    print("Error al parsear la línea del equipo.")
                    return

                # Mostrar toda la información asociada al equipo
                print("\nInformación completa del equipo:")
                for cab, val in zip(encabezados, datos):
                    print(f"{cab}: {val}")
            else:
                print(f"No se encontró un equipo con ID {id_buscar}.")

    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no existe. Agregue un equipo primero.")
    except Exception as e:
        print(f"Ocurrió un error al buscar por ID: {e}")


def main():
    """
    Función principal que muestra el menú de opciones.
    """
    while True:
        print("\n--- 🏭 Sistema de Gestión de Equipos de Control ---")
        print("1. Agregar un nuevo equipo")
        print("2. Listar todos los equipos")
        print("3. Buscar equipos por fecha de mantenimiento")
        print("4. Salir")
        print("5. Leer archivo secuencialmente (mostrar todas las líneas)")
        print("6. Buscar equipo por ID (acceso directo con seek)")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            agregar_equipo(NOMBRE_ARCHIVO)
        elif opcion == '2':
            listar_equipos(NOMBRE_ARCHIVO)
        elif opcion == '3':
            buscar_mantenimiento_por_fecha(NOMBRE_ARCHIVO)
        elif opcion == '5':
            leer_secuencial(NOMBRE_ARCHIVO)
        elif opcion == '6':
            buscar_equipo_por_id_acceso_directo(NOMBRE_ARCHIVO)
        elif opcion == '4':
            print("\nSaliendo del programa. ¡Hasta luego!")
            break
        else:
            print("\nOpción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()