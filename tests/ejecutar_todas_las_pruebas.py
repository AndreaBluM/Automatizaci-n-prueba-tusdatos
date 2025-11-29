"""
SUITE COMPLETA DE PRUEBAS - Bot Registraduría Nacional
====================================================

Script maestro que ejecuta todas las pruebas del sistema:
- Pruebas unitarias para funciones individuales
- Pruebas de integración para flujo completo  
- Pruebas de concurrencia y performance
- Generación de reporte consolidado

Uso:
    python ejecutar_todas_las_pruebas.py
    python ejecutar_todas_las_pruebas.py --verbose
    python ejecutar_todas_las_pruebas.py --solo-unitarias
    python ejecutar_todas_las_pruebas.py --solo-integracion

Autor: Sistema Automatizado
Fecha: 29/11/2025
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime
import unittest

# Configurar paths
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos de prueba
try:
    from test_unitarios import ejecutar_suite_completa as ejecutar_unitarias
    from test_integracion import ejecutar_suite_integracion as ejecutar_integracion
    import test_unitarios
    import test_integracion
except ImportError as e:
    print(f"⚠️ Error importando módulos de prueba: {e}")
    sys.exit(1)

class ReportePruebasCompleto:
    """Generador de reportes consolidados de todas las pruebas"""
    
    def __init__(self):
        self.inicio_global = time.time()
        self.resultados = {
            "unitarias": None,
            "integracion": None,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ambiente": {
                "python_version": sys.version,
                "plataforma": sys.platform,
                "directorio": os.getcwd()
            }
        }
    
    def ejecutar_pruebas_unitarias(self, verbose=True):
        """Ejecuta suite de pruebas unitarias"""
        
        print("\n" + "🧪 " * 20)
        print("INICIANDO PRUEBAS UNITARIAS")
        print("🧪 " * 20 + "\n")
        
        inicio = time.time()
        
        # Crear loader y suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Cargar todas las pruebas unitarias
        clases_unitarias = [
            test_unitarios.TestValidacionArgumentos,
            test_unitarios.TestExtraccionHTML,
            test_unitarios.TestProcesamientoPDF,
            test_unitarios.TestDeteccionPDF,
            test_unitarios.TestDescargaPDF,
            test_unitarios.TestGuardadoDatos,
            test_unitarios.TestIntegracionCompleta
        ]
        
        for clase in clases_unitarias:
            suite.addTests(loader.loadTestsFromTestCase(clase))
        
        # Ejecutar pruebas
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            stream=sys.stdout,
            failfast=False
        )
        
        resultado = runner.run(suite)
        fin = time.time()
        
        # Procesar resultados
        self.resultados["unitarias"] = {
            "ejecutadas": resultado.testsRun,
            "exitosas": resultado.testsRun - len(resultado.errors) - len(resultado.failures),
            "errores": len(resultado.errors),
            "fallos": len(resultado.failures),
            "tiempo": fin - inicio,
            "tasa_exito": ((resultado.testsRun - len(resultado.errors) - len(resultado.failures)) / resultado.testsRun * 100) if resultado.testsRun > 0 else 0
        }
        
        return resultado.testsRun == (resultado.testsRun - len(resultado.errors) - len(resultado.failures))
    
    def ejecutar_pruebas_integracion(self, verbose=True):
        """Ejecuta suite de pruebas de integración"""
        
        print("\n" + "🔧 " * 20)
        print("INICIANDO PRUEBAS DE INTEGRACIÓN")
        print("🔧 " * 20 + "\n")
        
        inicio = time.time()
        
        # Crear loader y suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Cargar todas las pruebas de integración
        clases_integracion = [
            test_integracion.TestIntegracionFormulario,
            test_integracion.TestIntegracionCAPTCHA,
            test_integracion.TestIntegracionPDF,
            test_integracion.TestIntegracionDatos,
            test_integracion.TestIntegracionConcurrencia,
            test_integracion.TestIntegracionPerformance
        ]
        
        for clase in clases_integracion:
            suite.addTests(loader.loadTestsFromTestCase(clase))
        
        # Ejecutar pruebas
        runner = unittest.TextTestRunner(
            verbosity=2 if verbose else 1,
            stream=sys.stdout,
            failfast=False
        )
        
        resultado = runner.run(suite)
        fin = time.time()
        
        # Procesar resultados
        self.resultados["integracion"] = {
            "ejecutadas": resultado.testsRun,
            "exitosas": resultado.testsRun - len(resultado.errors) - len(resultado.failures),
            "errores": len(resultado.errors),
            "fallos": len(resultado.failures),
            "tiempo": fin - inicio,
            "tasa_exito": ((resultado.testsRun - len(resultado.errors) - len(resultado.failures)) / resultado.testsRun * 100) if resultado.testsRun > 0 else 0
        }
        
        return resultado.testsRun == (resultado.testsRun - len(resultado.errors) - len(resultado.failures))
    
    def generar_reporte_final(self):
        """Genera reporte consolidado final"""
        
        fin_global = time.time()
        tiempo_total = fin_global - self.inicio_global
        
        # Calcular totales
        total_ejecutadas = 0
        total_exitosas = 0 
        total_errores = 0
        total_fallos = 0
        
        for tipo in ["unitarias", "integracion"]:
            if self.resultados[tipo]:
                total_ejecutadas += self.resultados[tipo]["ejecutadas"]
                total_exitosas += self.resultados[tipo]["exitosas"]
                total_errores += self.resultados[tipo]["errores"] 
                total_fallos += self.resultados[tipo]["fallos"]
        
        tasa_exito_global = (total_exitosas / total_ejecutadas * 100) if total_ejecutadas > 0 else 0
        
        # Mostrar reporte en consola
        print("\n" + "=" * 80)
        print("📊 REPORTE CONSOLIDADO FINAL - TODAS LAS PRUEBAS")
        print("=" * 80)
        print(f"🕐 Timestamp: {self.resultados['timestamp']}")
        print(f"⏱️ Tiempo total de ejecución: {tiempo_total:.2f} segundos")
        print(f"🐍 Python: {self.resultados['ambiente']['python_version'].split()[0]}")
        print(f"💻 Plataforma: {self.resultados['ambiente']['plataforma']}")
        print("\n" + "-" * 50)
        
        # Detalles por tipo de prueba
        if self.resultados["unitarias"]:
            unit = self.resultados["unitarias"]
            print(f"🧪 PRUEBAS UNITARIAS:")
            print(f"   ✅ Exitosas: {unit['exitosas']}/{unit['ejecutadas']}")
            print(f"   ❌ Fallos: {unit['fallos']}")
            print(f"   💥 Errores: {unit['errores']}")
            print(f"   📈 Tasa éxito: {unit['tasa_exito']:.1f}%")
            print(f"   ⏱️ Tiempo: {unit['tiempo']:.2f}s")
        
        if self.resultados["integracion"]:
            integ = self.resultados["integracion"] 
            print("\n🔧 PRUEBAS DE INTEGRACIÓN:")
            print(f"   ✅ Exitosas: {integ['exitosas']}/{integ['ejecutadas']}")
            print(f"   ❌ Fallos: {integ['fallos']}")
            print(f"   💥 Errores: {integ['errores']}")
            print(f"   📈 Tasa éxito: {integ['tasa_exito']:.1f}%")
            print(f"   ⏱️ Tiempo: {integ['tiempo']:.2f}s")
        
        # Totales globales
        print("\n" + "-" * 50)
        print("🎯 RESUMEN GLOBAL:")
        print(f"   📊 Total pruebas: {total_ejecutadas}")
        print(f"   ✅ Total exitosas: {total_exitosas}")
        print(f"   ❌ Total fallos: {total_fallos}")
        print(f"   💥 Total errores: {total_errores}")
        print(f"   📈 Tasa éxito global: {tasa_exito_global:.1f}%")
        print(f"   ⚡ Promedio por prueba: {tiempo_total/total_ejecutadas:.2f}s" if total_ejecutadas > 0 else "   ⚡ Promedio: N/A")
        
        # Estado final
        exito_total = (total_errores == 0 and total_fallos == 0)
        print("\\n" + "=" * 80)
        if exito_total:
            print("🎉 ESTADO FINAL: TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        else:
            print("⚠️ ESTADO FINAL: ALGUNAS PRUEBAS FALLARON")
        print("=" * 80)
        
        # Guardar reporte JSON
        self.resultados["resumen_global"] = {
            "total_ejecutadas": total_ejecutadas,
            "total_exitosas": total_exitosas,
            "total_errores": total_errores,
            "total_fallos": total_fallos,
            "tasa_exito_global": tasa_exito_global,
            "tiempo_total": tiempo_total,
            "exito_total": exito_total
        }
        
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        archivo_reporte = os.path.join(output_dir, f"reporte_pruebas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                json.dump(self.resultados, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Reporte guardado en: {archivo_reporte}")
        except Exception as e:
            print(f"\n⚠️ Error guardando reporte: {e}")
        
        return exito_total

def main():
    """Función principal para ejecutar todas las pruebas"""
    
    parser = argparse.ArgumentParser(
        description="Suite completa de pruebas para Bot Registraduría Nacional"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Salida detallada de las pruebas"
    )
    parser.add_argument(
        "--solo-unitarias",
        action="store_true", 
        help="Ejecutar solo pruebas unitarias"
    )
    parser.add_argument(
        "--solo-integracion",
        action="store_true",
        help="Ejecutar solo pruebas de integración"
    )
    
    args = parser.parse_args()
    
    # Mostrar banner inicial
    print("🤖 " * 25)
    print("BOT REGISTRADURÍA NACIONAL - SUITE COMPLETA DE PRUEBAS")
    print("🤖 " * 25)
    
    # Crear reporte
    reporte = ReportePruebasCompleto()
    
    exito_unitarias = True
    exito_integracion = True
    
    # Ejecutar pruebas según argumentos
    if not args.solo_integracion:
        exito_unitarias = reporte.ejecutar_pruebas_unitarias(verbose=args.verbose)
    
    if not args.solo_unitarias:
        exito_integracion = reporte.ejecutar_pruebas_integracion(verbose=args.verbose)
    
    # Generar reporte final
    exito_total = reporte.generar_reporte_final()
    
    # Salir con código apropiado
    sys.exit(0 if exito_total else 1)

if __name__ == "__main__":
    main()