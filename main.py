
import pandas as pd


pd.set_option("display.max_columns", None)
pd.set_option("display.width", 180)
pd.set_option("display.max_colwidth", 60)

def menu():
    print("\n=== GESTOR DE REGISTROS MÉDICOS SIMPLIFICADO ===")
    print("1) Cargar datos procesados")
    print("2) Mostrar primeros 20 registros")
    print("3) Ver información general del archivo")
    print("4) Mostrar resumen estadístico")
    print("0) Salir")
    return input("Elige una opción: ")

def cargar_datos():
    try:
        datos = pd.read_csv("Datos_Procesados/datos_procesados.csv")
        # Convertir fechas si existen
        for col in ("dia_programado", "dia_cita"):
            if col in datos.columns:
                datos[col] = pd.to_datetime(datos[col], errors="coerce")
        print("\nArchivo cargado correctamente.")
        return datos
    except FileNotFoundError:
        print("\nNo se encontró el archivo 'Datos_Procesados/datos_procesados.csv'.")
        return None
    except Exception as e:
        print("\nOcurrió un error al cargar el archivo:", e)
        return None

def mostrar_primeros(datos):
    if datos is None:
        print("\nPrimero carga los datos.")
        return
    print("\n--- PRIMEROS 20 REGISTROS ---")
    print(datos.head(20))

def mostrar_informacion(datos):
    if datos is None:
        print("\nPrimero carga los datos (opción 1).")
        return
    print("\n--- INFORMACIÓN GENERAL DEL ARCHIVO ---")
    print("Número total de registros:", len(datos))
    print("\nColumnas disponibles:")
    print(list(datos.columns))

def resumen_estadistico(datos):
    if datos is None:
        print("\nPrimero carga los datos (opción 1).")
        return
    print("\n--- RESUMEN ESTADÍSTICO (numéricas y categóricas) ---")
    print(datos.describe(include="all"))

if __name__ == "__main__":
    datos = None
    while True:
        opcion = menu()

        if opcion == "1":
            datos = cargar_datos()
        elif opcion == "2":
            mostrar_primeros(datos)
        elif opcion == "3":
            mostrar_informacion(datos)
        elif opcion == "4":
            resumen_estadistico(datos)
        elif opcion == "0":
            print("\nSaliendo del sistema. ¡Gracias!")
            break
        else:
            print("\nOpción inválida, intenta de nuevo.")
