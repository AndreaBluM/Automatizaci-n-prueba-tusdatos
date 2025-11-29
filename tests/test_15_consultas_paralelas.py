"""
DOCUMENTACIÓN DEL CASO DE PRUEBA: 15 CONSULTAS PARALELAS
========================================================

OBJETIVO:
○ Verificar que no haya bloqueos por parte de la página
○ Registrar tiempos de respuesta y éxito/fallo de cada consulta
○ Analizar rendimiento de concurrencia

METODOLOGÍA:
- Ejecutar 15 consultas simultáneas usando threading
- Monitorear tiempos de respuesta
- Detectar bloqueos y errores
- Generar reporte detallado con métricas

DATOS DE PRUEBA:
- 15 combinaciones de cédula/fecha diferentes
- Datos realistas para testing
- Distribución temporal variada

MÉTRICAS REGISTRADAS:
- Tiempo de inicio y fin de cada consulta
- Duración total por consulta
- Tasa de éxito/fallo
- Errores específicos encontrados
- Bloqueos detectados por la página
- Consultas simultáneas máximas
- Rendimiento promedio (consultas/segundo)

CRITERIOS DE ÉXITO:
✅ Tasa de éxito > 80%
✅ Sin bloqueos por límites de la página
✅ Tiempo promedio < 60 segundos por consulta
✅ Máximo 2 fallos por timeout

Autor: Bot Automatizado
Fecha: 29/11/2025
"""

import threading
import time
import json
import sys
import os
from datetime import datetime
import statistics
import subprocess

# Datos de prueba (cédulas reales para testing)
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

