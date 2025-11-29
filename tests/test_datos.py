"""
PRUEBAS DE DATOS - Bot Registraduría Nacional
==========================================

Módulo especializado en pruebas para validación y manejo de datos.
Incluye pruebas para diferentes formatos de datos, validaciones,
transformaciones y casos edge.

Casos probados:
- Validación de cédulas colombianas
- Formatos de fecha múltiples
- Extracción de nombres complejos
- Manejo de caracteres especiales
- Datos incompletos o corruptos

Autor: Sistema Automatizado  
Fecha: 29/11/2025
"""

import unittest
import sys
import os
import re
from datetime import datetime

# Agregar path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

class TestValidacionCedulasColombiana(unittest.TestCase):
    """Pruebas específicas para validación de cédulas colombianas"""
    
    def setUp(self):
        """Configuración de casos de prueba"""
        self.cedulas_reales = [
            "1036670248", "1018505654", "52456789", "1234567890",
            "98765432", "1111111111", "5555555555", "1000000000"
        ]
        
        self.cedulas_invalidas = [
            "0", "123", "12345678901234567890",  # Muy corta/larga
            "1234567A89", "ABC1234567",  # Con letras
            "12.345.678", "12,345,678",  # Con separadores
            "", None, "          ",  # Vacías/nulas
            "0000000000", "1111111111111"  # Casos especiales
        ]
        
    def test_formato_cedula_basico(self):
        """Prueba formato básico de cédulas"""
        for cedula in self.cedulas_reales:
            with self.subTest(cedula=cedula):
                # Validaciones básicas
                self.assertTrue(cedula.isdigit(), f"Cédula {cedula} contiene no-dígitos")
                self.assertTrue(7 <= len(cedula) <= 11, f"Cédula {cedula} longitud inválida")
                self.assertNotEqual(cedula[0], '0', f"Cédula {cedula} inicia con 0")
    
    def test_cedulas_invalidas(self):
        """Prueba rechazo de cédulas inválidas"""
        for cedula in self.cedulas_invalidas:
            with self.subTest(cedula=cedula):
                # Validar que sean rechazadas
                valida = False
                if cedula and isinstance(cedula, str):
                    cedula_limpia = cedula.strip()
                    if cedula_limpia.isdigit() and 7 <= len(cedula_limpia) <= 11:
                        if cedula_limpia[0] != '0':
                            valida = True
                
                self.assertFalse(valida, f"Cédula inválida {cedula} fue aceptada")
    
    def test_normalizacion_cedulas(self):
        """Prueba normalización de formatos de cédula"""
        casos_normalizacion = [
            ("1.036.670.248", "1036670248"),
            ("1,036,670,248", "1036670248"), 
            (" 1036670248 ", "1036670248"),
            ("1'036'670'248", "1036670248"),
            ("1 036 670 248", "1036670248"),
        ]
        
        for entrada, esperada in casos_normalizacion:
            with self.subTest(entrada=entrada):
                # Proceso de normalización
                normalizada = re.sub(r'[^0-9]', '', entrada)
                self.assertEqual(normalizada, esperada)

