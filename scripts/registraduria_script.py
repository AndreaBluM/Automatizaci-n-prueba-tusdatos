from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import io
import requests

# Configurar ruta de Tesseract (ajustar según instalación)
# Para Windows, descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def procesar_captcha_imagen(image_url, driver):
    """
    Procesa la imagen CAPTCHA usando OCR
    
    Args:
        image_url (str): URL de la imagen CAPTCHA
        driver: Instancia del WebDriver
        
    Returns:
        str: Texto extraído del CAPTCHA
    """
    try:
        print("   🔍 Procesando imagen CAPTCHA con OCR...")
        
        # Método 1: Tomar screenshot del elemento CAPTCHA
        try:
            captcha_element = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
            captcha_screenshot = captcha_element.screenshot_as_png
            
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(captcha_screenshot))
            
        except Exception as e:
            print(f"   ⚠️ Error con screenshot del elemento, intentando descargar imagen: {e}")
            
            # Método 2: Descargar imagen directamente
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Convertir a imagen PIL
            image = Image.open(io.BytesIO(response.content))
        
        # Preprocesar imagen para mejorar OCR
        image = preprocesar_imagen_captcha(image)
        
        # Configurar Tesseract para CAPTCHA
        config_tesseract = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Extraer texto
        texto_captcha = pytesseract.image_to_string(image, config=config_tesseract).strip()
        
        # Limpiar el texto extraído
        texto_limpio = limpiar_texto_captcha(texto_captcha)
        
        print(f"   ✓ Texto CAPTCHA extraído: '{texto_limpio}'")
        
        return texto_limpio
        
    except Exception as e:
        print(f"   ❌ Error procesando CAPTCHA: {e}")
        return ""