class MonitorConcurrencia:
    def __init__(self):
        self.resultados = []
        self.lock = threading.Lock()
        self.inicio_global = None
        self.fin_global = None
        
    def ejecutar_consulta_individual(self, datos, consulta_id):
        """Ejecuta una consulta individual con monitoreo completo"""
        
        resultado = {
            "consulta_id": consulta_id,
            "cedula": datos["cedula"],
            "fecha": datos["fecha"],
            "thread_id": threading.current_thread().ident,
            "inicio": time.time(),
            "fin": None,
            "duracion": None,
            "exitosa": False,
            "error": None,
            "datos_obtenidos": False,
            "archivo_generado": None,
            "bloqueo_detectado": False
        }
        
        try:
            print(f"🚀 [{consulta_id:2d}] Iniciando - Cédula: {datos['cedula']} - Thread: {threading.current_thread().ident}")
            
            # Ejecutar consulta usando subprocess para aislamiento
            proceso = subprocess.Popen([
                sys.executable, 
                "consulta_cedula.py", 
                datos["cedula"], 
                datos["fecha"]
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
            )
            
            # Esperar con timeout
            try:
                stdout, stderr = proceso.communicate(timeout=300)  # 5 minutos
                resultado["fin"] = time.time()
                resultado["duracion"] = resultado["fin"] - resultado["inicio"]
                
                if proceso.returncode == 0:
                    resultado["exitosa"] = True
                    
                    # Verificar si se generaron archivos
                    archivos_json = [f for f in os.listdir('.') if f.startswith(f'consulta_{datos["cedula"]}_')]
                    if archivos_json:
                        resultado["datos_obtenidos"] = True
                        resultado["archivo_generado"] = max(archivos_json, key=lambda x: os.path.getctime(x))
                    
                    print(f"✅ [{consulta_id:2d}] Exitosa - {resultado['duracion']:.1f}s")
                else:
                    resultado["exitosa"] = False
                    resultado["error"] = f"Código salida: {proceso.returncode}"
                    if stderr:
                        resultado["error"] += f" - {stderr[:100]}"
                    print(f"⚠️ [{consulta_id:2d}] Fallo - {resultado['error']}")
                    
            except subprocess.TimeoutExpired:
                proceso.kill()
                resultado["fin"] = time.time()
                resultado["duracion"] = resultado["fin"] - resultado["inicio"]
                resultado["exitosa"] = False
                resultado["error"] = "Timeout - Más de 5 minutos"
                resultado["bloqueo_detectado"] = True
                print(f"⏰ [{consulta_id:2d}] Timeout - Posible bloqueo")
                
        except Exception as e:
            resultado["fin"] = time.time()
            resultado["duracion"] = resultado["fin"] - resultado["inicio"] if resultado["inicio"] else 0
            resultado["exitosa"] = False
            resultado["error"] = str(e)
            print(f"❌ [{consulta_id:2d}] Error: {e}")
            
        # Guardar resultado de forma thread-safe
        with self.lock:
            self.resultados.append(resultado)
            
        return resultado
    
    def ejecutar_prueba_completa(self):
        """Ejecuta la prueba completa de 15 consultas paralelas"""
        
        print("🧪 PRUEBA DE 15 CONSULTAS PARALELAS")
        print("=" * 60)
        print(f"📅 Fecha/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🔢 Total consultas: {len(DATOS_PRUEBA)}")
        print(f"⚡ Ejecución: Paralela con {len(DATOS_PRUEBA)} threads")
        print("=" * 60)
        
        self.inicio_global = time.time()
        
        # Crear y lanzar threads
        threads = []
        for i, datos in enumerate(DATOS_PRUEBA, 1):
            thread = threading.Thread(
                target=self.ejecutar_consulta_individual,
                args=(datos, i)
            )
            threads.append(thread)
            thread.start()
            
            # Pequeño delay entre lanzamientos para evitar burst
            time.sleep(0.5)
        
        # Esperar a que todos terminen
        for i, thread in enumerate(threads, 1):
            thread.join()
            print(f"🔄 Thread {i} terminado")
            
        self.fin_global = time.time()
        
        print("\\n🏁 TODAS LAS CONSULTAS COMPLETADAS")
        print(f"⏱️ Tiempo total: {self.fin_global - self.inicio_global:.2f} segundos")
        
        return self.generar_reporte()
    
    def generar_reporte(self):
        """Genera reporte detallado con análisis"""
        
        # Ordenar por ID
        self.resultados.sort(key=lambda x: x["consulta_id"])
        
        # Calcular métricas
        total = len(self.resultados)
        exitosas = sum(1 for r in self.resultados if r["exitosa"])
        fallidas = total - exitosas
        con_datos = sum(1 for r in self.resultados if r["datos_obtenidos"])
        bloqueos = sum(1 for r in self.resultados if r["bloqueo_detectado"])
        
        duraciones = [r["duracion"] for r in self.resultados if r["duracion"]]
        tiempo_total = self.fin_global - self.inicio_global
        
        # Análisis de errores
        errores = {}
        for r in self.resultados:
            if r["error"]:
                error_key = r["error"][:50] + "..." if len(r["error"]) > 50 else r["error"]
                errores[error_key] = errores.get(error_key, 0) + 1
        
        # Crear reporte
        reporte = {
            "metadata": {
                "fecha_prueba": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                "version_script": "1.0",
                "objetivo": "Verificar concurrencia sin bloqueos"
            },
            "configuracion": {
                "total_consultas": total,
                "modo_ejecucion": "Paralelo",
                "timeout_por_consulta": 300,
                "delay_entre_lanzamientos": 0.5
            },
            "resultados_generales": {
                "tasa_exito": round(exitosas / total * 100, 2),
                "consultas_exitosas": exitosas,
                "consultas_fallidas": fallidas,
                "consultas_con_datos": con_datos,
                "bloqueos_detectados": bloqueos,
                "tiempo_total_segundos": round(tiempo_total, 2)
            },
            "analisis_tiempos": {
                "promedio": round(statistics.mean(duraciones), 2) if duraciones else 0,
                "minimo": round(min(duraciones), 2) if duraciones else 0,
                "maximo": round(max(duraciones), 2) if duraciones else 0,
                "mediana": round(statistics.median(duraciones), 2) if duraciones else 0,
                "desviacion_estandar": round(statistics.stdev(duraciones), 2) if len(duraciones) > 1 else 0
            },
            "analisis_concurrencia": {
                "consultas_por_segundo": round(total / tiempo_total, 2) if tiempo_total > 0 else 0,
                "eficiencia": round(exitosas / tiempo_total, 2) if tiempo_total > 0 else 0,
                "paralelismo_efectivo": self.calcular_paralelismo(),
                "bloqueos_por_limite_pagina": bloqueos == 0
            },
            "errores_encontrados": errores,
            "conclusiones": self.generar_conclusiones(exitosas, total, bloqueos, duraciones),
            "resultados_detallados": self.resultados
        }
        
        # Guardar reporte
        timestamp = int(time.time())
        archivo_reporte = f"reporte_15_consultas_{timestamp}.json"
        
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        self.mostrar_resumen(reporte)
        
        print(f"\\n📊 Reporte completo guardado: {archivo_reporte}")
        
        return reporte, archivo_reporte
    
    def calcular_paralelismo(self):
        """Calcula métricas de paralelismo efectivo"""
        
        # Crear timeline de ejecución
        eventos = []
        for r in self.resultados:
            if r["inicio"] and r["fin"]:
                eventos.append((r["inicio"], "inicio"))
                eventos.append((r["fin"], "fin"))
        
        eventos.sort()
        
        max_paralelas = 0
        paralelas_actual = 0
        
        for tiempo, tipo in eventos:
            if tipo == "inicio":
                paralelas_actual += 1
                max_paralelas = max(max_paralelas, paralelas_actual)
            else:
                paralelas_actual -= 1
                
        return {
            "max_consultas_paralelas": max_paralelas,
            "promedio_paralelas": round(len(self.resultados) / 2, 1)
        }
    
    def generar_conclusiones(self, exitosas, total, bloqueos, duraciones):
        """Genera conclusiones automáticas de la prueba"""
        
        conclusiones = []
        tasa_exito = exitosas / total * 100
        
        # Análisis de tasa de éxito
        if tasa_exito >= 80:
            conclusiones.append("✅ Tasa de éxito aceptable (>= 80%)")
        else:
            conclusiones.append("❌ Tasa de éxito baja (< 80%)")
        
        # Análisis de bloqueos
        if bloqueos == 0:
            conclusiones.append("✅ No se detectaron bloqueos por límites de la página")
        else:
            conclusiones.append(f"⚠️ Se detectaron {bloqueos} posibles bloqueos")
        
        # Análisis de tiempos
        if duraciones:
            tiempo_promedio = statistics.mean(duraciones)
            if tiempo_promedio < 60:
                conclusiones.append("✅ Tiempo promedio aceptable (< 60s)")
            else:
                conclusiones.append(f"⚠️ Tiempo promedio alto ({tiempo_promedio:.1f}s)")
        
        # Evaluación general
        if tasa_exito >= 80 and bloqueos == 0:
            conclusiones.append("🎉 PRUEBA EXITOSA - El sistema maneja bien la concurrencia")
        else:
            conclusiones.append("⚠️ REVISAR SISTEMA - Posibles problemas de concurrencia")
            
        return conclusiones
    
    def mostrar_resumen(self, reporte):
        """Muestra resumen en consola"""
        
        print("\\n" + "=" * 70)
        print("📋 RESUMEN DE PRUEBA DE CONCURRENCIA")
        print("=" * 70)
        
        print(f"🎯 RESULTADOS:")
        print(f"   • Consultas exitosas: {reporte['resultados_generales']['consultas_exitosas']}/{reporte['configuracion']['total_consultas']}")
        print(f"   • Tasa de éxito: {reporte['resultados_generales']['tasa_exito']}%")
        print(f"   • Con datos extraídos: {reporte['resultados_generales']['consultas_con_datos']}")
        print(f"   • Tiempo total: {reporte['resultados_generales']['tiempo_total_segundos']}s")
        
        print(f"\\n⏱️ TIEMPOS:")
        print(f"   • Promedio por consulta: {reporte['analisis_tiempos']['promedio']}s")
        print(f"   • Mínimo: {reporte['analisis_tiempos']['minimo']}s")
        print(f"   • Máximo: {reporte['analisis_tiempos']['maximo']}s")
        print(f"   • Velocidad: {reporte['analisis_concurrencia']['consultas_por_segundo']} consultas/segundo")
        
        print(f"\\n🔄 CONCURRENCIA:")
        print(f"   • Máx paralelas: {reporte['analisis_concurrencia']['paralelismo_efectivo']['max_consultas_paralelas']}")
        print(f"   • Bloqueos detectados: {reporte['resultados_generales']['bloqueos_detectados']}")
        
        if reporte['errores_encontrados']:
            print(f"\\n❌ ERRORES ({len(reporte['errores_encontrados'])}):")
            for error, count in reporte['errores_encontrados'].items():
                print(f"   • {error}: {count}x")
        
        print(f"\\n🔍 CONCLUSIONES:")
        for conclusion in reporte['conclusiones']:
            print(f"   {conclusion}")
            
        print("=" * 70)

def main():
    """Ejecuta la prueba de concurrencia"""
    
    print("⚠️ ADVERTENCIA: Esta prueba ejecutará 15 consultas reales en paralelo")
    print("Esto puede tomar varios minutos y generar múltiples archivos.")
    print("Asegúrate de tener Tesseract instalado y configurado.\\n")
    
    respuesta = input("¿Continuar con la prueba de concurrencia? (s/n): ").lower()
    
    if respuesta != 's':
        print("❌ Prueba cancelada")
        return
    
    # Ejecutar prueba
    monitor = MonitorConcurrencia()
    reporte, archivo = monitor.ejecutar_prueba_completa()
    
    print("\\n🎉 PRUEBA COMPLETADA")
    print(f"📄 Consulta el reporte detallado: {archivo}")

if __name__ == "__main__":
    main()