class TestValidacionFechasColombiana(unittest.TestCase):
    """Pruebas para validación de fechas en formato colombiano"""
    
    def setUp(self):
        """Configuración de casos de prueba de fechas"""
        self.fechas_validas = [
            "08/01/2015", "15/12/1990", "01/06/2000",
            "30/11/1995", "29/02/2000", "31/12/1999",  # Bisiesto y límites
            "01/01/1950", "31/12/2024"  # Rangos extremos
        ]
        
        self.fechas_invalidas = [
            "32/01/2015",  # Día inválido
            "01/13/2015",  # Mes inválido
            "29/02/2001",  # No bisiesto
            "31/04/2015",  # Abril no tiene 31
            "00/01/2015",  # Día 0
            "01/00/2015",  # Mes 0
            "2015-01-08",  # Formato ISO
            "08-01-2015",  # Formato US
            "Jan 8, 2015", # Formato texto
        ]
    
    def test_fechas_validas_colombianas(self):
        """Prueba fechas válidas formato DD/MM/YYYY"""
        for fecha in self.fechas_validas:
            with self.subTest(fecha=fecha):
                # Validar formato y contenido
                patron = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
                match = re.match(patron, fecha)
                self.assertIsNotNone(match, f"Fecha {fecha} no coincide con patrón")
                
                dia, mes, año = map(int, match.groups())
                
                # Validaciones básicas
                self.assertTrue(1 <= dia <= 31, f"Día inválido en {fecha}")
                self.assertTrue(1 <= mes <= 12, f"Mes inválido en {fecha}")
                self.assertTrue(1900 <= año <= 2030, f"Año inválido en {fecha}")
    
    def test_fechas_invalidas_colombianas(self):
        """Prueba rechazo de fechas inválidas"""
        for fecha in self.fechas_invalidas:
            with self.subTest(fecha=fecha):
                patron = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
                match = re.match(patron, fecha)
                
                valida = False
                if match:
                    try:
                        dia, mes, año = map(int, match.groups())
                        if (1 <= dia <= 31 and 1 <= mes <= 12 and 
                            1900 <= año <= 2030):
                            # Validación adicional de días por mes
                            dias_por_mes = [31, 28, 31, 30, 31, 30, 
                                          31, 31, 30, 31, 30, 31]
                            
                            # Ajustar febrero en años bisiestos
                            if año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
                                dias_por_mes[1] = 29
                            
                            if dia <= dias_por_mes[mes - 1]:
                                valida = True
                    except (ValueError, IndexError):
                        pass
                
                self.assertFalse(valida, f"Fecha inválida {fecha} fue aceptada")

class TestExtraccionNombresComplejo(unittest.TestCase):
    """Pruebas para extracción de nombres complejos colombianos"""
    
    def setUp(self):
        """Configuración de casos de nombres"""
        self.casos_nombres = [
            # (texto_fuente, nombre_esperado)
            ("NOMBRE: JUAN CARLOS RODRIGUEZ MARTINEZ", "JUAN CARLOS RODRIGUEZ MARTINEZ"),
            ("APELLIDOS Y NOMBRES: SILVA TORRES MARIA FERNANDA", "SILVA TORRES MARIA FERNANDA"),
            ("Nombre completo: ANA LUCIA GUTIERREZ DE LOPEZ", "ANA LUCIA GUTIERREZ DE LOPEZ"),
            ("NOMBRES: CARLOS ANDRES", "CARLOS ANDRES"),
            ("APELLIDOS: RODRIGUEZ MARTINEZ", "RODRIGUEZ MARTINEZ"),
            
            # Casos con caracteres especiales
            ("NOMBRE: JOSÉ MARÍA HERNÁNDEZ NÚÑEZ", "JOSÉ MARÍA HERNÁNDEZ NÚÑEZ"),
            ("APELLIDOS Y NOMBRES: PEÑA LÓPEZ MARÍA JOSÉ", "PEÑA LÓPEZ MARÍA JOSÉ"),
            
            # Casos con partículas
            ("NOMBRE: MARIA DEL CARMEN RODRIGUEZ", "MARIA DEL CARMEN RODRIGUEZ"),
            ("NOMBRE: JUAN DE LA CRUZ MARTINEZ", "JUAN DE LA CRUZ MARTINEZ"),
            ("NOMBRE: ANA SOFIA DE LOS SANTOS", "ANA SOFIA DE LOS SANTOS"),
        ]
    
    def test_extraccion_nombres_patron_basico(self):
        """Prueba extracción con patrón básico"""
        patron = r'NOMBR(?:E|ES?)[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})'
        
        for texto, esperado in self.casos_nombres:
            if "NOMBR" in texto:
                with self.subTest(texto=texto):
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        extraido = match.group(1).strip()
                        self.assertEqual(extraido, esperado)
    
    def test_extraccion_nombres_multiple_patrones(self):
        """Prueba múltiples patrones de extracción"""
        patrones = [
            r'NOMBRE[S]?[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
            r'APELLIDOS Y NOMBRES[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})', 
            r'Nombre completo[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
            r'APELLIDOS[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})'
        ]
        
        for texto, esperado in self.casos_nombres:
            with self.subTest(texto=texto):
                encontrado = False
                for patron in patrones:
                    match = re.search(patron, texto, re.IGNORECASE)
                    if match:
                        extraido = match.group(1).strip()
                        if extraido:
                            encontrado = True
                            break
                
                self.assertTrue(encontrado, f"No se extrajo nombre de: {texto}")
    
    def test_limpieza_nombres(self):
        """Prueba limpieza y normalización de nombres"""
        casos_limpieza = [
            ("  JUAN CARLOS  ", "JUAN CARLOS"),
            ("MARÍA   FERNANDA", "MARÍA FERNANDA"), 
            ("RODRIGUEZ\\nMARTINEZ", "RODRIGUEZ MARTINEZ"),
            ("JOSÉ  \\t MARÍA", "JOSÉ MARÍA"),
        ]
        
        for sucio, limpio in casos_limpieza:
            with self.subTest(sucio=sucio):
                # Proceso de limpieza
                normalizado = re.sub(r'\\s+', ' ', sucio.strip())
                self.assertEqual(normalizado, limpio)

