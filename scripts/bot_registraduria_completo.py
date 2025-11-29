"""
Script Completo para Consulta Automática de Cédula en Registraduría
Incluye resolución automática de CAPTCHA con OCR
"""

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
import os

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class RegistraduriaBot:
    """
    Bot automatizado para consultas en la Registraduría
    """
    
    def __init__(self, headless=False):
        """
        Inicializar el bot
        
        Args:
            headless (bool): Ejecutar en modo sin interfaz gráfica
        """
        self.driver = None
        self.headless = headless
        self.wait = None
        
    def configurar_driver(self):
        """Configurar y crear el WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        service = Service("C:\\chromedriver\\chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        
        return self.driver
    
    def procesar_captcha(self):
        """
        Procesar CAPTCHA automáticamente usando OCR
        
        Returns:
            str: Texto extraído del CAPTCHA
        """
        try:
            print("   🔍 Analizando CAPTCHA con OCR...")
            
            # Tomar screenshot del elemento CAPTCHA
            captcha_element = self.driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
            captcha_screenshot = captcha_element.screenshot_as_png
            
            # Convertir a imagen PIL
            image = Image.open(io.BytesIO(captcha_screenshot))
            
            # Preprocesar imagen
            image_procesada = self.preprocesar_imagen(image)
            
            # Configurar OCR para CAPTCHA
            config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Extraer texto con diferentes configuraciones
            resultados = []
            
            # Configuración 1: Estándar
            try:
                texto1 = pytesseract.image_to_string(image_procesada, config=config).strip()
                if texto1:
                    resultados.append(texto1)
            except:
                pass
            
            # Configuración 2: Solo letras
            try:
                config2 = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                texto2 = pytesseract.image_to_string(image_procesada, config=config2).strip()
                if texto2:
                    resultados.append(texto2)
            except:
                pass
            
            # Configuración 3: Con imagen original
            try:
                texto3 = pytesseract.image_to_string(image, config=config).strip()
                if texto3:
                    resultados.append(texto3)
            except:
                pass
            
            # Seleccionar el mejor resultado
            if resultados:
                # Limpiar y filtrar resultados
                resultados_limpios = [self.limpiar_texto_captcha(r) for r in resultados if r]
                resultados_filtrados = [r for r in resultados_limpios if len(r) >= 3 and len(r) <= 6]
                
                if resultados_filtrados:
                    mejor_resultado = max(resultados_filtrados, key=len)
                    print(f"   ✓ CAPTCHA extraído: '{mejor_resultado}' (de {len(resultados)} intentos)")
                    
                    # Guardar imagen para verificación
                    timestamp = int(time.time())
                    image.save(f"captcha_{timestamp}.png")
                    with open(f"captcha_{timestamp}.txt", "w") as f:
                        f.write(f"Todos los resultados: {resultados}\n")
                        f.write(f"Resultado final: {mejor_resultado}\n")
                    
                    return mejor_resultado
            
            print("   ⚠️ No se pudo extraer texto del CAPTCHA")
            return ""
            
        except Exception as e:
            print(f"   ❌ Error procesando CAPTCHA: {e}")
            return ""
    
    def preprocesar_imagen(self, image):
        """Preprocesar imagen para mejorar OCR"""
        try:
            # Convertir a escala de grises
            if image.mode != 'L':
                image = image.convert('L')
            
            # Redimensionar (más grande = mejor OCR)
            width, height = image.size
            image = image.resize((width * 4, height * 4), Image.LANCZOS)
            
            # Mejorar contraste y nitidez
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.5)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convertir a array para OpenCV
            img_array = np.array(image)
            
            # Umbralización adaptativa
            img_thresh = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Operaciones morfológicas para limpiar ruido
            kernel = np.ones((2, 2), np.uint8)
            img_clean = cv2.morphologyEx(img_thresh, cv2.MORPH_CLOSE, kernel)
            img_clean = cv2.morphologyEx(img_clean, cv2.MORPH_OPEN, kernel)
            
            return Image.fromarray(img_clean)
            
        except Exception as e:
            print(f"   ⚠️ Error en preprocesamiento: {e}")
            return image
    
    def limpiar_texto_captcha(self, texto):
        """Limpiar y corregir texto extraído"""
        if not texto:
            return ""
        
        # Remover caracteres no alfanuméricos
        texto_limpio = ''.join(c for c in texto if c.isalnum())
        
        # Convertir a mayúsculas
        texto_limpio = texto_limpio.upper()
        
        # Correcciones comunes de OCR
        correcciones = {
            '0': 'O', '1': 'I', '5': 'S', '8': 'B', '6': 'G',
            'i': 'I', 'l': 'I', 'o': 'O', 's': 'S'
        }
        
        texto_corregido = ""
        for char in texto_limpio:
            texto_corregido += correcciones.get(char, char)
        
        return texto_corregido
    
    def consultar_cedula(self, cedula, dia, mes, año, intentos_captcha=3, enviar_automatico=False):
        """
        Realizar consulta completa de cédula
        
        Args:
            cedula (str): Número de cédula
            dia (str): Día de expedición
            mes (str): Mes de expedición
            año (str): Año de expedición
            intentos_captcha (int): Número de intentos para resolver CAPTCHA
            enviar_automatico (bool): Enviar formulario automáticamente
            
        Returns:
            dict: Resultado de la consulta
        """
        resultado = {
            'exito': False,
            'cedula': cedula,
            'fecha': f"{dia}/{mes}/{año}",
            'captcha_resuelto': False,
            'captcha_texto': '',
            'formulario_enviado': False,
            'error': None,
            'url_resultado': None
        }
        
        try:
            print("🏛️ INICIANDO CONSULTA AUTOMÁTICA DE CÉDULA")
            print("=" * 60)
            
            # Configurar driver
            self.configurar_driver()
            
            # Abrir página
            print("1️⃣ Abriendo página de la Registraduría...")
            self.driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
            time.sleep(3)
            print(f"   ✓ Página cargada: {self.driver.title}")
            
            # Llenar cédula
            print("2️⃣ Ingresando número de cédula...")
            cedula_field = self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
            cedula_field.clear()
            cedula_field.send_keys(cedula)
            print(f"   ✓ Cédula ingresada: {cedula}")
            
            # Seleccionar fecha
            print("3️⃣ Seleccionando fecha de expedición...")
            
            # Día
            dia_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
            dia_formato = f"{int(dia):02d}"
            dia_dropdown.select_by_value(dia_formato)
            
            # Mes
            mes_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
            meses = {
                "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
                "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
                "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
            }
            mes_nombre = meses.get(str(int(mes)), str(mes))
            mes_dropdown.select_by_visible_text(mes_nombre)
            
            # Año
            año_dropdown = Select(self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
            año_dropdown.select_by_visible_text(str(año))
            
            print(f"   ✓ Fecha seleccionada: {dia_formato}/{mes_nombre}/{año}")
            
            # Resolver CAPTCHA
            print("4️⃣ Resolviendo CAPTCHA...")
            captcha_resuelto = False
            
            # Primer intento automático
            print("   🤖 Intento automático con OCR...")
            captcha_texto = self.procesar_captcha()
            
            if captcha_texto and len(captcha_texto) >= 3:
                # Ingresar código CAPTCHA automáticamente
                codigo_field = self.wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox2")))
                codigo_field.clear()
                codigo_field.send_keys(captcha_texto)
                
                resultado['captcha_texto'] = captcha_texto
                resultado['captcha_resuelto'] = True
                captcha_resuelto = True
                print(f"   ✅ CAPTCHA resuelto automáticamente: '{captcha_texto}'")
            else:
                print("   ❌ OCR falló, cambiando a modo manual")
                
                if not self.headless:
                    # Modo manual
                    print("   📝 MODO MANUAL ACTIVADO")
                    print("   🔍 Observa la imagen CAPTCHA en el navegador")
                    
                    # Resaltar campo para ingreso manual
                    codigo_field = self.driver.find_element(By.ID, "ContentPlaceHolder1_TextBox2")
                    self.driver.execute_script("arguments[0].style.border='5px solid red'", codigo_field)
                    self.driver.execute_script("arguments[0].style.backgroundColor='#ffffaa'", codigo_field)
                    self.driver.execute_script("arguments[0].focus()", codigo_field)
                    
                    # Esperar ingreso manual
                    print("   ⏳ Esperando ingreso manual del CAPTCHA...")
                    print("   💡 Ingresa el código y presiona Enter, o espera 60 segundos")
                    
                    tiempo_espera = 60
                    inicio = time.time()
                    
                    while time.time() - inicio < tiempo_espera:
                        try:
                            # Verificar si se ingresó texto
                            valor_actual = codigo_field.get_attribute("value")
                            if valor_actual and len(valor_actual.strip()) >= 3:
                                captcha_resuelto = True
                                resultado['captcha_texto'] = valor_actual.strip().upper()
                                resultado['captcha_resuelto'] = True
                                print(f"   ✅ CAPTCHA ingresado manualmente: '{resultado['captcha_texto']}'")
                                break
                        except:
                            pass
                        
                        time.sleep(1)
                    
                    if not captcha_resuelto:
                        print("   ⚠️ Tiempo agotado para ingreso manual")
                        resultado['error'] = "CAPTCHA no ingresado manualmente"
                else:
                    print("   ❌ Modo headless: no se puede ingresar manualmente")
                    resultado['error'] = "CAPTCHA no resuelto (modo headless)"
            
            # Enviar formulario
            if captcha_resuelto and enviar_automatico:
                print("5️⃣ Enviando formulario...")
                try:
                    # Scroll para asegurar que el botón esté visible
                    continuar_btn = self.driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
                    self.driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
                    time.sleep(1)
                    
                    # Intentar clic normal primero
                    try:
                        continuar_btn.click()
                    except:
                        # Si falla, usar JavaScript click
                        self.driver.execute_script("arguments[0].click();", continuar_btn)
                    
                    # Esperar respuesta
                    time.sleep(5)
                    resultado['formulario_enviado'] = True
                    resultado['url_resultado'] = self.driver.current_url
                    
                    print(f"   ✅ Formulario enviado")
                    print(f"   📄 URL resultado: {resultado['url_resultado']}")
                    print(f"   📝 Título: {self.driver.title}")
                    
                except Exception as e:
                    print(f"   ❌ Error enviando formulario: {e}")
                    print(f"   💡 CAPTCHA resuelto correctamente, puedes hacer clic manualmente en 'Continuar'")
                    resultado['error'] = str(e)
            
            resultado['exito'] = captcha_resuelto
            
            # Mantener navegador abierto si no es headless
            if not self.headless:
                tiempo_espera = 30 if captcha_resuelto else 60
                print(f"\n🖥️ Navegador permanecerá abierto {tiempo_espera} segundos...")
                time.sleep(tiempo_espera)
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            resultado['error'] = str(e)
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Sesión finalizada")
        
        return resultado

def main():
    """Función principal para ejecutar consulta"""
    print("🤖 BOT AUTOMATIZADO - CONSULTA DE CÉDULA")
    print("=" * 50)
    
    # Datos de consulta - PERSONALIZAR AQUÍ
    cedula = "1234567890"
    dia = "15"
    mes = "6"  # Junio
    año = "2020"
    
    # Crear bot
    bot = RegistraduriaBot(headless=False)  # Cambiar a True para modo sin interfaz
    
    # Realizar consulta
    resultado = bot.consultar_cedula(
        cedula=cedula,
        dia=dia,
        mes=mes,
        año=año,
        intentos_captcha=3,
        enviar_automatico=True  # Cambiar a False para envío manual
    )
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADO DE LA CONSULTA")
    print("=" * 60)
    print(f"✅ Éxito: {'Sí' if resultado['exito'] else 'No'}")
    print(f"🆔 Cédula: {resultado['cedula']}")
    print(f"📅 Fecha: {resultado['fecha']}")
    print(f"🤖 CAPTCHA resuelto: {'Sí' if resultado['captcha_resuelto'] else 'No'}")
    if resultado['captcha_texto']:
        print(f"🔤 Texto CAPTCHA: {resultado['captcha_texto']}")
    print(f"📤 Formulario enviado: {'Sí' if resultado['formulario_enviado'] else 'No'}")
    if resultado['url_resultado']:
        print(f"🌐 URL resultado: {resultado['url_resultado']}")
    if resultado['error']:
        print(f"❌ Error: {resultado['error']}")
    print("=" * 60)

if __name__ == "__main__":
    main()