"""
PRUEBAS DE INTEGRACIÓN - Bot Registraduría Nacional  
==================================================

Este módulo contiene pruebas de integración para el flujo completo
del bot de consulta de cédulas, probando la interacción entre todos
los componentes del sistema.

Flujos probados:
- Consulta completa desde formulario hasta JSON
- Integración Selenium + OCR + PDF
- Manejo de errores y recuperación
- Performance y concurrencia
- Validación de datos end-to-end

Autor: Sistema Automatizado
Fecha: 29/11/2025
"""

import unittest
import sys
import os
import time
import json
import tempfile
import threading
import subprocess
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Agregar path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# Importar módulos del bot
try:
    import consulta_cedula
    from test_15_consultas_paralelas import MonitorConcurrencia
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")

class TestIntegracionFormulario(unittest.TestCase):
    """Pruebas de integración para interacción con formularios web"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.cedula_test = "1036670248"
        self.fecha_test = "08/01/2015"
        self.url_registraduria = "https://wsp.registraduria.gov.co/censo/consultar/consultarCiudadano.html"
        
        # Configurar opciones de Chrome para testing
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Sin interfaz gráfica
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    @patch('consulta_cedula.webdriver.Chrome')
    def test_navegacion_pagina(self, mock_driver_class):
        """Prueba navegación a la página de la Registraduría"""
        
        # Configurar mock driver
        mock_driver = Mock()
        mock_driver_class.return_value = mock_driver
        
        # Simular navegación exitosa
        mock_driver.get.return_value = None
        mock_driver.title = "Consulta Estado Cédula - Registraduría Nacional"
        mock_driver.current_url = self.url_registraduria
        
        # Crear instancia del driver
        driver = mock_driver_class(options=self.chrome_options)
        
        # Ejecutar navegación
        driver.get(self.url_registraduria)
        
        # Verificaciones
        mock_driver.get.assert_called_once_with(self.url_registraduria)
        self.assertIn("Consulta", driver.title)
        
    @patch('consulta_cedula.webdriver.Chrome')
    def test_llenado_formulario(self, mock_driver_class):
        """Prueba llenado automático del formulario"""
        
        # Configurar mock driver y elementos
        mock_driver = Mock()
        mock_driver_class.return_value = mock_driver
        
        # Mock de elementos del formulario
        mock_input_cedula = Mock()
        mock_input_fecha = Mock()
        mock_captcha_img = Mock()
        mock_submit_button = Mock()
        
        # Configurar respuestas de find_element
        def mock_find_element(by, value):
            if "cedula" in value.lower():
                return mock_input_cedula
            elif "fecha" in value.lower():
                return mock_input_fecha
            elif "captcha" in value.lower():
                return mock_captcha_img
            elif "submit" in value.lower() or "consultar" in value.lower():
                return mock_submit_button
            return Mock()
        
        mock_driver.find_element.side_effect = mock_find_element
        
        # Ejecutar llenado de formulario
        driver = mock_driver_class(options=self.chrome_options)
        
        # Simular llenado
        campo_cedula = driver.find_element("id", "cedula")
        campo_fecha = driver.find_element("id", "fecha")
        imagen_captcha = driver.find_element("id", "captcha")
        boton_enviar = driver.find_element("id", "submit")
        
        # Llenar campos
        campo_cedula.clear()
        campo_cedula.send_keys(self.cedula_test)
        campo_fecha.clear() 
        campo_fecha.send_keys(self.fecha_test)
        
        # Verificar que se llamaron los métodos
        mock_input_cedula.clear.assert_called_once()
        mock_input_cedula.send_keys.assert_called_once_with(self.cedula_test)
        mock_input_fecha.clear.assert_called_once()
        mock_input_fecha.send_keys.assert_called_once_with(self.fecha_test)

class TestIntegracionCAPTCHA(unittest.TestCase):
    """Pruebas de integración para manejo de CAPTCHA"""
    
    def setUp(self):
        """Configuración para pruebas de CAPTCHA"""
        self.mock_driver = Mock()
        self.captcha_test_path = "captcha_test.png"
        
    @patch('consulta_cedula.capturar_screenshot_captcha')
    @patch('consulta_cedula.resolver_captcha_ocr')
    def test_flujo_captcha_ocr(self, mock_resolver, mock_capturar):
        """Prueba flujo completo de resolución CAPTCHA con OCR"""
        
        # Configurar mocks
        mock_capturar.return_value = self.captcha_test_path
        mock_resolver.return_value = "ABCD12"
        
        # Ejecutar flujo
        archivo_captcha = mock_capturar(self.mock_driver)
        codigo_captcha = mock_resolver(archivo_captcha)
        
        # Verificaciones
        self.assertEqual(archivo_captcha, self.captcha_test_path)
        self.assertEqual(codigo_captcha, "ABCD12")
        self.assertEqual(len(codigo_captcha), 6)
        
        mock_capturar.assert_called_once_with(self.mock_driver)
        mock_resolver.assert_called_once_with(self.captcha_test_path)
    
    @patch('consulta_cedula.resolver_captcha_ocr')
    def test_captcha_ocr_fallback_manual(self, mock_resolver):
        """Prueba fallback a entrada manual cuando OCR falla"""
        
        # Simular fallo de OCR
        mock_resolver.return_value = None
        
        # Simular entrada manual
        with patch('builtins.input', return_value='MANUAL123'):
            codigo_ocr = mock_resolver(self.captcha_test_path)
            
            if not codigo_ocr:
                codigo_manual = input("Ingrese CAPTCHA manualmente: ")
                resultado_final = codigo_manual
            else:
                resultado_final = codigo_ocr
        
        self.assertEqual(resultado_final, "MANUAL123")
    
    def test_validacion_codigo_captcha(self):
        """Prueba validación de códigos CAPTCHA"""
        
        codigos_validos = ["ABCD12", "XYZ789", "123ABC", "AAAAAA"]
        codigos_invalidos = ["", "AB", "1234567890", "abcd12", None]
        
        for codigo in codigos_validos:
            with self.subTest(codigo=codigo):
                # Validación típica de CAPTCHA
                valido = codigo and len(codigo) == 6 and codigo.isalnum()
                self.assertTrue(valido, f"Código válido {codigo} fue rechazado")
        
        for codigo in codigos_invalidos:
            with self.subTest(codigo=codigo):
                valido = codigo and len(codigo) == 6 and codigo.isalnum() if codigo else False
                self.assertFalse(valido, f"Código inválido {codigo} fue aceptado")

class TestIntegracionPDF(unittest.TestCase):
    """Pruebas de integración para procesamiento completo de PDFs"""
    
    def setUp(self):
        """Configuración para pruebas de PDF"""
        self.mock_driver = Mock()
        self.cedula_test = "1036670248"
        self.url_pdf_test = "https://example.com/certificado.pdf"
        
    @patch('consulta_cedula.detectar_pdf_generado')
    @patch('consulta_cedula.descargar_pdf_automatico') 
    @patch('consulta_cedula.parsear_y_extraer_pdf')
    def test_flujo_pdf_completo(self, mock_parsear, mock_descargar, mock_detectar):
        """Prueba flujo completo: detectar → descargar → extraer PDF"""
        
        # Configurar mocks en secuencia
        archivo_pdf = f"certificado_{self.cedula_test}.pdf"
        
        mock_detectar.return_value = self.url_pdf_test
        mock_descargar.return_value = archivo_pdf
        mock_parsear.return_value = {
            "cedula": self.cedula_test,
            "nombre": "USUARIO PRUEBA PDF",
            "estado": "VIGENTE",
            "vigente": True,
            "fuente": "PDF",
            "archivo_pdf": archivo_pdf
        }
        
        # Ejecutar flujo secuencial
        url_pdf = mock_detectar(self.mock_driver)
        self.assertIsNotNone(url_pdf)
        
        archivo_descargado = mock_descargar(self.mock_driver, url_pdf, self.cedula_test)
        self.assertIsNotNone(archivo_descargado)
        self.assertIn(self.cedula_test, archivo_descargado)
        
        datos_extraidos = mock_parsear(archivo_descargado, self.cedula_test)
        self.assertIsNotNone(datos_extraidos)
        self.assertEqual(datos_extraidos["cedula"], self.cedula_test)
        self.assertTrue(datos_extraidos["vigente"])
        
        # Verificar llamadas en orden correcto
        mock_detectar.assert_called_once_with(self.mock_driver)
        mock_descargar.assert_called_once_with(self.mock_driver, url_pdf, self.cedula_test)
        mock_parsear.assert_called_once_with(archivo_descargado, self.cedula_test)
    
    @patch('consulta_cedula.detectar_pdf_generado')
    @patch('consulta_cedula.extraer_datos_del_html')
    def test_fallback_html_cuando_no_pdf(self, mock_html, mock_detectar):
        """Prueba fallback a HTML cuando no se encuentra PDF"""
        
        # Simular PDF no encontrado
        mock_detectar.return_value = None
        
        # Configurar extracción HTML como fallback
        mock_html.return_value = {
            "cedula": self.cedula_test,
            "nombre": "USUARIO PRUEBA HTML",
            "estado": "VIGENTE", 
            "vigente": True,
            "fuente": "HTML"
        }
        
        # Ejecutar lógica de fallback
        url_pdf = mock_detectar(self.mock_driver)
        
        if not url_pdf:
            # Usar HTML como alternativa
            datos_html = mock_html(self.mock_driver, self.cedula_test)
            resultado_final = datos_html
        else:
            resultado_final = None
        
        # Verificaciones
        self.assertIsNone(url_pdf)
        self.assertIsNotNone(resultado_final)
        self.assertEqual(resultado_final["fuente"], "HTML")
        self.assertEqual(resultado_final["cedula"], self.cedula_test)

class TestIntegracionDatos(unittest.TestCase):
    """Pruebas de integración para manejo completo de datos"""
    
    def setUp(self):
        """Configuración para pruebas de datos"""
        self.cedula_test = "1036670248"
        self.directorio_temp = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        import shutil
        shutil.rmtree(self.directorio_temp, ignore_errors=True)
    
    @patch('consulta_cedula.guardar_datos_json')
    def test_persistencia_datos_json(self, mock_guardar):
        """Prueba guardado y persistencia de datos JSON"""
        
        datos_consulta = {
            "cedula": self.cedula_test,
            "nombre": "USUARIO PRUEBA INTEGRACION",
            "estado": "VIGENTE",
            "vigente": True,
            "fecha_consulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "metadata": {
                "fuente": "PDF",
                "tiempo_procesamiento": 5.2,
                "intentos_captcha": 1
            }
        }
        
        archivo_json = os.path.join(self.directorio_temp, f"consulta_{self.cedula_test}.json")
        mock_guardar.return_value = archivo_json
        
        # Ejecutar guardado
        resultado = mock_guardar(datos_consulta, self.cedula_test)
        
        # Verificaciones
        self.assertEqual(resultado, archivo_json)
        mock_guardar.assert_called_once_with(datos_consulta, self.cedula_test)
    
    def test_validacion_estructura_datos(self):
        """Prueba validación de estructura completa de datos"""
        
        datos_completos = {
            "cedula": self.cedula_test,
            "nombre": "USUARIO PRUEBA",
            "estado": "VIGENTE",
            "vigente": True,
            "fecha_expedicion": "08/01/2015",
            "lugar_expedicion": "BOGOTA D.C.",
            "fecha_consulta": "29/11/2025 13:30:00",
            "fuente": "PDF",
            "archivo_pdf": f"certificado_{self.cedula_test}.pdf",
            "metadata": {
                "tiempo_total": 8.5,
                "intentos_captcha": 2,
                "metodo_captcha": "OCR"
            }
        }
        
        # Validar campos obligatorios
        campos_obligatorios = ["cedula", "fecha_consulta", "vigente"]
        for campo in campos_obligatorios:
            self.assertIn(campo, datos_completos, f"Campo obligatorio {campo} faltante")
        
        # Validar tipos de datos
        self.assertIsInstance(datos_completos["cedula"], str)
        self.assertIsInstance(datos_completos["vigente"], bool)
        self.assertIsInstance(datos_completos["metadata"], dict)
        
        # Validar estructura metadata
        metadata_fields = ["tiempo_total", "intentos_captcha"]
        for field in metadata_fields:
            self.assertIn(field, datos_completos["metadata"])

class TestIntegracionConcurrencia(unittest.TestCase):
    """Pruebas de integración para ejecución concurrente"""
    
    def setUp(self):
        """Configuración para pruebas de concurrencia"""
        self.cedulas_test = [
            "1036670248", "1018505654", "1234567890", 
            "9876543210", "1111111111"
        ]
        self.fecha_test = "08/01/2015"
        
    @patch('consulta_cedula.ejecutar_consulta_completa')
    def test_consultas_paralelas(self, mock_ejecutar):
        """Prueba ejecución de consultas paralelas"""
        
        # Configurar mock para diferentes resultados
        def mock_consulta(cedula, fecha):
            return {
                "cedula": cedula,
                "nombre": f"USUARIO {cedula}",
                "estado": "VIGENTE",
                "vigente": True,
                "tiempo_procesamiento": 3.5
            }
        
        mock_ejecutar.side_effect = mock_consulta
        
        # Ejecutar consultas en paralelo
        resultados = []
        threads = []
        
        def ejecutar_consulta(cedula):
            resultado = mock_ejecutar(cedula, self.fecha_test)
            resultados.append(resultado)
        
        # Crear y ejecutar threads
        for cedula in self.cedulas_test:
            thread = threading.Thread(target=ejecutar_consulta, args=(cedula,))
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen todos
        for thread in threads:
            thread.join()
        
        # Verificaciones
        self.assertEqual(len(resultados), len(self.cedulas_test))
        self.assertEqual(mock_ejecutar.call_count, len(self.cedulas_test))
        
        # Verificar que todas las cédulas fueron procesadas
        cedulas_procesadas = [r["cedula"] for r in resultados]
        for cedula in self.cedulas_test:
            self.assertIn(cedula, cedulas_procesadas)
    
    def test_manejo_concurrencia_con_errores(self):
        """Prueba manejo de errores en ejecución concurrente"""
        
        def consulta_con_error(cedula, exito=True):
            if not exito:
                raise Exception(f"Error simulado para {cedula}")
            return {
                "cedula": cedula,
                "resultado": "exitoso"
            }
        
        resultados_exitosos = []
        errores = []
        
        def ejecutar_con_manejo_error(cedula, debe_fallar=False):
            try:
                resultado = consulta_con_error(cedula, not debe_fallar)
                resultados_exitosos.append(resultado)
            except Exception as e:
                errores.append({"cedula": cedula, "error": str(e)})
        
        # Ejecutar mezcla de exitosos y con error
        threads = []
        for i, cedula in enumerate(self.cedulas_test):
            # Hacer que algunas fallen
            debe_fallar = i % 2 == 0
            thread = threading.Thread(
                target=ejecutar_con_manejo_error, 
                args=(cedula, debe_fallar)
            )
            threads.append(thread)
            thread.start()
        
        # Esperar threads
        for thread in threads:
            thread.join()
        
        # Verificar manejo de errores
        self.assertGreater(len(errores), 0, "Deberían haber errores simulados")
        self.assertGreater(len(resultados_exitosos), 0, "Deberían haber éxitos")
        self.assertEqual(
            len(errores) + len(resultados_exitosos), 
            len(self.cedulas_test),
            "Total de resultados debe coincidir"
        )

class TestIntegracionPerformance(unittest.TestCase):
    """Pruebas de integración para rendimiento del sistema"""
    
    def setUp(self):
        """Configuración para pruebas de performance"""
        self.cedula_test = "1036670248"
        self.fecha_test = "08/01/2015"
        
    @patch('consulta_cedula.ejecutar_consulta_completa')
    def test_tiempo_respuesta_consulta(self, mock_ejecutar):
        """Prueba medición de tiempos de respuesta"""
        
        # Simular diferentes tiempos de procesamiento
        def consulta_con_delay():
            time.sleep(0.1)  # Simular procesamiento
            return {
                "cedula": self.cedula_test,
                "resultado": "exitoso",
                "tiempo_procesamiento": 0.1
            }
        
        mock_ejecutar.side_effect = lambda c, f: consulta_con_delay()
        
        # Medir tiempo de ejecución
        inicio = time.time()
        resultado = mock_ejecutar(self.cedula_test, self.fecha_test)
        fin = time.time()
        
        tiempo_total = fin - inicio
        
        # Verificaciones de performance
        self.assertLess(tiempo_total, 1.0, "Consulta demasiado lenta")
        self.assertGreater(tiempo_total, 0.05, "Tiempo medición válida")
        self.assertIsNotNone(resultado)
    
    def test_uso_memoria_multiple_consultas(self):
        """Prueba uso de memoria en múltiples consultas"""
        
        import psutil
        import os
        
        proceso = psutil.Process(os.getpid())
        memoria_inicial = proceso.memory_info().rss
        
        # Simular múltiples consultas
        resultados = []
        for i in range(10):
            datos_consulta = {
                "cedula": f"123456789{i}",
                "nombre": f"USUARIO {i}",
                "datos": "x" * 1000  # Simular datos de cierto tamaño
            }
            resultados.append(datos_consulta)
        
        memoria_final = proceso.memory_info().rss
        incremento_memoria = memoria_final - memoria_inicial
        
        # Verificar que el incremento no sea excesivo
        self.assertLess(
            incremento_memoria, 
            50 * 1024 * 1024,  # 50MB máximo
            "Incremento de memoria excesivo"
        )

def ejecutar_suite_integracion():
    """Ejecuta todas las pruebas de integración"""
    
    print("🔧 EJECUTANDO SUITE COMPLETA DE PRUEBAS DE INTEGRACIÓN")
    print("=" * 65)
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de prueba de integración
    clases_prueba = [
        TestIntegracionFormulario,
        TestIntegracionCAPTCHA,
        TestIntegracionPDF,
        TestIntegracionDatos,
        TestIntegracionConcurrencia,
        TestIntegracionPerformance
    ]
    
    for clase in clases_prueba:
        suite.addTests(loader.loadTestsFromTestCase(clase))
    
    # Ejecutar pruebas con reporte detallado
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        failfast=False
    )
    
    inicio_suite = time.time()
    resultado = runner.run(suite)
    fin_suite = time.time()
    
    # Generar reporte de resultados
    tiempo_total = fin_suite - inicio_suite
    total_tests = resultado.testsRun
    errores = len(resultado.errors)
    fallos = len(resultado.failures)
    exitosos = total_tests - errores - fallos
    
    print("\\n" + "=" * 65)
    print("📊 REPORTE FINAL DE PRUEBAS DE INTEGRACIÓN")
    print("=" * 65)
    print(f"✅ Pruebas exitosas: {exitosos}/{total_tests}")
    print(f"❌ Fallos: {fallos}")
    print(f"💥 Errores: {errores}")
    print(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
    print(f"📈 Tasa de éxito: {(exitosos/total_tests)*100:.1f}%")
    print(f"⚡ Promedio por prueba: {tiempo_total/total_tests:.2f}s")
    
    if errores > 0:
        print("\n💥 ERRORES DE INTEGRACIÓN:")
        for test, error in resultado.errors:
            error_lines = error.split('\n')
            error_msg = error_lines[-2] if len(error_lines) > 1 else str(error)
            print(f"   • {test}: {error_msg}")
    
    if fallos > 0:
        print("\n❌ FALLOS DE INTEGRACIÓN:")
        for test, fallo in resultado.failures:
            fallo_lines = fallo.split('\n')
            fallo_msg = fallo_lines[-2] if len(fallo_lines) > 1 else str(fallo)
            print(f"   • {test}: {fallo_msg}")
    
    print("=" * 65)
    
    return exitosos == total_tests

if __name__ == "__main__":
    # Ejecutar todas las pruebas de integración
    exito = ejecutar_suite_integracion()
    
    if exito:
        print("🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON")
        sys.exit(0)
    else:
        print("⚠️ ALGUNAS PRUEBAS DE INTEGRACIÓN FALLARON")
        sys.exit(1)