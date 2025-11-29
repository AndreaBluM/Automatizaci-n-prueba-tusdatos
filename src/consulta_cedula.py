"""
Script ejecutable para consulta de cédula con datos reales
Uso: python consulta_cedula.py <cedula> <fecha_dd/mm/yyyy>
Ejemplo: python consulta_cedula.py 1036670248 08/01/2015
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
import json
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import io
import re
import requests
import os
from urllib.parse import urljoin
import base64

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def validar_argumentos():
    """Validar argumentos de línea de comandos"""
    if len(sys.argv) != 3:
        print("❌ USO INCORRECTO")
        print("📋 Uso: python consulta_cedula.py <cedula> <fecha_dd/mm/yyyy>")
        print("📝 Ejemplo: python consulta_cedula.py 1036670248 08/01/2015")
        print("💡 Fecha debe estar en formato DD/MM/YYYY")
        return None, None, None, None
    
    cedula = sys.argv[1].strip()
    fecha = sys.argv[2].strip()
    
    # Validar cédula
    if not cedula.isdigit() or len(cedula) != 10:
        print(f"❌ Cédula inválida: '{cedula}'")
        print("💡 La cédula debe tener exactamente 10 dígitos")
        return None, None, None, None
    
    # Validar y parsear fecha
    try:
        partes_fecha = fecha.split('/')
        if len(partes_fecha) != 3:
            raise ValueError("Formato incorrecto")
        
        dia, mes, año = partes_fecha
        
        # Validar día
        dia_int = int(dia)
        if not (1 <= dia_int <= 31):
            raise ValueError("Día inválido")
        
        # Validar mes
        mes_int = int(mes)
        if not (1 <= mes_int <= 12):
            raise ValueError("Mes inválido")
        
        # Validar año
        año_int = int(año)
        if not (1950 <= año_int <= 2025):
            raise ValueError("Año inválido")
        
        return cedula, dia, str(mes_int), año
        
    except (ValueError, IndexError) as e:
        print(f"❌ Fecha inválida: '{fecha}'")
        print("💡 Use el formato DD/MM/YYYY (ejemplo: 08/01/2015)")
        return None, None, None, None

def procesar_captcha_imagen(image_url, driver):
    """Procesar CAPTCHA con OCR"""
    try:
        # Tomar screenshot del elemento CAPTCHA
        captcha_element = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
        captcha_screenshot = captcha_element.screenshot_as_png
        
        # Convertir a imagen PIL
        image = Image.open(io.BytesIO(captcha_screenshot))
        
        # Preprocesar imagen
        image = preprocesar_imagen_captcha(image)
        
        # Configurar Tesseract
        config_tesseract = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Extraer texto
        texto_captcha = pytesseract.image_to_string(image, config=config_tesseract).strip()
        
        # Limpiar texto
        texto_limpio = ''.join(c for c in texto_captcha if c.isalnum()).upper()
        
        return texto_limpio if len(texto_limpio) >= 3 else ""
        
    except Exception as e:
        return ""

def preprocesar_imagen_captcha(image):
    """Preprocesar imagen para OCR"""
    try:
        if image.mode != 'L':
            image = image.convert('L')
        
        width, height = image.size
        image = image.resize((width * 3, height * 3), Image.LANCZOS)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        img_array = np.array(image)
        img_thresh = cv2.adaptiveThreshold(
            img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return Image.fromarray(img_thresh)
        
    except Exception:
        return image

def pedir_captcha_manual(driver):
    """Pedir CAPTCHA por consola cuando OCR falla"""
    print("   🔧 Activando modo manual...")
    
    # Resaltar imagen CAPTCHA para que sea más visible
    try:
        captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
        driver.execute_script("arguments[0].style.border='5px solid red'", captcha_img)
        driver.execute_script("arguments[0].style.padding='5px'", captcha_img)
        driver.execute_script("arguments[0].scrollIntoView();", captcha_img)
        time.sleep(1)  # Dar tiempo para que se vea el resaltado
    except Exception as e:
        print(f"   ⚠️ Error resaltando imagen: {e}")
    
    print("\n" + "="*50)
    print("🔍 MIRA LA IMAGEN CAPTCHA EN EL NAVEGADOR")
    print("="*50)
    print("📋 La imagen CAPTCHA está resaltada con BORDE ROJO")
    print("💡 Escribe exactamente lo que ves en la imagen")
    print("="*50)
    
    while True:
        try:
            captcha_usuario = input("\n🤖 ¿Qué dice el CAPTCHA? (3-6 caracteres): ").strip().upper()
            
            if len(captcha_usuario) >= 3 and len(captcha_usuario) <= 8 and captcha_usuario.replace(" ", "").isalnum():
                # Limpiar espacios y caracteres extraños
                captcha_limpio = ''.join(c for c in captcha_usuario if c.isalnum())
                print(f"   ✅ CAPTCHA recibido: '{captcha_limpio}'")
                return captcha_limpio
            else:
                print("   ❌ Ingresa entre 3-6 caracteres alfanuméricos (letras y números solamente)")
                print("   💡 Ejemplo: ABC123, HELLO, 12345")
                
        except KeyboardInterrupt:
            print("\n   ❌ Proceso cancelado por el usuario")
            return ""
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return ""

def procesar_certificado_pdf(driver, cedula):
    """Buscar botón Generar Certificado, descargar PDF y extraer datos"""
    
    try:
        print("7️⃣ Procesando certificado...")
        
        # Buscar ESPECÍFICAMENTE el botón "Generar Certificado"
        print("   🔍 Buscando botón ESPECÍFICO 'Generar Certificado'...")
        
        # Selectores MUY específicos solo para "Generar Certificado"
        selectores_especificos = [
            "//input[@value='Generar Certificado']",
            "//button[text()='Generar Certificado']",
            "//input[@type='submit' and @value='Generar Certificado']",
            "//*[@value='Generar Certificado']"
        ]
        
        boton_certificado = None
        for selector in selectores_especificos:
            try:
                elementos = driver.find_elements(By.XPATH, selector)
                if elementos:
                    elemento = elementos[0]
                    value = elemento.get_attribute("value") or ""
                    texto = elemento.text.strip()
                    print(f"   ✅ Botón 'Generar Certificado' encontrado: value='{value}', texto='{texto}'")
                    boton_certificado = elemento
                    break
            except Exception as e:
                continue
        
        if not boton_certificado:
            print("   ❌ No se encontró botón específico 'Generar Certificado'")
            print("   📄 La página puede no tener opción de generar PDF")
            return None
        
        # Hacer clic en el botón y monitorear cambios
        print("   🖱️ Haciendo clic en 'Generar Certificado'...")
        
        # Contar ventanas antes del clic
        ventanas_antes = len(driver.window_handles)
        url_antes = driver.current_url
        
        try:
            driver.execute_script("arguments[0].scrollIntoView();", boton_certificado)
            time.sleep(1)
            boton_certificado.click()
            print("   ✅ Clic realizado")
        except Exception as e:
            print(f"   ⚠️ Clic normal falló, usando JavaScript: {e}")
            driver.execute_script("arguments[0].click();", boton_certificado)
        
        # Esperar y monitorear cambios
        print("   ⏳ Esperando generación del certificado (10 segundos)...")
        time.sleep(10)
        
        # Verificar si hubo cambios
        ventanas_despues = len(driver.window_handles)
        url_despues = driver.current_url
        
        print(f"   📊 Ventanas: {ventanas_antes} → {ventanas_despues}")
        print(f"   📊 URL cambió: {url_antes != url_despues}")
        
        # Capturar PDF generado automáticamente
        print("   📄 Capturando PDF generado por la consulta...")
        pdf_capturado = capturar_pdf_automatico(driver, cedula)
        
        if pdf_capturado:
            print("   ✅ PDF capturado y procesado exitosamente")
            return pdf_capturado
        else:
            # Fallback: extraer datos del HTML si no hay PDF
            print("   📄 Fallback: Extrayendo datos del HTML...")
            datos_certificado = extraer_datos_del_html(driver, cedula)
            return datos_certificado
            
    except Exception as e:
        print(f"   ❌ Error procesando certificado: {e}")
        return None





def capturar_pdf_automatico(driver, cedula):
    """
    Capturar el PDF generado por la consulta de forma automatizada
    Implementa los 3 puntos solicitados:
    1. Capturar el PDF generado
    2. Descargar automáticamente 
    3. Extraer información del PDF
    """
    
    try:
        print("   🎯 INICIANDO CAPTURA AUTOMÁTICA DE PDF")
        print("   " + "="*50)
        
        # PASO 1: Capturar el PDF generado por la consulta
        pdf_url = detectar_pdf_generado(driver)
        
        if not pdf_url:
            print("   ❌ No se detectó PDF generado")
            return None
        
        print(f"   ✅ PDF detectado: {pdf_url}")
        
        # PASO 2: Descargar el documento de forma automatizada  
        archivo_pdf = descargar_pdf_automatico(driver, pdf_url, cedula)
        
        if not archivo_pdf:
            print("   ❌ Error descargando PDF")
            return None
            
        print(f"   ✅ PDF descargado: {archivo_pdf}")
        
        # PASO 3: Extraer la información contenida en el PDF
        datos_extraidos = parsear_y_extraer_pdf(archivo_pdf, cedula)
        
        if datos_extraidos:
            datos_extraidos["archivo_pdf"] = archivo_pdf
            print("   ✅ Información extraída del PDF exitosamente")
            return datos_extraidos
        else:
            print("   ❌ Error extrayendo información del PDF")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en captura automática: {e}")
        return None

def detectar_pdf_generado(driver):
    """
    Detectar el PDF generado por la consulta usando múltiples métodos
    """
    
    try:
        print("   🔍 Detectando PDF generado...")
        
        # Método 1: Buscar en nuevas ventanas/pestañas
        ventanas = driver.window_handles
        print(f"   📊 Ventanas abiertas: {len(ventanas)}")
        
        if len(ventanas) > 1:
            for i, ventana in enumerate(ventanas):
                driver.switch_to.window(ventana)
                url = driver.current_url
                titulo = driver.title
                
                print(f"   📄 Ventana {i+1}: {titulo}")
                print(f"   🔗 URL: {url}")
                
                if ".pdf" in url.lower() or "pdf" in titulo.lower():
                    print("   ✅ PDF encontrado en nueva ventana")
                    return url
            
            # Volver a ventana original
            driver.switch_to.window(ventanas[0])
        
        # Método 2: Buscar iframes con PDF
        print("   🔍 Buscando iframes con PDF...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute("src") or ""
            print(f"   📄 iframe {i+1}: {src}")
            
            if ".pdf" in src.lower():
                print("   ✅ PDF encontrado en iframe")
                return src
        
        # Método 3: Buscar enlaces de descarga PDF
        print("   🔍 Buscando enlaces de descarga...")
        enlaces_pdf = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        
        for enlace in enlaces_pdf:
            href = enlace.get_attribute("href")
            texto = enlace.text.strip()
            print(f"   🔗 Enlace PDF: '{texto}' -> {href}")
            
            if href:
                print("   ✅ Enlace PDF encontrado")
                return href
        
        # Método 4: JavaScript para detectar PDF
        print("   🔍 Usando JavaScript para detectar PDF...")
        try:
            # Ejecutar JavaScript para buscar PDFs
            pdf_urls = driver.execute_script("""
                var pdfs = [];
                
                // Buscar en todos los enlaces
                var enlaces = document.querySelectorAll('a[href*=".pdf"], a[href*="PDF"]');
                for(var i = 0; i < enlaces.length; i++) {
                    pdfs.push(enlaces[i].href);
                }
                
                // Buscar en iframes
                var iframes = document.querySelectorAll('iframe[src*=".pdf"], iframe[src*="PDF"]');
                for(var i = 0; i < iframes.length; i++) {
                    pdfs.push(iframes[i].src);
                }
                
                return pdfs;
            """)
            
            if pdf_urls:
                print(f"   📋 JavaScript encontró {len(pdf_urls)} PDFs:")
                for url in pdf_urls:
                    print(f"   🔗 {url}")
                return pdf_urls[0]
                
        except Exception as js_error:
            print(f"   ⚠️ Error con JavaScript: {js_error}")
        
        print("   ❌ No se detectó PDF generado")
        return None
        
    except Exception as e:
        print(f"   ❌ Error detectando PDF: {e}")
        return None

def descargar_pdf_automatico(driver, pdf_url, cedula):
    """
    Descargar el documento PDF de forma automatizada
    """
    
    try:
        print("   📥 DESCARGANDO PDF AUTOMÁTICAMENTE")
        print(f"   🔗 URL: {pdf_url}")
        
        # Crear sesión con cookies del navegador
        session = requests.Session()
        
        # Copiar cookies del navegador
        cookies = driver.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        # Headers para simular el navegador
        headers = {
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
            'Referer': driver.current_url,
            'Accept': 'application/pdf,application/*,*/*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Convertir URL relativa a absoluta si es necesario
        if not pdf_url.startswith('http'):
            base_url = driver.current_url
            pdf_url = urljoin(base_url, pdf_url)
            print(f"   🔄 URL convertida: {pdf_url}")
        
        # Realizar descarga
        print("   🌐 Realizando descarga...")
        response = session.get(pdf_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Verificar Content-Type
        content_type = response.headers.get('Content-Type', '')
        print(f"   📋 Content-Type: {content_type}")
        
        if 'pdf' not in content_type.lower():
            print(f"   ⚠️ Advertencia: Content-Type no es PDF")
        
        # Generar nombre de archivo único
        timestamp = int(time.time())
        nombre_archivo = f"certificado_{cedula}_{timestamp}.pdf"
        
        # Guardar archivo
        print(f"   💾 Guardando como: {nombre_archivo}")
        
        with open(nombre_archivo, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verificar archivo guardado
        if os.path.exists(nombre_archivo):
            tamano = os.path.getsize(nombre_archivo)
            print(f"   ✅ Archivo guardado: {tamano} bytes")
            
            if tamano > 0:
                return nombre_archivo
            else:
                print("   ❌ Archivo vacío")
                return None
        else:
            print("   ❌ Error: archivo no existe")
            return None
            
    except Exception as e:
        print(f"   ❌ Error descargando PDF: {e}")
        return None

def parsear_y_extraer_pdf(archivo_pdf, cedula):
    """
    3. Extracción de datos:
    ○ Parsear el contenido del PDF
    ○ Extraer campos relevantes (nombre, número de documento, estado de vigencia, fecha de expedición, etc.)
    ○ Limpiar y estructurar la información extraída
    """
    
    try:
        print("   📄 PARSEANDO Y EXTRAYENDO DATOS DEL PDF")
        print("   " + "="*50)
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo_pdf):
            print(f"   ❌ Archivo no encontrado: {archivo_pdf}")
            return None
        
        tamano = os.path.getsize(archivo_pdf)
        print(f"   📊 Tamaño archivo: {tamano} bytes")
        
        if tamano == 0:
            print("   ❌ Archivo PDF vacío")
            return None
        
        # Estructura de datos para almacenar información extraída
        datos_extraidos = {
            "cedula": cedula,
            "nombre": "",
            "numero_documento": cedula,
            "estado_vigencia": "",
            "fecha_expedicion": "",
            "lugar_expedicion": "",
            "fecha_consulta": time.strftime("%d/%m/%Y %H:%M:%S"),
            "vigente": False,
            "texto_completo": "",
            "campos_extraidos": []
        }
        
        # Intentar múltiples métodos de extracción
        texto_extraido = None
        
        # Método 1: Intentar con PyPDF2 si está disponible
        try:
            import PyPDF2
            print("   📖 Usando PyPDF2 para extraer texto...")
            
            with open(archivo_pdf, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                texto_completo = ""
                
                for i, page in enumerate(reader.pages):
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
                        print(f"   📄 Página {i+1}: {len(texto_pagina)} caracteres")
                
                if texto_completo:
                    texto_extraido = texto_completo
                    print(f"   ✅ PyPDF2 extrajo {len(texto_completo)} caracteres")
                    
        except ImportError:
            print("   ⚠️ PyPDF2 no disponible")
        except Exception as e:
            print(f"   ⚠️ Error con PyPDF2: {e}")
        
        # Método 2: Intentar con pdfplumber si está disponible  
        if not texto_extraido:
            try:
                import pdfplumber
                print("   📖 Usando pdfplumber para extraer texto...")
                
                with pdfplumber.open(archivo_pdf) as pdf:
                    texto_completo = ""
                    
                    for i, pagina in enumerate(pdf.pages):
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            texto_completo += texto_pagina + "\n"
                            print(f"   📄 Página {i+1}: {len(texto_pagina)} caracteres")
                    
                    if texto_completo:
                        texto_extraido = texto_completo
                        print(f"   ✅ pdfplumber extrajo {len(texto_completo)} caracteres")
                        
            except ImportError:
                print("   ⚠️ pdfplumber no disponible")
            except Exception as e:
                print(f"   ⚠️ Error con pdfplumber: {e}")
        
        # Si no se pudo extraer texto
        if not texto_extraido:
            print("   ❌ No se pudo extraer texto del PDF")
            print("   💡 Instala PyPDF2 o pdfplumber: pip install PyPDF2 pdfplumber")
            return None
        
        datos_extraidos["texto_completo"] = texto_extraido
        
        # Extraer campos relevantes usando regex
        print("   🔍 Extrayendo campos relevantes...")
        
        # Patrones regex para extraer información específica
        patrones = {
            "nombre": [
                r'Nombre[s]?[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
                r'NOMBRE[S]?[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
                r'Apellidos y nombres[:\s]+([A-ZÁÉÍÓÚÑ\s]{10,60})',
                r'([A-ZÁÉÍÓÚÑ\s]{15,50})(?=\s*\d{7,})',  # Nombre antes de cédula
            ],
            "estado_vigencia": [
                r'Estado[:\s]+(VIGENTE|NO VIGENTE|VÁLIDA|INVÁLIDA|ACTIVA|INACTIVA)',
                r'(VIGENTE|NO VIGENTE|VÁLIDA|INVÁLIDA|ACTIVA|INACTIVA)',
                r'La cédula.*?(vigente|válida|activa)',
            ],
            "fecha_expedicion": [
                r'Fecha.*?expedición[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'Expedida.*?el[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            ],
            "lugar_expedicion": [
                r'Lugar.*?expedición[:\s]+([A-ZÁÉÍÓÚÑ\s,.-]{5,40})',
                r'Expedida en[:\s]+([A-ZÁÉÍÓÚÑ\s,.-]{5,40})',
            ]
        }
        
        # Aplicar patrones y extraer datos
        for campo, lista_patrones in patrones.items():
            for patron in lista_patrones:
                matches = re.findall(patron, texto_extraido, re.IGNORECASE | re.MULTILINE)
                if matches:
                    valor = matches[0].strip()
                    
                    # Limpiar y estructurar la información
                    if campo == "nombre":
                        valor = re.sub(r'\d+', '', valor).strip()  # Quitar números
                        valor = re.sub(r'\s+', ' ', valor).strip()  # Limpiar espacios
                        if len(valor) >= 10:  # Validar longitud mínima
                            datos_extraidos[campo] = valor
                            datos_extraidos["campos_extraidos"].append(campo)
                            print(f"   ✅ {campo}: {valor}")
                            break
                    
                    elif campo == "estado_vigencia":
                        valor_upper = valor.upper()
                        datos_extraidos[campo] = valor_upper
                        datos_extraidos["vigente"] = valor_upper in ["VIGENTE", "VÁLIDA", "ACTIVA"]
                        datos_extraidos["campos_extraidos"].append(campo)
                        print(f"   ✅ {campo}: {valor_upper} (vigente: {datos_extraidos['vigente']})")
                        break
                    
                    else:
                        datos_extraidos[campo] = valor
                        datos_extraidos["campos_extraidos"].append(campo)
                        print(f"   ✅ {campo}: {valor}")
                        break
            
            if campo not in datos_extraidos["campos_extraidos"]:
                print(f"   ❌ {campo}: No encontrado")
        
        # Mostrar resumen de extracción
        campos_encontrados = len(datos_extraidos["campos_extraidos"])
        print(f"   📊 Campos extraídos: {campos_encontrados}")
        print(f"   📋 Campos: {', '.join(datos_extraidos['campos_extraidos'])}")
        
        if campos_encontrados > 0:
            print("   ✅ Extracción de datos completada")
            return datos_extraidos
        else:
            print("   ❌ No se pudieron extraer campos relevantes")
            return datos_extraidos  # Retornar aunque sea con texto completo
            
    except Exception as e:
        print(f"   ❌ Error parseando PDF: {e}")
        return None

def extraer_datos_del_html(driver, cedula):
    """Extraer datos del certificado directamente del HTML cuando no hay PDF"""
    
    try:
        print("   📄 Extrayendo datos del HTML de la página...")
        
        # Estructura de datos
        datos = {
            "cedula": cedula,
            "nombre": "",
            "estado": "",
            "fecha_expedicion": "",
            "lugar_expedicion": "",
            "fecha_consulta": time.strftime("%d/%m/%Y %H:%M:%S"),
            "vigente": False,
            "archivo_pdf": None,
            "texto_completo": "",
            "fuente": "HTML"
        }
        
        # Obtener todo el HTML de la página
        html_content = driver.page_source
        datos["texto_completo"] = html_content
        
        print(f"   📊 HTML extraído: {len(html_content)} caracteres")
        
        # Buscar elementos específicos del certificado
        try:
            # Buscar el título del certificado
            titulo_elemento = driver.find_element(By.XPATH, "//h2[contains(text(), 'Certificado')]")
            if titulo_elemento:
                print(f"   ✅ Título encontrado: {titulo_elemento.text}")
        except:
            pass
        
        # Extraer texto visible de la página
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            texto_visible = body.text
            print(f"   📝 Texto visible: {len(texto_visible)} caracteres")
            
            # Buscar patrones en el texto visible
            patrones_regex = {
                "nombre": [
                    r'Nombre.*?:\s*([A-ZÁÉÍÓÚÑ\s]{10,50})',
                    r'NOMBRE.*?:\s*([A-ZÁÉÍÓÚÑ\s]{10,50})',
                    r'([A-ZÁÉÍÓÚÑ\s]{15,50})(?=\s*Documento)',
                    r'([A-ZÁÉÍÓÚÑ\s]{15,50})(?=\s*C[eé]dula)',
                    r'([A-ZÁÉÍÓÚÑ\s]{15,50})(?=\s*\d{7,})'
                ],
                "estado": [
                    r'Estado.*?:\s*(VIGENTE|NO VIGENTE|VÁLIDA|INVÁLIDA)',
                    r'(VIGENTE|NO VIGENTE|VÁLIDA|INVÁLIDA)',
                    r'La cédula.*?(vigente|válida)',
                    r'(vigente|válida|activa)',
                    r'Estado.*?(vigente|válida|activa)'
                ],
                "fecha_expedicion": [
                    r'Fecha.*?expedición.*?:\s*(\d{1,2}/\d{1,2}/\d{4})',
                    r'Expedida.*?:\s*(\d{1,2}/\d{1,2}/\d{4})',
                    r'(\d{1,2}/\d{1,2}/\d{4})',
                    r'(\d{4}-\d{2}-\d{2})'
                ],
                "lugar_expedicion": [
                    r'Lugar.*?expedición.*?:\s*([A-ZÁÉÍÓÚÑ\s,.-]{5,40})',
                    r'Expedida en.*?:\s*([A-ZÁÉÍÓÚÑ\s,.-]{5,40})',
                    r'([A-ZÁÉÍÓÚÑ\s]{5,30})(?=\s*Estado|Estado)'
                ]
            }
            
            # Aplicar patrones regex al texto visible
            for campo, patrones in patrones_regex.items():
                encontrado = False
                for patron in patrones:
                    matches = re.findall(patron, texto_visible, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        valor = matches[0].strip()
                        
                        # Limpieza específica por campo
                        if campo == "nombre":
                            valor = re.sub(r'\d+', '', valor).strip()
                            valor = re.sub(r'\s+', ' ', valor).strip()
                            if len(valor) >= 10:
                                datos[campo] = valor
                                print(f"   ✅ {campo}: '{valor}'")
                                encontrado = True
                                break
                        elif campo == "estado":
                            valor_upper = valor.upper()
                            if valor_upper in ["VIGENTE", "VÁLIDA", "ACTIVA"]:
                                datos[campo] = "VIGENTE"
                                datos["vigente"] = True
                            else:
                                datos[campo] = "NO VIGENTE"
                                datos["vigente"] = False
                            print(f"   ✅ {campo}: '{datos[campo]}' (vigente: {datos['vigente']})")
                            encontrado = True
                            break
                        else:
                            datos[campo] = valor
                            print(f"   ✅ {campo}: '{valor}'")
                            encontrado = True
                            break
                
                if not encontrado:
                    print(f"   ❌ {campo}: No encontrado en HTML")
                    
        except Exception as text_error:
            print(f"   ❌ Error extrayendo texto visible: {text_error}")
        
        # Verificar si se encontraron datos útiles
        campos_encontrados = sum(1 for v in [datos["nombre"], datos["estado"], datos["fecha_expedicion"], datos["lugar_expedicion"]] if v)
        print(f"   📊 Campos extraídos del HTML: {campos_encontrados}/4")
        
        if campos_encontrados > 0:
            print("   ✅ Extracción del HTML exitosa")
            return datos
        else:
            print("   ❌ No se pudieron extraer datos del HTML")
            return None
            
    except Exception as e:
        print(f"   ❌ Error extrayendo datos del HTML: {e}")
        return None

def mostrar_resultados_certificado(datos):
    """Mostrar los resultados extraídos del certificado"""
    
    if not datos:
        return
    
    print("\n" + "=" * 60)
    print("📋 INFORMACIÓN EXTRAÍDA DEL CERTIFICADO")
    print("=" * 60)
    
    print(f"🆔 Cédula: {datos.get('cedula', 'N/A')}")
    print(f"👤 Nombre: {datos.get('nombre', 'N/A')}")
    print(f"✅ Estado: {datos.get('estado', 'N/A')}")
    print(f"📅 Fecha expedición: {datos.get('fecha_expedicion', 'N/A')}")
    print(f"📍 Lugar expedición: {datos.get('lugar_expedicion', 'N/A')}")
    print(f"🕐 Fecha consulta: {datos.get('fecha_consulta', 'N/A')}")
    
    if datos.get('vigente'):
        print("🟢 CÉDULA VIGENTE")
    else:
        print("🔴 CÉDULA NO VIGENTE")
    
    print(f"📄 Archivo PDF: {datos.get('archivo_pdf', 'N/A')}")
    
    print("=" * 60)
    print("📊 Los datos se guardarán automáticamente en formato JSON")
    print("=" * 60)

def guardar_datos_json(datos, cedula):
    """Guardar los datos extraídos en un archivo JSON"""
    
    if not datos:
        return None
    
    try:
        # Nombre del archivo JSON
        timestamp = int(time.time())
        # Crear ruta absoluta hacia carpeta output
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        nombre_json = os.path.join(output_dir, f"consulta_{cedula}_{timestamp}.json")
        
        # Agregar metadatos adicionales
        datos_completos = {
            "metadatos": {
                "timestamp": timestamp,
                "fecha_procesamiento": time.strftime("%d/%m/%Y %H:%M:%S"),
                "version_bot": "1.0",
                "fuente": "Registraduría Nacional de Colombia"
            },
            "datos_ciudadano": datos
        }
        
        # Guardar archivo JSON
        with open(nombre_json, 'w', encoding='utf-8') as f:
            json.dump(datos_completos, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Datos guardados en: {nombre_json}")
        return nombre_json
        
    except Exception as e:
        print(f"⚠️ Error guardando JSON: {e}")
        return None
        return nombre_json
        
    except Exception as e:
        print(f"⚠️ Error guardando JSON: {e}")
        return None

def ejecutar_consulta(cedula, dia, mes, año):
    """Ejecutar consulta completa"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service("C:\\chromedriver\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🏛️ CONSULTA REGISTRADURÍA NACIONAL")
        print("=" * 50)
        print(f"🆔 Cédula: {cedula}")
        print(f"📅 Fecha expedición: {dia}/{mes}/{año}")
        print("=" * 50)
        
        # 1. Abrir página
        print("1️⃣ Abriendo página...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        wait = WebDriverWait(driver, 15)
        time.sleep(3)
        
        # 2. Llenar cédula
        print("2️⃣ Ingresando cédula...")
        cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
        cedula_field.clear()
        cedula_field.send_keys(cedula)
        
        # 3. Seleccionar fecha
        print("3️⃣ Seleccionando fecha...")
        
        # Día
        dia_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
        dia_formato = f"{int(dia):02d}"
        dia_dropdown.select_by_value(dia_formato)
        
        # Mes
        mes_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
        meses = {
            "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
            "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
            "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        }
        mes_nombre = meses.get(mes, mes)
        mes_dropdown.select_by_visible_text(mes_nombre)
        
        # Año
        año_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
        año_dropdown.select_by_visible_text(año)
        
        # 4. Resolver CAPTCHA
        print("4️⃣ Resolviendo CAPTCHA...")
        captcha_texto = ""
        
        # Intentar OCR automático primero
        print("   🤖 Intentando OCR automático...")
        try:
            captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
            captcha_src = captcha_img.get_attribute("src")
            captcha_ocr = procesar_captcha_imagen(captcha_src, driver)
            
            # Validación más estricta del OCR
            if captcha_ocr and len(captcha_ocr) >= 3 and len(captcha_ocr) <= 8 and captcha_ocr.isalnum():
                captcha_texto = captcha_ocr
                print(f"   ✅ OCR automático exitoso: '{captcha_texto}'")
            else:
                print(f"   ❌ OCR automático falló. Resultado: '{captcha_ocr}'")
                print("   🔧 Activando modo manual...")
                # Inmediatamente activar modo manual
                captcha_texto = pedir_captcha_manual(driver)
        except Exception as e:
            print(f"   ❌ Error en OCR: {e}")
            print("   🔧 Activando modo manual...")
            # Inmediatamente activar modo manual
            captcha_texto = pedir_captcha_manual(driver)
        
        if not captcha_texto:
            print("   ❌ No se pudo obtener CAPTCHA")
            return False
        
        # 5. Llenar campo CAPTCHA
        print("5️⃣ Completando formulario...")
        codigo_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox2")))
        codigo_field.clear()
        codigo_field.send_keys(captcha_texto)
        
        # Confirmar visualmente
        driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
        driver.execute_script("arguments[0].style.border='3px solid green'", codigo_field)
        
        # 6. Enviar formulario
        print("6️⃣ Enviando consulta...")
        continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
        driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
        time.sleep(1)
        
        try:
            continuar_btn.click()
        except:
            driver.execute_script("arguments[0].click();", continuar_btn)
        
        # 7. Esperar respuesta
        time.sleep(5)
        
        # Verificar si hay alertas de error (CAPTCHA incorrecto)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"\n⚠️ Alerta detectada: {alert_text}")
            
            if "validacion" in alert_text.lower() or "captcha" in alert_text.lower():
                print("❌ CAPTCHA incorrecto detectado")
                alert.accept()  # Cerrar la alerta
                
                # Activar modo manual para retry
                print("🔄 Reintentando con modo manual...")
                captcha_texto = pedir_captcha_manual(driver)
                
                if captcha_texto:
                    # Rellenar el CAPTCHA nuevamente
                    codigo_field = driver.find_element(By.ID, "ContentPlaceHolder1_TextBox2")
                    codigo_field.clear()
                    codigo_field.send_keys(captcha_texto)
                    
                    # Reenviar formulario
                    continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
                    continuar_btn.click()
                    time.sleep(5)
                    
                    # Verificar si hay otra alerta
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print(f"⚠️ Segunda alerta: {alert_text}")
                        alert.accept()
                        print("❌ CAPTCHA sigue siendo incorrecto")
                        return False
                    except:
                        print("✅ No hay más alertas - CAPTCHA aceptado")
                else:
                    print("❌ No se pudo obtener CAPTCHA manual")
                    return False
            else:
                alert.accept()
        except:
            # No hay alertas, continuar normalmente
            pass
        
        print("\n" + "=" * 50)
        print("✅ CONSULTA PROCESADA")
        print("=" * 50)
        print(f"📄 URL actual: {driver.current_url}")
        print(f"📝 Título: {driver.title}")
        
        # Verificar resultados
        if "Datos.aspx" not in driver.current_url:
            print("🎉 ¡Consulta exitosa!")
            
            # Procesar certificado PDF
            datos_certificado = procesar_certificado_pdf(driver, cedula)
            
            if datos_certificado:
                mostrar_resultados_certificado(datos_certificado)
                # Guardar datos en archivo JSON
                archivo_json = guardar_datos_json(datos_certificado, cedula)
                print(f"\n🖥️ Navegador permanecerá abierto 30 segundos...")
                time.sleep(30)
                return datos_certificado
            else:
                print("📋 Revisa los resultados en el navegador manualmente")
                print(f"\n🖥️ Navegador permanecerá abierto 60 segundos...")
                time.sleep(60)
                return True
        else:
            print("⚠️ Verifica si hay mensajes de error en la página.")
            print(f"\n🖥️ Navegador permanecerá abierto 60 segundos...")
            time.sleep(60)
            return False
        
    except Exception as e:
        print(f"❌ Error durante la consulta: {e}")
        return False
    
    finally:
        driver.quit()
        print("🔚 Sesión finalizada")
def ejecutar_consulta_completa(cedula, fecha):
    """
    Función para ejecutar una consulta completa desde otro script
    Retorna los datos extraídos o None si hay error
    """
    try:
        print(f"🤖 CONSULTA AUTOMÁTICA - Cédula: {cedula}")
        
        # Parsear fecha
        partes = fecha.split('/')
        if len(partes) != 3:
            raise ValueError("Formato de fecha inválido")
            
        dia, mes, año = partes[0], partes[1], partes[2]
        
        # Ejecutar consulta
        resultado = ejecutar_bot(cedula, dia, mes, año)
        return resultado
        
    except Exception as e:
        print(f"❌ Error en consulta completa: {e}")
        return None

def main():
    """Función principal"""
    print("🤖 CONSULTA AUTOMÁTICA DE CÉDULA - REGISTRADURÍA")
    print("=" * 55)
    
    # Validar argumentos
    cedula, dia, mes, año = validar_argumentos()
    
    if not cedula:
        print("\n📋 EJEMPLOS DE USO:")
        print("python consulta_cedula.py 1036670248 08/01/2015")
        print("python consulta_cedula.py 1234567890 15/06/2020")
        return
    
    # Ejecutar consulta
    try:
        exito = ejecutar_consulta(cedula, dia, mes, año)
        print("\n" + "=" * 55)
        if exito:
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        else:
            print("❌ PROCESO COMPLETADO CON ERRORES")
        print("=" * 55)
        
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")

if __name__ == "__main__":
    main()