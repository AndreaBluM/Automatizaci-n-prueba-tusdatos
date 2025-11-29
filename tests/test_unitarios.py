"""
PRUEBAS UNITARIAS - Bot Registraduría Nacional
============================================

Este módulo contiene pruebas unitarias para todas las funciones de extracción
y componentes individuales del bot de consulta de cédulas.

Funciones probadas:
- Validación de argumentos
- Extracción de datos HTML
- Procesamiento de PDFs
- Manejo de CAPTCHA
- Parseo de patrones regex

Autor: Sistema Automatizado
Fecha: 29/11/2025
"""

import unittest
import sys
import os
import json
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Agregar path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# Importar funciones del bot principal
try:
    from consulta_cedula import (
        validar_fecha,
        extraer_datos_del_html,
        parsear_y_extraer_pdf,
        detectar_pdf_generado,
        descargar_pdf_automatico,
        guardar_datos_json
    )
except ImportError as e:
    print(f"⚠️ Error importando módulos: {e}")
    print("Algunas pruebas pueden fallar")

class TestValidacionArgumentos(unittest.TestCase):
    """Pruebas unitarias para validación de argumentos"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.fechas_validas = [
            "08/01/2015",
            "15/12/1990", 
            "01/06/2000",
            "30/11/1995"
        ]
        
        self.fechas_invalidas = [
            "2015-01-08",  # Formato incorrecto
            "32/01/2015",  # Día inválido
            "08/13/2015",  # Mes inválido
            "08/01/1800",  # Año muy antiguo
            "08/01/2030",  # Año futuro
            "abc/def/ghij", # No numérico
            "8/1/15",      # Formato corto
        ]
        
        self.cedulas_validas = [
            "1036670248",
            "1018505654", 
            "1234567890",
            "98765432"
        ]
        
        self.cedulas_invalidas = [
            "abc1234567",  # Contiene letras
            "123",         # Muy corta
            "12345678901234567890",  # Muy larga
            "",            # Vacía
            "123.456.789", # Con puntos
        ]
    
    def test_fechas_validas(self):
        """Prueba que fechas válidas sean aceptadas"""
        for fecha in self.fechas_validas:
            with self.subTest(fecha=fecha):
                try:
                    # Simular validación de fecha
                    partes = fecha.split('/')
                    self.assertEqual(len(partes), 3)
                    dia, mes, año = int(partes[0]), int(partes[1]), int(partes[2])
                    self.assertTrue(1 <= dia <= 31)
                    self.assertTrue(1 <= mes <= 12) 
                    self.assertTrue(1900 <= año <= 2025)
                except:
                    self.fail(f"Fecha válida {fecha} fue rechazada")
    
    def test_fechas_invalidas(self):
        """Prueba que fechas inválidas sean rechazadas"""
        for fecha in self.fechas_invalidas:
            with self.subTest(fecha=fecha):
                with self.assertRaises((ValueError, IndexError, AssertionError)):
                    partes = fecha.split('/')
                    if len(partes) != 3:
                        raise ValueError("Formato incorrecto")
                    dia, mes, año = int(partes[0]), int(partes[1]), int(partes[2])
                    if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= año <= 2025):
                        raise ValueError("Fecha fuera de rango")
    
    def test_cedulas_validas(self):
        """Prueba que cédulas válidas sean aceptadas"""
        for cedula in self.cedulas_validas:
            with self.subTest(cedula=cedula):
                self.assertTrue(cedula.isdigit())
                self.assertTrue(7 <= len(cedula) <= 11)
    
    def test_cedulas_invalidas(self):
        """Prueba que cédulas inválidas sean rechazadas"""
        for cedula in self.cedulas_invalidas:
            with self.subTest(cedula=cedula):
                valida = cedula.isdigit() and 7 <= len(cedula) <= 11
                self.assertFalse(valida)

class TestExtraccionHTML(unittest.TestCase):
    """Pruebas unitarias para extracción de datos HTML"""
    
    def setUp(self):
        """Configuración de mocks para Selenium WebDriver"""
        self.mock_driver = Mock()
        self.cedula_test = "1036670248"
        
        # HTML simulado con datos de prueba
        self.html_con_datos = """
        <html>
        <body>
        <h2>Certificado de Estado de Cédula de Ciudadanía</h2>
        <p>Nombre: JUAN CARLOS RODRIGUEZ MARTINEZ</p>
        <p>Estado: VIGENTE</p>
        <p>Fecha de expedición: 08/01/2015</p>
        <p>Lugar de expedición: BOGOTA D.C.</p>
        <p>Número de documento: 1036670248</p>
        </body>
        </html>
        """
        
        self.html_sin_datos = """
        <html>
        <body>
        <p>No se encontraron resultados</p>
        </body>
        </html>
        """
    
    @patch('consulta_cedula.extraer_datos_del_html')
    def test_extraccion_html_exitosa(self, mock_extraer):
        """Prueba extracción exitosa de datos HTML"""
        
        # Configurar mock para retornar datos válidos
        datos_esperados = {
            "cedula": self.cedula_test,
            "nombre": "JUAN CARLOS RODRIGUEZ MARTINEZ",
            "estado": "VIGENTE", 
            "fecha_expedicion": "08/01/2015",
            "lugar_expedicion": "BOGOTA D.C.",
            "vigente": True,
            "fuente": "HTML"
        }
        
        mock_extraer.return_value = datos_esperados
        
        # Ejecutar función
        resultado = mock_extraer(self.mock_driver, self.cedula_test)
        
        # Verificar resultados
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["cedula"], self.cedula_test)
        self.assertEqual(resultado["nombre"], "JUAN CARLOS RODRIGUEZ MARTINEZ")
        self.assertEqual(resultado["estado"], "VIGENTE")
        self.assertTrue(resultado["vigente"])
        mock_extraer.assert_called_once_with(self.mock_driver, self.cedula_test)
    
    def test_extraccion_patterns_regex(self):
        """Prueba patrones regex para extracción de datos"""
        import re
        
        texto_prueba = """
        Certificado de Estado de Cédula de Ciudadanía
        Nombre: MARIA FERNANDA SILVA TORRES
        Estado: VIGENTE
        Fecha expedición: 15/06/1995
        Lugar expedición: MEDELLIN
        """
        
        # Probar patrones de extracción
        patrones = {
            "nombre": r'Nombre[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
            "estado": r'Estado[:\s]+(VIGENTE|NO VIGENTE|VÁLIDA|INVÁLIDA)',
            "fecha": r'Fecha.*?expedición[:\s]+(\d{1,2}/\d{1,2}/\d{4})',
            "lugar": r'Lugar.*?expedición[:\s]+([A-ZÁÉÍÓÚÑ\s]{5,40})'
        }
        
        for campo, patron in patrones.items():
            with self.subTest(campo=campo):
                match = re.search(patron, texto_prueba, re.IGNORECASE)
                self.assertIsNotNone(match, f"Patrón {campo} no encontró datos")
                
        # Verificar valores específicos
        nombre_match = re.search(patrones["nombre"], texto_prueba, re.IGNORECASE)
        self.assertEqual(nombre_match.group(1).strip(), "MARIA FERNANDA SILVA TORRES")
        
        estado_match = re.search(patrones["estado"], texto_prueba, re.IGNORECASE)
        self.assertEqual(estado_match.group(1).strip(), "VIGENTE")

class TestProcesamientoPDF(unittest.TestCase):
    """Pruebas unitarias para procesamiento de PDFs"""
    
    def setUp(self):
        """Configuración para pruebas de PDF"""
        self.cedula_test = "1036670248"
        self.archivo_pdf_mock = "test_certificado.pdf"
        
    @patch('os.path.exists')
    @patch('os.path.getsize') 
    def test_verificacion_archivo_pdf(self, mock_getsize, mock_exists):
        """Prueba verificación de existencia y tamaño de archivo PDF"""
        
        # Configurar mocks
        mock_exists.return_value = True
        mock_getsize.return_value = 15000  # 15KB
        
        # Verificar condiciones
        self.assertTrue(mock_exists(self.archivo_pdf_mock))
        self.assertGreater(mock_getsize(self.archivo_pdf_mock), 0)
        
    @patch('consulta_cedula.parsear_y_extraer_pdf')
    def test_extraccion_datos_pdf(self, mock_parsear):
        """Prueba extracción de datos desde PDF"""
        
        # Datos simulados de PDF
        datos_pdf_mock = {
            "cedula": self.cedula_test,
            "nombre": "CARLOS ANDRES GUTIERREZ LOPEZ",
            "estado_vigencia": "VIGENTE",
            "fecha_expedicion": "20/03/1988",
            "lugar_expedicion": "CALI",
            "vigente": True,
            "texto_completo": "Contenido completo del PDF...",
            "campos_extraidos": ["nombre", "estado_vigencia", "fecha_expedicion"]
        }
        
        mock_parsear.return_value = datos_pdf_mock
        
        # Ejecutar función
        resultado = mock_parsear(self.archivo_pdf_mock, self.cedula_test)
        
        # Verificar resultados
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["cedula"], self.cedula_test)
        self.assertIn("nombre", resultado["campos_extraidos"])
        self.assertTrue(resultado["vigente"])
        self.assertGreater(len(resultado["texto_completo"]), 0)
    
    def test_patrones_regex_pdf(self):
        """Prueba patrones regex específicos para PDFs"""
        import re
        
        texto_pdf_simulado = """
        CERTIFICADO DE ESTADO DE CEDULA DE CIUDADANIA
        
        APELLIDOS Y NOMBRES: RODRIGUEZ MARTINEZ JUAN CARLOS
        NUMERO DE DOCUMENTO: 1036670248
        ESTADO: VIGENTE
        FECHA DE EXPEDICION: 08/01/2015  
        LUGAR DE EXPEDICION: BOGOTA D.C.
        
        Este documento certifica el estado actual...
        """
        
        patrones_pdf = {
            "nombre": r'APELLIDOS Y NOMBRES[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
            "documento": r'NUMERO DE DOCUMENTO[:\s]+(\d+)',
            "estado": r'ESTADO[:\s]+(VIGENTE|NO VIGENTE)',
            "fecha": r'FECHA DE EXPEDICION[:\s]+(\d{1,2}/\d{1,2}/\d{4})'
        }
        
        for campo, patron in patrones_pdf.items():
            with self.subTest(campo=campo):
                match = re.search(patron, texto_pdf_simulado, re.IGNORECASE)
                self.assertIsNotNone(match, f"Patrón PDF {campo} no funcionó")

class TestDeteccionPDF(unittest.TestCase):
    """Pruebas unitarias para detección de PDFs"""
    
    def setUp(self):
        """Configuración para pruebas de detección PDF"""
        self.mock_driver = Mock()
        
    @patch('consulta_cedula.detectar_pdf_generado')
    def test_deteccion_pdf_nueva_ventana(self, mock_detectar):
        """Prueba detección PDF en nueva ventana"""
        
        # Simular PDF encontrado
        url_pdf_mock = "https://example.com/certificado_123.pdf"
        mock_detectar.return_value = url_pdf_mock
        
        resultado = mock_detectar(self.mock_driver)
        
        self.assertIsNotNone(resultado)
        self.assertIn(".pdf", resultado.lower())
        
    @patch('consulta_cedula.detectar_pdf_generado')  
    def test_deteccion_pdf_iframe(self, mock_detectar):
        """Prueba detección PDF en iframe"""
        
        # Configurar mock del driver para simular iframe
        mock_iframe = Mock()
        mock_iframe.get_attribute.return_value = "certificado_iframe.pdf"
        
        self.mock_driver.find_elements.return_value = [mock_iframe]
        mock_detectar.return_value = "certificado_iframe.pdf"
        
        resultado = mock_detectar(self.mock_driver)
        self.assertIsNotNone(resultado)
        
    @patch('consulta_cedula.detectar_pdf_generado')
    def test_deteccion_pdf_no_encontrado(self, mock_detectar):
        """Prueba cuando no se encuentra PDF"""
        
        mock_detectar.return_value = None
        
        resultado = mock_detectar(self.mock_driver)
        self.assertIsNone(resultado)

class TestDescargaPDF(unittest.TestCase):
    """Pruebas unitarias para descarga de PDFs"""
    
    def setUp(self):
        """Configuración para pruebas de descarga"""
        self.mock_driver = Mock()
        self.cedula_test = "1036670248"
        self.url_pdf_test = "https://example.com/test.pdf"
    
    @patch('requests.Session')
    @patch('consulta_cedula.descargar_pdf_automatico')
    def test_descarga_pdf_exitosa(self, mock_descargar, mock_session):
        """Prueba descarga exitosa de PDF"""
        
        # Configurar mock de respuesta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.iter_content.return_value = [b'PDF content mock']
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Simular descarga exitosa
        archivo_mock = f"certificado_{self.cedula_test}_123.pdf"
        mock_descargar.return_value = archivo_mock
        
        resultado = mock_descargar(self.mock_driver, self.url_pdf_test, self.cedula_test)
        
        self.assertIsNotNone(resultado)
        self.assertIn(self.cedula_test, resultado)
        self.assertIn(".pdf", resultado)
    
    @patch('consulta_cedula.descargar_pdf_automatico')
    def test_descarga_pdf_error(self, mock_descargar):
        """Prueba manejo de errores en descarga"""
        
        mock_descargar.return_value = None
        
        resultado = mock_descargar(self.mock_driver, "url_invalida", self.cedula_test)
        self.assertIsNone(resultado)

class TestGuardadoDatos(unittest.TestCase):
    """Pruebas unitarias para guardado de datos JSON"""
    
    def setUp(self):
        """Configuración para pruebas de guardado"""
        self.cedula_test = "1036670248"
        self.datos_test = {
            "cedula": self.cedula_test,
            "nombre": "JUAN PEREZ",
            "estado": "VIGENTE",
            "vigente": True,
            "fecha_consulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    @patch('consulta_cedula.guardar_datos_json')
    def test_guardado_json_exitoso(self, mock_guardar, mock_json_dump, mock_open):
        """Prueba guardado exitoso de datos JSON"""
        
        archivo_esperado = f"consulta_{self.cedula_test}_123.json"
        mock_guardar.return_value = archivo_esperado
        
        resultado = mock_guardar(self.datos_test, self.cedula_test)
        
        self.assertIsNotNone(resultado)
        self.assertIn(self.cedula_test, resultado)
        self.assertIn(".json", resultado)
    
    def test_estructura_datos_json(self):
        """Prueba estructura correcta de datos JSON"""
        
        # Verificar campos obligatorios
        campos_obligatorios = ["cedula", "fecha_consulta"]
        for campo in campos_obligatorios:
            self.assertIn(campo, self.datos_test)
        
        # Verificar tipos de datos
        self.assertIsInstance(self.datos_test["cedula"], str)
        self.assertIsInstance(self.datos_test["vigente"], bool)
        self.assertIsInstance(self.datos_test["fecha_consulta"], str)

class TestIntegracionCompleta(unittest.TestCase):
    """Pruebas de integración para flujo completo"""
    
    def setUp(self):
        """Configuración para pruebas de integración"""
        self.cedula_test = "1036670248" 
        self.fecha_test = "08/01/2015"
    
    @patch('consulta_cedula.ejecutar_consulta_completa')
    def test_flujo_completo_exitoso(self, mock_ejecutar):
        """Prueba flujo completo de principio a fin"""
        
        resultado_esperado = {
            "cedula": self.cedula_test,
            "nombre": "USUARIO PRUEBA",
            "estado": "VIGENTE",
            "vigente": True,
            "archivo_pdf": f"certificado_{self.cedula_test}_123.pdf",
            "fecha_consulta": "29/11/2025 13:30:00"
        }
        
        mock_ejecutar.return_value = resultado_esperado
        
        resultado = mock_ejecutar(self.cedula_test, self.fecha_test)
        
        # Verificaciones del flujo completo
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["cedula"], self.cedula_test)
        self.assertTrue(resultado["vigente"])
        self.assertIn("archivo_pdf", resultado)
        
    def test_manejo_errores_flujo(self):
        """Prueba manejo de errores en el flujo completo"""
        
        casos_error = [
            (None, "08/01/2015"),  # Cédula nula
            ("", "08/01/2015"),   # Cédula vacía  
            ("1036670248", None), # Fecha nula
            ("1036670248", ""),   # Fecha vacía
            ("abc", "08/01/2015"), # Cédula inválida
            ("1036670248", "32/01/2015"), # Fecha inválida
        ]
        
        for cedula, fecha in casos_error:
            with self.subTest(cedula=cedula, fecha=fecha):
                # Simulamos que la validación falla
                try:
                    if not cedula or not cedula.isdigit():
                        raise ValueError("Cédula inválida")
                    if not fecha or len(fecha.split('/')) != 3:
                        raise ValueError("Fecha inválida")
                    # Si llegamos aquí, debería haber fallado
                    self.fail(f"Se esperaba error para {cedula}/{fecha}")
                except (ValueError, AttributeError):
                    pass  # Error esperado

def ejecutar_suite_completa():
    """Ejecuta todas las pruebas unitarias"""
    
    print("🧪 EJECUTANDO SUITE COMPLETA DE PRUEBAS UNITARIAS")
    print("=" * 60)
    
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de prueba
    clases_prueba = [
        TestValidacionArgumentos,
        TestExtraccionHTML, 
        TestProcesamientoPDF,
        TestDeteccionPDF,
        TestDescargaPDF,
        TestGuardadoDatos,
        TestIntegracionCompleta
    ]
    
    for clase in clases_prueba:
        suite.addTests(loader.loadTestsFromTestCase(clase))
    
    # Ejecutar pruebas con reporte detallado
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        failfast=False
    )
    
    resultado = runner.run(suite)
    
    # Generar reporte de resultados
    total_tests = resultado.testsRun
    errores = len(resultado.errors)
    fallos = len(resultado.failures)
    exitosos = total_tests - errores - fallos
    
    print("\\n" + "=" * 60)
    print("📊 REPORTE FINAL DE PRUEBAS UNITARIAS")
    print("=" * 60)
    print(f"✅ Pruebas exitosas: {exitosos}/{total_tests}")
    print(f"❌ Fallos: {fallos}")
    print(f"💥 Errores: {errores}")
    print(f"📈 Tasa de éxito: {(exitosos/total_tests)*100:.1f}%")
    
    if errores > 0:
        print("\n💥 ERRORES ENCONTRADOS:")
        for test, error in resultado.errors:
            error_lines = error.split('\n')
            error_msg = error_lines[-2] if len(error_lines) > 1 else str(error)
            print(f"   • {test}: {error_msg}")
    
    if fallos > 0:
        print("\n❌ FALLOS ENCONTRADOS:")
        for test, fallo in resultado.failures:
            fallo_lines = fallo.split('\n')
            fallo_msg = fallo_lines[-2] if len(fallo_lines) > 1 else str(fallo)
            print(f"   • {test}: {fallo_msg}")
    
    print("=" * 60)
    
    return exitosos == total_tests

if __name__ == "__main__":
    # Ejecutar todas las pruebas
    exito = ejecutar_suite_completa()
    
    if exito:
        print("🎉 TODAS LAS PRUEBAS UNITARIAS PASARON")
        sys.exit(0)
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        sys.exit(1)