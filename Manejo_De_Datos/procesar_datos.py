import pandas as pd


ARCHIVO_ENTRADA = './KaggleV2-May-2016.csv'  # Archivo original sin procesar
ARCHIVO_SALIDA = './Datos_Procesados/datos_procesados.csv'   # Archivo limpio generado
 

def cargar_datos():
    """
    Carga el archivo CSV original en un DataFrame de Pandas.
    Si ocurre un error, muestra un mensaje explicativo.
    """
    try:
        df = pd.read_csv(ARCHIVO_ENTRADA)
        print(f"Archivo '{ARCHIVO_ENTRADA}' cargado correctamente.\n")
        return df
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ARCHIVO_ENTRADA}'. "
              "Asegúrate de que esté en la misma carpeta que este script.")
        return None
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None


# ======================================================
# FUNCIÓN 2: Limpieza y estructuración de datos
# ======================================================
def limpiar_datos(df):
    """
    Realiza la limpieza y estandarización de los datos médicos:
      - Renombrar columnas
      - Conversión de fechas
      - Cálculo de días de espera
      - Codificación de asistencia (Yes/No = 0/1)
      - Eliminación de edades inválidas
    """
    # Diccionario de renombrado (inglés → español)
    renombrar_columnas = {
        'PatientId': 'id_paciente',
        'AppointmentID': 'id_cita',
        'Gender': 'genero',
        'ScheduledDay': 'dia_programado',
        'AppointmentDay': 'dia_cita',
        'Age': 'edad',
        'Neighbourhood': 'vecindario',
        'Scholarship': 'beca',
        'Hipertension': 'hipertension',
        'Diabetes': 'diabetes',
        'Alcoholism': 'alcoholismo',
        'Handcap': 'discapacidad',
        'SMS_received': 'sms_recibido',
        'No-show': 'se_presento'
    }

    # Renombrar columnas
    df.rename(columns=renombrar_columnas, inplace=True)

    # Convertir columnas de fechas
    df['dia_programado'] = pd.to_datetime(df['dia_programado'])
    df['dia_cita'] = pd.to_datetime(df['dia_cita'])

    # Normalizar columna asistencia
    df['se_presento'] = df['se_presento'].str.strip().str.upper()
    df['asistio'] = df['se_presento'].apply(lambda x: 1 if x == 'YES' else 0)
    df.drop(columns=['se_presento'], inplace=True)


    # Filtrar edades inválidas
    registros_iniciales = len(df)
    df = df[(df['edad'] >= 0) & (df['edad'] <= 100)]
    registros_eliminados = registros_iniciales - len(df)

    print(f"Limpieza completada. Registros eliminados: {registros_eliminados}\n")
    return df



# ======================================================
# FUNCIÓN 3: Guardar los datos procesados
# ======================================================
def guardar_datos(df):
    """
    Guarda el DataFrame limpio como un nuevo archivo CSV.
    """
    try:
        df.to_csv(ARCHIVO_SALIDA, index=False)
        print(f"Datos procesados guardados exitosamente como '{ARCHIVO_SALIDA}'.")
    except Exception as e:
        print(f"Error al guardar los datos procesados: {e}")



if __name__ == "__main__":
    datos_originales = cargar_datos()

    if datos_originales is not None:
        datos_limpios = limpiar_datos(datos_originales)
        guardar_datos(datos_limpios)