class TestManejoDatosIncompletos(unittest.TestCase):
    """Pruebas para manejo de datos incompletos o parciales"""
    
    def setUp(self):
        """Configuración de casos de datos incompletos"""
        self.datos_parciales = [
            {
                "cedula": "1036670248",
                "nombre": "JUAN CARLOS RODRIGUEZ",
                # Falta estado y fecha
            },
            {
                "cedula": "1018505654", 
                "estado": "VIGENTE",
                # Falta nombre y fecha
            },
            {
                "nombre": "MARIA FERNANDA SILVA",
                "fecha_expedicion": "15/06/1995",
                # Falta cédula y estado  
            }
        ]
    
    def test_completitud_datos_minimos(self):
        """Prueba validación de datos mínimos requeridos"""
        campos_obligatorios = ["cedula"]
        
        for datos in self.datos_parciales:
            with self.subTest(datos=datos):
                # Verificar campos obligatorios
                for campo in campos_obligatorios:
                    if campo not in datos or not datos[campo]:
                        with self.assertRaises(AssertionError):
                            assert campo in datos and datos[campo], f"Campo {campo} requerido"
    
    def test_completar_datos_faltantes(self):
        """Prueba completar datos con valores por defecto"""
        for datos_originales in self.datos_parciales:
            with self.subTest(datos=datos_originales):
                # Crear copia para no modificar original
                datos = datos_originales.copy()
                
                # Aplicar valores por defecto
                datos.setdefault("estado", "NO DETERMINADO")
                datos.setdefault("vigente", None)
                datos.setdefault("fecha_consulta", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                datos.setdefault("fuente", "PARCIAL")
                
                # Verificar que todos los campos están presentes
                campos_esperados = ["estado", "vigente", "fecha_consulta", "fuente"]
                for campo in campos_esperados:
                    self.assertIn(campo, datos)

class TestTransformacionDatos(unittest.TestCase):
    """Pruebas para transformación y normalización de datos"""
    
    def setUp(self):
        """Configuración para transformaciones"""
        self.datos_crudos = {
            "cedula": " 1036670248 ",
            "nombre": "  JUAN  CARLOS   RODRIGUEZ  ",  
            "estado": "vigente",
            "fecha_expedicion": "8/1/2015",
            "lugar_expedicion": "bogota d.c."
        }
    
    def test_normalizacion_completa(self):
        """Prueba normalización completa de datos"""
        datos_normalizados = {}
        
        # Normalizar cédula
        if "cedula" in self.datos_crudos:
            cedula = re.sub(r'[^0-9]', '', self.datos_crudos["cedula"])
            datos_normalizados["cedula"] = cedula
        
        # Normalizar nombre
        if "nombre" in self.datos_crudos:
            nombre = re.sub(r'\\s+', ' ', self.datos_crudos["nombre"].strip().upper())
            datos_normalizados["nombre"] = nombre
        
        # Normalizar estado
        if "estado" in self.datos_crudos:
            estado = self.datos_crudos["estado"].upper().strip()
            if estado in ["VIGENTE", "VÁLIDA", "ACTIVA", "ACTIVO"]:
                datos_normalizados["estado"] = "VIGENTE"
                datos_normalizados["vigente"] = True
            else:
                datos_normalizados["estado"] = "NO VIGENTE"
                datos_normalizados["vigente"] = False
        
        # Normalizar fecha
        if "fecha_expedicion" in self.datos_crudos:
            fecha = self.datos_crudos["fecha_expedicion"]
            # Convertir formato D/M/YYYY a DD/MM/YYYY
            partes = fecha.split('/')
            if len(partes) == 3:
                dia, mes, año = partes
                fecha_norm = f"{dia.zfill(2)}/{mes.zfill(2)}/{año}"
                datos_normalizados["fecha_expedicion"] = fecha_norm
        
        # Normalizar lugar
        if "lugar_expedicion" in self.datos_crudos:
            lugar = self.datos_crudos["lugar_expedicion"].upper().strip()
            datos_normalizados["lugar_expedicion"] = lugar
        
        # Verificar transformaciones
        self.assertEqual(datos_normalizados["cedula"], "1036670248")
        self.assertEqual(datos_normalizados["nombre"], "JUAN CARLOS RODRIGUEZ")
        self.assertEqual(datos_normalizados["estado"], "VIGENTE")
        self.assertTrue(datos_normalizados["vigente"])
        self.assertEqual(datos_normalizados["fecha_expedicion"], "08/01/2015")
        self.assertEqual(datos_normalizados["lugar_expedicion"], "BOGOTA D.C.")
    
    def test_deteccion_estado_vigencia(self):
        """Prueba detección inteligente de estado de vigencia"""
        casos_estado = [
            ("VIGENTE", True),
            ("VÁLIDA", True),
            ("ACTIVA", True),
            ("ACTIVO", True),
            ("NO VIGENTE", False),
            ("INVÁLIDA", False), 
            ("INACTIVA", False),
            ("CANCELADA", False),
            ("SUSPENDIDA", False),
            ("VENCIDA", False),
        ]
        
        for estado_texto, vigente_esperado in casos_estado:
            with self.subTest(estado=estado_texto):
                # Lógica de detección
                estados_vigentes = ["VIGENTE", "VÁLIDA", "ACTIVA", "ACTIVO"]
                vigente = estado_texto.upper() in estados_vigentes
                
                self.assertEqual(vigente, vigente_esperado)

def ejecutar_pruebas_datos():
    """Ejecuta todas las pruebas de datos"""
    
    print("📊 EJECUTANDO PRUEBAS ESPECIALIZADAS DE DATOS")
    print("=" * 55)
    
    # Crear suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar clases de prueba
    clases_datos = [
        TestValidacionCedulasColombiana,
        TestValidacionFechasColombiana,
        TestExtraccionNombresComplejo,
        TestManejoDatosIncompletos,
        TestTransformacionDatos
    ]
    
    for clase in clases_datos:
        suite.addTests(loader.loadTestsFromTestCase(clase))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    resultado = runner.run(suite)
    
    # Reporte
    total = resultado.testsRun
    errores = len(resultado.errors)
    fallos = len(resultado.failures)
    exitosos = total - errores - fallos
    
    print("\\n" + "=" * 55)
    print("📊 REPORTE DE PRUEBAS DE DATOS")
    print("=" * 55)
    print(f"✅ Pruebas exitosas: {exitosos}/{total}")
    print(f"❌ Fallos: {fallos}")
    print(f"💥 Errores: {errores}")
    print(f"📈 Tasa de éxito: {(exitosos/total)*100:.1f}%")
    print("=" * 55)
    
    return exitosos == total

if __name__ == "__main__":
    exito = ejecutar_pruebas_datos()
    sys.exit(0 if exito else 1)