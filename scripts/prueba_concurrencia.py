"""
CASO DE PRUEBA: 15 CONSULTAS PARALELAS
=====================================

Este script ejecuta 15 consultas paralelas para verificar:
○ No hay bloqueos por parte de la página
○ Registrar tiempos de respuesta y éxito/fallo de cada consulta
○ Análisis de rendimiento y concurrencia

Autor: Bot Automatizado
Fecha: 29/11/2025
"""

import concurrent.futures
import threading
import time
import json
import sys
import os
from datetime import datetime
import statistics

# Importar el módulo principal
sys.path.append('.')

# Datos de prueba (cédulas y fechas reales para testing)
DATOS_PRUEBA = [
    {"cedula": "1036670248", "fecha": "08/01/2015"},
    {"cedula": "1018505654", "fecha": "15/05/1991"},
    {"cedula": "1234567890", "fecha": "01/01/2000"},
    {"cedula": "9876543210", "fecha": "15/12/1995"},
    {"cedula": "1111111111", "fecha": "20/06/1990"},
    {"cedula": "2222222222", "fecha": "10/03/1985"},
    {"cedula": "3333333333", "fecha": "25/08/1992"},
    {"cedula": "4444444444", "fecha": "05/11/1988"},
    {"cedula": "5555555555", "fecha": "30/04/1993"},
    {"cedula": "6666666666", "fecha": "12/09/1987"},
    {"cedula": "7777777777", "fecha": "18/07/1994"},
    {"cedula": "8888888888", "fecha": "22/02/1989"},
    {"cedula": "9999999999", "fecha": "14/10/1996"},
    {"cedula": "1010101010", "fecha": "07/05/1991"},
    {"cedula": "2020202020", "fecha": "03/12/1986"}
]

