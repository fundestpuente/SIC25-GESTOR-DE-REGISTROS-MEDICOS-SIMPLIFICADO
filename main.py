import pandas as pd
import numpy as np
from datetime import datetime
import os
import json


class SIRAM:
    def __init__(self):
        self.datos = None
        self.nombre_sistema = "SIRAM"
        self.descripcion = "Sistema Integrado de Registro y Análisis Médico"
        self.version = "v2.0"
        self.archivo_principal = "base_datos_medicos.csv"
        self.archivo_origen = "datos_procesados.csv"
        self.archivo_backup = "backup_medicos.json"
        
        # Configuración de pandas para mejor visualización
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 180)
        pd.set_option("display.max_colwidth", 60)
        pd.set_option('display.float_format', '{:,.2f}'.format)

    # ==============================
    # CARGA Y CREACIÓN DE DATOS
    # ==============================
    def cargar_datos(self):
        print(f"\n📂 {self.nombre_sistema} - Cargando base de datos...")

        # Si no existe la base principal, intentar crearla desde datos_procesados.csv
        if not os.path.exists(self.archivo_principal):
            if os.path.exists(self.archivo_origen):
                print("⚙️ No se encontró base principal. Creando desde datos_procesados.csv ...")
                self.crear_base_desde_datos_procesados()
            else:
                print("❌ No se encontró ninguna base de datos disponible.")
                self.crear_base_vacia()
                return self.datos

        # Cargar base principal
        try:
            self.datos = pd.read_csv(self.archivo_principal)

            # Convertir fechas
            columnas_fecha = [
                'dia_programado', 'dia_cita', 
                'fecha_consulta', 'fecha_registro'
            ]
            for col in columnas_fecha:
                if col in self.datos.columns:
                    self.datos[col] = pd.to_datetime(self.datos[col], errors='coerce')

            print(f"✅ Base '{self.archivo_principal}' cargada correctamente ({len(self.datos):,} registros)")
            return self.datos
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
            return None

    def crear_base_desde_datos_procesados(self):
        """Convierte datos_procesados.csv en la base extendida de SIRAM"""
        try:
            df = pd.read_csv(self.archivo_origen)

            # Asegurar columnas requeridas
            columnas_requeridas = [
                'id_paciente', 'id_cita', 'genero', 'dia_programado', 'dia_cita',
                'edad', 'vecindario', 'beca', 'hipertension', 'diabetes',
                'alcoholismo', 'discapacidad', 'sms_recibido', 'asistio'
            ]

            for col in columnas_requeridas:
                if col not in df.columns:
                    df[col] = np.nan

            # Añadir columnas nuevas si no existen
            columnas_nuevas = [
                'nombre', 'apellido', 'motivo_consulta', 'diagnostico',
                'tratamiento', 'medico_tratante', 'prioridad', 'estado',
                'observaciones', 'fecha_registro', 'fecha_consulta'
            ]
            for col in columnas_nuevas:
                if col not in df.columns:
                    df[col] = ""

            # Establecer formato de fechas
            hoy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'fecha_registro' in df.columns:
                df['fecha_registro'] = hoy
            if 'fecha_consulta' in df.columns:
                df['fecha_consulta'] = pd.to_datetime(df['dia_cita'], errors='coerce')

            df.to_csv(self.archivo_principal, index=False)
            self.datos = df
            print(f"✅ Base '{self.archivo_principal}' creada correctamente desde '{self.archivo_origen}'.")
            print(f"📊 Se migraron {len(df):,} registros históricos.")
        except Exception as e:
            print(f"❌ Error al crear base desde datos_procesados.csv: {e}")
            self.crear_base_vacia()

    def crear_base_vacia(self):
        columnas = [
            'id_paciente', 'id_cita', 'genero', 'dia_programado', 'dia_cita', 'edad',
            'vecindario', 'beca', 'hipertension', 'diabetes', 'alcoholismo',
            'discapacidad', 'sms_recibido', 'asistio', 'nombre', 'apellido',
            'fecha_registro', 'fecha_consulta', 'motivo_consulta', 'diagnostico',
            'tratamiento', 'medico_tratante', 'prioridad', 'estado', 'observaciones'
        ]
        self.datos = pd.DataFrame(columns=columnas)
        self.guardar_base_datos()
        print("✅ Base médica vacía creada.")

    # ==============================
    # GUARDADO Y BACKUP
    # ==============================
    def guardar_base_datos(self):
        try:
            self.datos.to_csv(self.archivo_principal, index=False)
            backup = {
                "fecha_backup": datetime.now().isoformat(),
                "total_registros": len(self.datos)
            }
            with open(self.archivo_backup, 'w') as f:
                json.dump(backup, f, indent=2)
            print("💾 Base de datos guardada correctamente.")
        except Exception as e:
            print(f"❌ Error al guardar base de datos: {e}")

    # ==============================
    # REGISTRO DE NUEVAS CITAS
    # ==============================
    def registrar_nueva_cita(self):
        if self.datos is None or len(self.datos) == 0:
            print("⚠️ No hay base cargada.")
            return

        print("\n🩺 REGISTRO DE NUEVA CITA EN SIRAM")
        id_paciente_input = input("Ingrese ID del paciente (o deje vacío para nuevo): ").strip()

        if id_paciente_input:
            try:
                id_paciente = float(id_paciente_input)
            except:
                print("❌ ID inválido.")
                return
            paciente = self.datos[self.datos['id_paciente'] == id_paciente]
        else:
            paciente = pd.DataFrame()

        if paciente.empty:
            print("⚙️ No se encontró paciente. Se creará uno nuevo.")
            id_paciente = float(datetime.now().timestamp() * 1e6)
            nombre = input("Nombre: ").strip().title()
            apellido = input("Apellido: ").strip().title()
            genero = input("Género (M/F/Otros): ").strip().upper() or "No especificado"
            edad = int(input("Edad: ") or 0)
            vecindario = input("Vecindario: ").strip().title()
        else:
            p = paciente.iloc[0]
            nombre = p.get('nombre', '')
            apellido = p.get('apellido', '')
            genero = p.get('genero', '')
            edad = p.get('edad', '')
            vecindario = p.get('vecindario', '')
            print(f"✅ Paciente encontrado: {nombre} {apellido} (ID: {int(id_paciente)})")

        motivo = input("Motivo de consulta: ").strip()
        diagnostico = input("Diagnóstico: ").strip()
        tratamiento = input("Tratamiento: ").strip()
        prioridad = input("Prioridad (Baja/Media/Alta/Urgente): ").strip().title() or "Media"
        medico = input("Médico tratante: ").strip()

        # Registrar fechas
        dia_programado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dia_cita_input = input("Fecha y hora de la cita (YYYY-MM-DD HH:MM): ").strip()

        try:
            dia_cita = datetime.strptime(dia_cita_input, '%Y-%m-%d %H:%M')
        except ValueError:
            print("❌ Formato de fecha incorrecto. Use 'YYYY-MM-DD HH:MM'")
            return

        # Verificar colisión
        existe_cita = self.datos[
            self.datos['dia_cita'].astype(str) == dia_cita.strftime('%Y-%m-%d %H:%M:%S')
        ]

        if not existe_cita.empty:
            print("⚠️ Ya existe una cita registrada en esa fecha y hora. Intente con otro horario.")
            return

        # Crear registro nuevo
        id_cita = int(datetime.now().timestamp() * 1e6)

        nueva_cita = {
            'id_paciente': id_paciente,
            'id_cita': id_cita,
            'genero': genero,
            'dia_programado': dia_programado,
            'dia_cita': dia_cita,
            'edad': edad,
            'vecindario': vecindario,
            'beca': 0,
            'hipertension': 0,
            'diabetes': 0,
            'alcoholismo': 0,
            'discapacidad': 0,
            'sms_recibido': 0,
            'asistio': 0,
            'nombre': nombre,
            'apellido': apellido,
            'fecha_registro': dia_programado,
            'fecha_consulta': dia_cita,
            'motivo_consulta': motivo,
            'diagnostico': diagnostico,
            'tratamiento': tratamiento,
            'medico_tratante': medico,
            'prioridad': prioridad,
            'estado': 'Activo',
            'observaciones': ''
        }

        self.datos = pd.concat([self.datos, pd.DataFrame([nueva_cita])], ignore_index=True)
        self.guardar_base_datos()
        print(f"🎉 Nueva cita registrada exitosamente (ID cita: {id_cita}).")

    # ==============================
    # ANÁLISIS ESTADÍSTICO
    # ==============================
    def mostrar_primeros_registros(self):
        if self.datos is None:
            print("\n⚠️ Primero carga los datos (Opción 1).")
            return
        print(f"\n--- PRIMEROS 20 REGISTROS ({len(self.datos):,} totales) ---")
        print(self.datos.head(20))

    def mostrar_informacion_general(self):
        if self.datos is None:
            print("\n⚠️ Primero carga los datos (Opción 1).")
            return
        print("\n--- INFORMACIÓN GENERAL DEL ARCHIVO ---")
        print(f"📊 Número total de registros: {len(self.datos):,}")
        print(f"🎯 Total de columnas: {len(self.datos.columns)}")
        print("\n📋 Columnas disponibles:")
        for i, col in enumerate(self.datos.columns, 1):
            print(f"   {i:2d}. {col}")

    def resumen_estadistico(self):
        if self.datos is None:
            print("\n⚠️ Primero carga los datos (Opción 1).")
            return
        print("\n--- RESUMEN ESTADÍSTICO COMPLETO ---")
        print("📈 Estadísticas descriptivas (variables numéricas y categóricas):")
        print(self.datos.describe(include="all"))

    def analisis_avanzado(self):
        if self.datos is None:
            print("\n⚠️ Primero carga los datos (Opción 1).")
            return
        
        print(f"\n📊 {self.nombre_sistema} - ANÁLISIS AVANZADO")
        print("=" * 60)
        
        # Análisis de asistencias
        if 'asistio' in self.datos.columns:
            total_citas = len(self.datos)
            asistencias = self.datos['asistio'].sum()
            tasa_asistencia = (asistencias / total_citas) * 100
            print(f"🎯 ASISTENCIA A CITAS:")
            print(f"   • Total citas programadas: {total_citas:,}")
            print(f"   • Citas atendidas: {asistencias:,}")
            print(f"   • Tasa de asistencia: {tasa_asistencia:.1f}%")
        
        # Análisis por género
        if 'genero' in self.datos.columns:
            print(f"\n👥 DISTRIBUCIÓN POR GÉNERO:")
            distribucion_genero = self.datos['genero'].value_counts()
            for genero, cantidad in distribucion_genero.items():
                porcentaje = (cantidad / len(self.datos)) * 100
                print(f"   • {genero}: {cantidad:,} ({porcentaje:.1f}%)")
        
        # Análisis por edad
        if 'edad' in self.datos.columns:
            print(f"\n📅 DISTRIBUCIÓN POR EDAD:")
            print(f"   • Edad promedio: {self.datos['edad'].mean():.1f} años")
            print(f"   • Edad mínima: {self.datos['edad'].min()} años")
            print(f"   • Edad máxima: {self.datos['edad'].max()} años")
        
        # Análisis de condiciones médicas
        condiciones = ['hipertension', 'diabetes', 'alcoholismo', 'discapacidad']
        condiciones_presentes = [cond for cond in condiciones if cond in self.datos.columns]
        
        if condiciones_presentes:
            print(f"\n🏥 PREVALENCIA DE CONDICIONES MÉDICAS:")
            for cond in condiciones_presentes:
                total = self.datos[cond].sum()
                porcentaje = (total / len(self.datos)) * 100
                print(f"   • {cond.title()}: {total:,} ({porcentaje:.1f}%)")

    def dashboard_estadistico(self):
        if self.datos is None:
            print("\n⚠️ Primero carga los datos (Opción 1).")
            return
        
        print(f"\n📈 {self.nombre_sistema} - DASHBOARD ESTADÍSTICO")
        print("=" * 70)
        
        # Información general
        print("🎯 INFORMACIÓN GENERAL:")
        print(f"   • 📊 Total de registros: {len(self.datos):,}")
        print(f"   • 📅 Rango temporal: {self.obtener_rango_temporal()}")
        print(f"   • 🎯 Variables analizables: {len(self.datos.columns)}")
        
        # Tipos de datos
        numeric_cols = self.datos.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.datos.select_dtypes(include=['object']).columns.tolist()
        date_cols = self.datos.select_dtypes(include=['datetime64']).columns.tolist()
        
        print(f"\n🔧 ESTRUCTURA DE DATOS:")
        print(f"   • 🔢 Variables numéricas: {len(numeric_cols)}")
        print(f"   • 📝 Variables categóricas: {len(categorical_cols)}")
        print(f"   • 📅 Variables de fecha: {len(date_cols)}")
        
        # Calidad de datos
        print(f"\n✅ CALIDAD DE DATOS:")
        total_cells = self.datos.size
        missing_cells = self.datos.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        print(f"   • 📈 Completitud de datos: {completeness:.1f}%")
        print(f"   • ⚠️  Valores faltantes: {missing_cells:,}")

    def obtener_rango_temporal(self):
        """Obtiene el rango temporal de las consultas"""
        date_cols = ['dia_cita', 'fecha_consulta', 'dia_programado']
        for col in date_cols:
            if col in self.datos.columns:
                fechas = pd.to_datetime(self.datos[col], errors='coerce')
                if not fechas.isna().all():
                    min_fecha = fechas.min()
                    max_fecha = fechas.max()
                    if pd.notna(min_fecha) and pd.notna(max_fecha):
                        return f"{min_fecha.strftime('%Y-%m-%d')} a {max_fecha.strftime('%Y-%m-%d')}"
        return "No disponible"

    # ==============================
    # MENÚ PRINCIPAL MEJORADO
    # ==============================
    def menu_principal(self):
        while True:
            print(f"\n{'='*70}")
            print(f"🏥 {self.nombre_sistema} – {self.descripcion} {self.version}")
            print(f"{'='*70}")
            print("📊 MÓDULO DE ANÁLISIS ESTADÍSTICO:")
            print("   1️⃣  Cargar/Crear base de datos")
            print("   2️⃣  Mostrar primeros 20 registros")
            print("   3️⃣  Información general del archivo")
            print("   4️⃣  Resumen estadístico completo")
            print("   5️⃣  Dashboard estadístico")
            print("   6️⃣  Análisis avanzado")
            print(f"{'-'*70}")
            print("🩺 MÓDULO DE REGISTRO MÉDICO:")
            print("   7️⃣  Registrar nueva cita")
            print("   8️⃣  Buscar paciente")
            print(f"{'-'*70}")
            print("   0️⃣  Salir del sistema")
            print(f"{'='*70}")

            opcion = input("\n🎯 Seleccione una opción: ").strip()

            if opcion == "1":
                self.cargar_datos()
            elif opcion == "2":
                self.mostrar_primeros_registros()
            elif opcion == "3":
                self.mostrar_informacion_general()
            elif opcion == "4":
                self.resumen_estadistico()
            elif opcion == "5":
                self.dashboard_estadistico()
            elif opcion == "6":
                self.analisis_avanzado()
            elif opcion == "7":
                self.registrar_nueva_cita()
            elif opcion == "8":
                self.buscar_paciente()
            elif opcion == "0":
                print(f"\n👋 Saliendo de {self.nombre_sistema}. ¡Gracias por usar nuestro sistema!")
                break
            else:
                print("❌ Opción no válida. Intente de nuevo.")
            
            input("\n⏎ Presione Enter para continuar...")

    def buscar_paciente(self):
        if self.datos is None:
            print("⚠️ No hay base cargada.")
            return
        
        print("\n🔍 BUSCAR PACIENTE")
        criterio = input("Buscar por (nombre/apellido/id): ").strip().lower()
        
        if criterio in ['nombre', 'apellido']:
            valor = input(f"Ingrese {criterio}: ").strip().title()
            resultados = self.datos[self.datos[criterio].str.contains(valor, na=False)]
        elif criterio == 'id':
            try:
                valor = float(input("Ingrese ID paciente: ").strip())
                resultados = self.datos[self.datos['id_paciente'] == valor]
            except:
                print("❌ ID inválido.")
                return
        else:
            print("❌ Criterio no válido.")
            return
        
        if resultados.empty:
            print("❌ No se encontraron resultados.")
        else:
            print(f"\n✅ Se encontraron {len(resultados)} resultados:")
            print(resultados[['id_paciente', 'nombre', 'apellido', 'edad', 'genero', 'vecindario']].to_string(index=False))


# ==============================
# EJECUCIÓN DEL SISTEMA
# ==============================
if __name__ == "__main__":
    app = SIRAM()
    app.menu_principal()