def preprocesar_imagen_captcha(image):
    """
    Preprocesa la imagen CAPTCHA para mejorar la precisión del OCR
    
    Args:
        image (PIL.Image): Imagen original
        
    Returns:
        PIL.Image: Imagen procesada
    """
    try:
        # Convertir a escala de grises
        if image.mode != 'L':
            image = image.convert('L')
        
        # Redimensionar imagen (hacer más grande para mejor OCR)
        width, height = image.size
        new_width = width * 3
        new_height = height * 3
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Aumentar nitidez
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Aplicar filtro para reducir ruido
        image = image.filter(ImageFilter.MedianFilter())
        
        # Convertir a array NumPy para OpenCV
        img_array = np.array(image)
        
        # Aplicar umbralización adaptativa
        img_thresh = cv2.adaptiveThreshold(
            img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Aplicar operaciones morfológicas para limpiar
        kernel = np.ones((1, 1), np.uint8)
        img_clean = cv2.morphologyEx(img_thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convertir de vuelta a PIL
        image_final = Image.fromarray(img_clean)
        
        return image_final
        
    except Exception as e:
        print(f"   ⚠️ Error en preprocesamiento, usando imagen original: {e}")
        return image

def limpiar_texto_captcha(texto):
    """
    Limpia y corrige el texto extraído del CAPTCHA
    
    Args:
        texto (str): Texto original extraído
        
    Returns:
        str: Texto limpiado
    """
    if not texto:
        return ""
    
    # Remover espacios y caracteres no deseados
    texto = ''.join(c for c in texto if c.isalnum())
    
    # Correcciones comunes de OCR
    correcciones = {
        '0': 'O', '1': 'I', '5': 'S', '8': 'B',
        'i': 'I', 'l': 'I', 'o': 'O', 's': 'S'
    }
    
    texto_corregido = ""
    for char in texto.upper():
        texto_corregido += correcciones.get(char, char)
    
    return texto_corregido

def verificar_tesseract():
    """
    Verifica si Tesseract está instalado y configurado
    
    Returns:
        bool: True si está disponible
    """
    try:
        pytesseract.get_tesseract_version()
        return True
    except:
        print("⚠️ Tesseract no está instalado o configurado correctamente")
        print("📥 Descarga Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki")
        print("🔧 Descomenta y ajusta la línea: pytesseract.pytesseract.tesseract_cmd")
        return False

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Configurar el servicio con ChromeDriver
service = Service("C:\\chromedriver\\chromedriver.exe")

# Crear el driver
driver = webdriver.Chrome(service=service, options=chrome_options)

def llenar_formulario(cedula, dia, mes, año, codigo_imagen):
    """
    Función para llenar el formulario de consulta de cédula usando los selectores correctos
    """
    try:
        print("Abriendo página de la Registraduría...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        
        # Esperar a que la página cargue completamente
        wait = WebDriverWait(driver, 10)
        time.sleep(3)  # Tiempo adicional para cargar completamente
        
        print(f"✓ Página cargada: {driver.title}")
        
        # 1. Llenar campo de cédula (primer campo de texto)
        print("1. Llenando campo de cédula...")
        try:
            cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
            cedula_field.clear()
            cedula_field.send_keys(cedula)
            print(f"   ✓ Cédula ingresada: {cedula}")
        except Exception as e:
            print(f"   ❌ Error ingresando cédula: {e}")
            return False
        
        # 2. Seleccionar día de expedición
        print("2. Seleccionando fecha de expedición...")
        try:
            dia_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
            # Asegurar formato de 2 dígitos
            dia_formato = f"{int(dia):02d}"
            dia_dropdown.select_by_value(dia_formato)
            print(f"   ✓ Día seleccionado: {dia_formato}")
        except Exception as e:
            print(f"   ❌ Error seleccionando día: {e}")
        
        # 3. Seleccionar mes de expedición
        try:
            mes_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
            
            # Mapear número de mes a nombre
            meses = {
                "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
                "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
                "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
                "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
                "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
                "9": "Septiembre"
            }
            
            mes_nombre = meses.get(str(mes), mes)
            mes_dropdown.select_by_visible_text(mes_nombre)
            print(f"   ✓ Mes seleccionado: {mes_nombre}")
        except Exception as e:
            print(f"   ❌ Error seleccionando mes: {e}")
        
        # 4. Seleccionar año de expedición
        try:
            año_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
            año_dropdown.select_by_visible_text(str(año))
            print(f"   ✓ Año seleccionado: {año}")
        except Exception as e:
            print(f"   ❌ Error seleccionando año: {e}")
        
        # 5. Procesar CAPTCHA automáticamente
        print("3. Procesando CAPTCHA...")
        captcha_texto_final = ""
        
        try:
            # Verificar si Tesseract está disponible
            if not verificar_tesseract():
                print("   ⚠️ Tesseract no disponible, CAPTCHA debe ingresarse manualmente")
                captcha_texto_final = codigo_imagen
            else:
                captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
                captcha_src = captcha_img.get_attribute("src")
                print(f"   ✓ Imagen CAPTCHA encontrada")
                print(f"   🖼️ URL: {captcha_src[:80]}...")
                
                # Intentar resolver CAPTCHA automáticamente solo si no se proporcionó código manual
                if not codigo_imagen:
                    print("   🤖 Intentando resolver automáticamente...")
                    captcha_texto_ocr = procesar_captcha_imagen(captcha_src, driver)
                    
                    if captcha_texto_ocr and len(captcha_texto_ocr) >= 3:
                        captcha_texto_final = captcha_texto_ocr
                        print(f"   ✅ CAPTCHA resuelto automáticamente: '{captcha_texto_final}'")
                    else:
                        print("   ❌ OCR falló, activando modo manual")
                        print("   📝 Observa la imagen CAPTCHA en el navegador")
                        print("   💡 El campo estará resaltado para ingreso manual")
                        captcha_texto_final = ""  # Forzar ingreso manual
                else:
                    captcha_texto_final = codigo_imagen
                    print(f"   📝 Usando código proporcionado: '{captcha_texto_final}'")
                
        except Exception as e:
            print(f"   ❌ Error procesando CAPTCHA: {e}")
            print("   🔧 Cambiando a modo manual")
            captcha_texto_final = ""
        
        # 6. Llenar campo de código CAPTCHA
        print("4. Llenando código CAPTCHA...")
        try:
            codigo_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox2")))
            
            if captcha_texto_final:
                # Modo automático exitoso
                codigo_field.clear()
                codigo_field.send_keys(captcha_texto_final)
                print(f"   ✓ Código CAPTCHA ingresado automáticamente: '{captcha_texto_final}'")
                
                # Guardar imagen y texto para verificación
                try:
                    timestamp = int(time.time())
                    captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
                    captcha_img.screenshot(f"captcha_{timestamp}.png")
                    print(f"   💾 Screenshot guardado: captcha_{timestamp}.png")
                    
                    with open(f"captcha_{timestamp}.txt", "w") as f:
                        f.write(f"Texto extraído: {captcha_texto_final}")
                    
                except:
                    pass
                
            else:
                # Modo manual por consola
                print("   🔧 MODO MANUAL POR CONSOLA ACTIVADO")
                print("   📝 El OCR automático no pudo resolver el CAPTCHA")
                
                # Resaltar imagen CAPTCHA para que sea más visible
                try:
                    captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
                    driver.execute_script("arguments[0].style.border='5px solid red'", captcha_img)
                    driver.execute_script("arguments[0].scrollIntoView();", captcha_img)
                except:
                    pass
                
                # Pedir al usuario que vea el CAPTCHA en el navegador
                print("\n" + "="*50)
                print("🔍 MIRA LA IMAGEN CAPTCHA EN EL NAVEGADOR")
                print("="*50)
                print("📋 La imagen CAPTCHA está resaltada con un borde rojo")
                print("💡 Escribe exactamente lo que ves en la imagen")
                
                while True:
                    try:
                        captcha_usuario = input("\n🤖 ¿Qué dice el CAPTCHA? (3-6 caracteres): ").strip().upper()
                        
                        if len(captcha_usuario) >= 3 and captcha_usuario.isalnum():
                            captcha_texto_final = captcha_usuario
                            print(f"   ✅ CAPTCHA ingresado: '{captcha_texto_final}'")
                            
                            # Llenar el campo automáticamente
                            codigo_field.clear()
                            codigo_field.send_keys(captcha_texto_final)
                            
                            # Cambiar color del campo para confirmar
                            driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
                            driver.execute_script("arguments[0].style.border='3px solid green'", codigo_field)
                            
                            print("   📝 Campo CAPTCHA completado automáticamente")
                            break
                        else:
                            print("   ❌ Ingresa al menos 3 caracteres alfanuméricos")
                            
                    except KeyboardInterrupt:
                        print("\n   ⚠️ Proceso cancelado por el usuario")
                        break
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        break
                
        except Exception as e:
            print(f"   ❌ Error con campo CAPTCHA: {e}")
        
        # 7. Mostrar botones disponibles
        print("5. Identificando botones...")
        try:
            continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
            regresar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button2")
            
            print("   ✓ Botones encontrados:")
            print("     - Botón 'Continuar' (para enviar formulario)")
            print("     - Botón 'Regresar'")
        except Exception as e:
            print(f"   ❌ Error encontrando botones: {e}")
        
        print("\n" + "="*60)
        print("📋 FORMULARIO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print("✅ Cédula ingresada")
        print("✅ Fecha de expedición seleccionada")
        
        if captcha_texto_final:
            print(f"🤖 CAPTCHA procesado: '{captcha_texto_final}'")
            print("🚀 ¡Formulario listo para enviar!")
            
            # Envío automático cuando el CAPTCHA está resuelto
            print("5. Enviando formulario automáticamente...")
            try:
                continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
                
                # Scroll para asegurar que el botón esté visible
                driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
                time.sleep(1)
                
                # Intentar clic
                try:
                    continuar_btn.click()
                except:
                    # Si falla, usar JavaScript
                    driver.execute_script("arguments[0].click();", continuar_btn)
                
                print("   ✅ Formulario enviado automáticamente")
                
                # Esperar respuesta
                time.sleep(5)
                print(f"   📄 Página actual: {driver.current_url}")
                print(f"   📝 Título: {driver.title}")
                
                # Verificar si hay resultados o errores
                try:
                    # Buscar mensajes de error comunes
                    error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .mensaje-error")
                    if error_elements:
                        print("   ⚠️ Posibles mensajes en la página:")
                        for elem in error_elements[:3]:  # Primeros 3 mensajes
                            if elem.text.strip():
                                print(f"      • {elem.text.strip()}")
                    
                    # Verificar si cambió la URL (indicaría éxito)
                    if "Datos.aspx" not in driver.current_url:
                        print("   🎉 ¡Consulta procesada exitosamente!")
                    
                except:
                    pass
                    
            except Exception as e:
                print(f"   ❌ Error enviando formulario: {e}")
                print("   💡 Puedes hacer clic manualmente en el botón 'Continuar'")
            
        else:
            print("⚠️ CAPTCHA requiere ingreso manual")
            print("🔍 Revisa la imagen CAPTCHA y completa el campo")
            print("🖱️ Después haz clic en 'Continuar' para enviar")
        
        print("="*60)
        
        # Mantener el navegador abierto
        tiempo_espera = 30 if captcha_texto_final else 120
        print(f"\n🖥️ Navegador permanecerá abierto por {tiempo_espera} segundos...")
        
        if not captcha_texto_final:
            print("💡 Completa el CAPTCHA manualmente y haz clic en 'Continuar'")
        else:
            print("💡 Puedes revisar los resultados de la consulta")
        
        time.sleep(tiempo_espera)
        
        return True
        
    except Exception as e:
        print(f"❌ Error llenando formulario: {e}")
        return False

# Datos de ejemplo - CAMBIA ESTOS VALORES POR DATOS REALES
cedula_numero = "1234567890"  # Número de cédula (10 dígitos)
dia_expedicion = "15"         # Día de expedición (01-31)
mes_expedicion = "6"          # Mes de expedición (1-12 o nombre del mes)
año_expedicion = "2020"       # Año de expedición
codigo_captcha = ""           # Déjalo vacío - se resolverá automáticamente

try:
    print("🤖 INICIANDO BOT AUTOMATIZADO DE REGISTRADURÍA")
    print("=" * 60)
    print(f"📋 Datos a consultar:")
    print(f"   • Cédula: {cedula_numero}")
    print(f"   • Fecha expedición: {dia_expedicion}/{mes_expedicion}/{año_expedicion}")
    print("=" * 60)
    
    # Ejecutar la función completamente automática
    exito = llenar_formulario(cedula_numero, dia_expedicion, mes_expedicion, año_expedicion, codigo_captcha)
    
    print("\n" + "=" * 60)
    if exito:
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("🎉 Consulta de cédula procesada automáticamente")
    else:
        print("⚠️ PROCESO COMPLETADO CON ADVERTENCIAS")
        print("💡 Revisa los mensajes anteriores para más detalles")
    print("=" * 60)
        
except Exception as e:
    print(f"\n❌ Error general del sistema: {e}")
    
finally:
    driver.quit()
    print("🔚 Sesión finalizada.")