class PruebaConcurrencia:
    """
    Clase para ejecutar y documentar pruebas de concurrencia
    """
    
    def __init__(self):
        self.resultados = []
        self.lock = threading.Lock()
        self.inicio_prueba = None
        self.fin_prueba = None
        
    def ejecutar_consulta_individual(self, datos, indice):
        """
        Ejecuta una consulta individual y registra métricas
        
        Args:
            datos (dict): {"cedula": "xxx", "fecha": "dd/mm/yyyy"}
            indice (int): Número de consulta (1-15)
            
        Returns:
            dict: Resultado con métricas de la consulta
        """
        
        resultado = {
            "consulta_id": indice,
            "cedula": datos["cedula"],
            "fecha": datos["fecha"],
            "inicio": None,
            "fin": None,
            "duracion": None,
            "exitosa": False,
            "error": None,
            "datos_extraidos": None,
            "archivo_pdf": None,
            "thread_id": threading.current_thread().ident
        }
        
        try:
            print(f"🚀 Iniciando consulta {indice} - Cédula: {datos['cedula']}")
            resultado["inicio"] = time.time()
            
            # Importar y ejecutar la consulta
            from consulta_cedula import ejecutar_consulta_completa
            
            # Ejecutar la consulta completa
            datos_resultado = ejecutar_consulta_completa(datos["cedula"], datos["fecha"])
            
            resultado["fin"] = time.time()
            resultado["duracion"] = resultado["fin"] - resultado["inicio"]
            
            if datos_resultado:
                resultado["exitosa"] = True
                resultado["datos_extraidos"] = datos_resultado
                if "archivo_pdf" in datos_resultado:
                    resultado["archivo_pdf"] = datos_resultado["archivo_pdf"]
                print(f"✅ Consulta {indice} exitosa - Duración: {resultado['duracion']:.2f}s")
            else:
                resultado["exitosa"] = False
                resultado["error"] = "No se obtuvieron datos"
                print(f"⚠️ Consulta {indice} sin datos - Duración: {resultado['duracion']:.2f}s")
                
        except Exception as e:
            resultado["fin"] = time.time() if resultado["inicio"] else time.time()
            resultado["duracion"] = resultado["fin"] - resultado["inicio"] if resultado["inicio"] else 0
            resultado["exitosa"] = False
            resultado["error"] = str(e)
            print(f"❌ Error en consulta {indice}: {e}")
            
        # Thread-safe append de resultados
        with self.lock:
            self.resultados.append(resultado)
            
        return resultado
    
    def ejecutar_pruebas_paralelas(self, max_workers=15):
        """
        Ejecuta las 15 consultas en paralelo
        
        Args:
            max_workers (int): Número máximo de hilos paralelos
        """
        
        print("🎯 INICIANDO PRUEBA DE 15 CONSULTAS PARALELAS")
        print("=" * 60)
        print(f"📊 Configuración:")
        print(f"   • Consultas paralelas: {len(DATOS_PRUEBA)}")
        print(f"   • Max workers: {max_workers}")
        print(f"   • Fecha/Hora inicio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        self.inicio_prueba = time.time()
        
        # Ejecutar consultas en paralelo usando ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Crear futures para cada consulta
            futures = {
                executor.submit(self.ejecutar_consulta_individual, datos, i+1): i+1 
                for i, datos in enumerate(DATOS_PRUEBA)
            }
            
            # Esperar a que todas las consultas terminen
            completed_count = 0
            for future in concurrent.futures.as_completed(futures):
                completed_count += 1
                consulta_id = futures[future]
                try:
                    resultado = future.result()
                    estado = "✅" if resultado["exitosa"] else "❌"
                    print(f"{estado} Consulta {consulta_id} completada ({completed_count}/{len(DATOS_PRUEBA)})")
                except Exception as e:
                    print(f"❌ Excepción en consulta {consulta_id}: {e}")
        
        self.fin_prueba = time.time()
        
        print("\\n🏁 TODAS LAS CONSULTAS COMPLETADAS")
        print(f"⏱️ Tiempo total: {self.fin_prueba - self.inicio_prueba:.2f} segundos")
    
    def generar_reporte_detallado(self):
        """
        Genera un reporte detallado con análisis de resultados
        """
        
        if not self.resultados:
            print("❌ No hay resultados para generar reporte")
            return None
            
        # Ordenar resultados por consulta_id
        self.resultados.sort(key=lambda x: x["consulta_id"])
        
        # Calcular métricas
        consultas_exitosas = [r for r in self.resultados if r["exitosa"]]
        consultas_fallidas = [r for r in self.resultados if not r["exitosa"]]
        
        duraciones = [r["duracion"] for r in self.resultados if r["duracion"]]
        
        tasa_exito = len(consultas_exitosas) / len(self.resultados) * 100
        tiempo_total = self.fin_prueba - self.inicio_prueba
        
        # Crear reporte
        reporte = {
            "fecha_prueba": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            "configuracion": {
                "total_consultas": len(self.resultados),
                "consultas_paralelas": len(DATOS_PRUEBA),
                "tiempo_total": tiempo_total
            },
            "metricas_generales": {
                "tasa_exito": tasa_exito,
                "consultas_exitosas": len(consultas_exitosas),
                "consultas_fallidas": len(consultas_fallidas),
                "tiempo_promedio": statistics.mean(duraciones) if duraciones else 0,
                "tiempo_minimo": min(duraciones) if duraciones else 0,
                "tiempo_maximo": max(duraciones) if duraciones else 0,
                "tiempo_mediana": statistics.median(duraciones) if duraciones else 0
            },
            "analisis_concurrencia": {
                "bloqueos_detectados": self.detectar_bloqueos(),
                "consultas_simultaneas": self.calcular_simultaneidad(),
                "rendimiento_por_segundo": len(self.resultados) / tiempo_total if tiempo_total > 0 else 0
            },
            "resultados_individuales": self.resultados,
            "errores_encontrados": self.analizar_errores()
        }
        
        # Guardar reporte en archivo
        timestamp = int(time.time())
        nombre_archivo = f"reporte_concurrencia_{timestamp}.json"
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📊 Reporte guardado en: {nombre_archivo}")
        
        # Mostrar resumen en consola
        self.mostrar_resumen_consola(reporte)
        
        return reporte
    
    def detectar_bloqueos(self):
        """
        Detecta posibles bloqueos analizando patrones en los tiempos
        """
        
        bloqueos = []
        
        # Buscar consultas que tardaron excesivamente
        duraciones = [r["duracion"] for r in self.resultados if r["duracion"]]
        if duraciones:
            promedio = statistics.mean(duraciones)
            umbral_bloqueo = promedio * 3  # 3 veces el promedio
            
            for resultado in self.resultados:
                if resultado["duracion"] and resultado["duracion"] > umbral_bloqueo:
                    bloqueos.append({
                        "consulta_id": resultado["consulta_id"],
                        "cedula": resultado["cedula"],
                        "duracion": resultado["duracion"],
                        "tipo": "Tiempo excesivo"
                    })
        
        # Buscar errores relacionados con bloqueos
        for resultado in self.resultados:
            if resultado["error"]:
                error_lower = resultado["error"].lower()
                if any(palabra in error_lower for palabra in ["timeout", "blocked", "rate limit", "too many"]):
                    bloqueos.append({
                        "consulta_id": resultado["consulta_id"],
                        "cedula": resultado["cedula"],
                        "error": resultado["error"],
                        "tipo": "Error de bloqueo"
                    })
        
        return bloqueos
    
    def calcular_simultaneidad(self):
        """
        Calcula métricas de simultaneidad
        """
        
        # Crear timeline de ejecución
        eventos = []
        for resultado in self.resultados:
            if resultado["inicio"] and resultado["fin"]:
                eventos.append({"tiempo": resultado["inicio"], "tipo": "inicio", "consulta_id": resultado["consulta_id"]})
                eventos.append({"tiempo": resultado["fin"], "tipo": "fin", "consulta_id": resultado["consulta_id"]})
        
        # Ordenar eventos por tiempo
        eventos.sort(key=lambda x: x["tiempo"])
        
        # Calcular simultaneidad máxima
        consultas_activas = 0
        max_simultaneas = 0
        
        for evento in eventos:
            if evento["tipo"] == "inicio":
                consultas_activas += 1
                max_simultaneas = max(max_simultaneas, consultas_activas)
            else:
                consultas_activas -= 1
        
        return {
            "max_consultas_simultaneas": max_simultaneas,
            "consultas_activas_promedio": len(self.resultados) / 2  # Aproximación
        }
    
    def analizar_errores(self):
        """
        Analiza y categoriza los errores encontrados
        """
        
        errores = {}
        for resultado in self.resultados:
            if resultado["error"]:
                error = resultado["error"]
                if error in errores:
                    errores[error] += 1
                else:
                    errores[error] = 1
        
        return errores
    
    def mostrar_resumen_consola(self, reporte):
        """
        Muestra un resumen del reporte en la consola
        """
        
        print("\\n" + "=" * 80)
        print("📋 REPORTE DE PRUEBA DE CONCURRENCIA")
        print("=" * 80)
        
        # Métricas generales
        print(f"🎯 RESULTADOS GENERALES:")
        print(f"   • Total consultas: {reporte['configuracion']['total_consultas']}")
        print(f"   • Tasa de éxito: {reporte['metricas_generales']['tasa_exito']:.1f}%")
        print(f"   • Exitosas: {reporte['metricas_generales']['consultas_exitosas']}")
        print(f"   • Fallidas: {reporte['metricas_generales']['consultas_fallidas']}")
        print(f"   • Tiempo total: {reporte['configuracion']['tiempo_total']:.2f}s")
        
        # Tiempos
        print(f"\\n⏱️ ANÁLISIS DE TIEMPOS:")
        print(f"   • Tiempo promedio: {reporte['metricas_generales']['tiempo_promedio']:.2f}s")
        print(f"   • Tiempo mínimo: {reporte['metricas_generales']['tiempo_minimo']:.2f}s")
        print(f"   • Tiempo máximo: {reporte['metricas_generales']['tiempo_maximo']:.2f}s")
        print(f"   • Mediana: {reporte['metricas_generales']['tiempo_mediana']:.2f}s")
        
        # Concurrencia
        print(f"\\n🔄 ANÁLISIS DE CONCURRENCIA:")
        print(f"   • Max consultas simultáneas: {reporte['analisis_concurrencia']['consultas_simultaneas']['max_consultas_simultaneas']}")
        print(f"   • Rendimiento: {reporte['analisis_concurrencia']['rendimiento_por_segundo']:.2f} consultas/segundo")
        
        # Bloqueos
        bloqueos = reporte['analisis_concurrencia']['bloqueos_detectados']
        if bloqueos:
            print(f"\\n⚠️ BLOQUEOS DETECTADOS: {len(bloqueos)}")
            for bloqueo in bloqueos:
                print(f"   • Consulta {bloqueo['consulta_id']}: {bloqueo['tipo']}")
        else:
            print(f"\\n✅ NO SE DETECTARON BLOQUEOS")
        
        # Errores
        errores = reporte['errores_encontrados']
        if errores:
            print(f"\\n❌ ERRORES ENCONTRADOS:")
            for error, count in errores.items():
                print(f"   • {error}: {count} veces")
        else:
            print(f"\\n✅ NO SE ENCONTRARON ERRORES")
        
        print("=" * 80)

def ejecutar_consulta_completa(cedula, fecha):
    """
    Función wrapper para ejecutar una consulta completa
    Esta función debe ser implementada en consulta_cedula.py
    """
    try:
        # Simulación temporal - reemplazar con la función real
        import subprocess
        import sys
        
        # Ejecutar el script principal con los parámetros
        resultado = subprocess.run([
            sys.executable, 
            "consulta_cedula.py", 
            cedula, 
            fecha
        ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
        
        if resultado.returncode == 0:
            # Buscar archivo JSON generado
            import glob
            archivos_json = glob.glob(f"consulta_{cedula}_*.json")
            if archivos_json:
                archivo_reciente = max(archivos_json, key=os.path.getctime)
                with open(archivo_reciente, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"exito": True, "mensaje": "Consulta completada"}
        else:
            return None
            
    except subprocess.TimeoutExpired:
        raise Exception("Timeout - Consulta tardó más de 5 minutos")
    except Exception as e:
        raise Exception(f"Error ejecutando consulta: {e}")

if __name__ == "__main__":
    print("🧪 CASO DE PRUEBA: 15 CONSULTAS PARALELAS")
    print("Verificando concurrencia y bloqueos...")
    print("\\n⚠️ IMPORTANTE: Este test ejecutará 15 consultas reales en paralelo")
    print("Esto puede tomar varios minutos y generar múltiples archivos.")
    
    respuesta = input("\\n¿Continuar con la prueba? (s/n): ").lower()
    
    if respuesta != 's':
        print("❌ Prueba cancelada por el usuario")
        sys.exit(0)
    
    # Ejecutar prueba
    prueba = PruebaConcurrencia()
    prueba.ejecutar_pruebas_paralelas()
    reporte = prueba.generar_reporte_detallado()
    
    print("\\n🎉 PRUEBA COMPLETADA")
    print("✅ Reporte generado con métricas detalladas")
    print("📁 Archivos generados en el directorio actual")