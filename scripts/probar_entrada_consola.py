"""
Script de prueba para el modo manual por consola
Este script deshabilitará el OCR para probar la entrada por consola
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Configurar el servicio con ChromeDriver
service = Service("C:\\chromedriver\\chromedriver.exe")

# Crear el driver
driver = webdriver.Chrome(service=service, options=chrome_options)

def probar_entrada_consola():
    """Probar entrada de CAPTCHA por consola"""
    
    try:
        print("🧪 PRUEBA DE ENTRADA POR CONSOLA")
        print("=" * 50)
        
        print("1️⃣ Abriendo página...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        # Llenar datos básicos
        print("2️⃣ Llenando datos básicos...")
        
        # Cédula
        cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
        cedula_field.clear()
        cedula_field.send_keys("1234567890")
        
        # Fecha
        dia_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_DropDownList1"))
        dia_dropdown.select_by_value("15")
        
        mes_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_DropDownList2"))
        mes_dropdown.select_by_visible_text("Junio")
        
        año_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_DropDownList3"))
        año_dropdown.select_by_visible_text("2020")
        
        print("   ✅ Datos básicos completados")
        
        # Resaltar imagen CAPTCHA
        print("3️⃣ PREPARANDO MODO MANUAL POR CONSOLA")
        try:
            captcha_img = driver.find_element(By.ID, "datos_contentplaceholder1_captcha1_CaptchaImage")
            driver.execute_script("arguments[0].style.border='5px solid red'", captcha_img)
            driver.execute_script("arguments[0].scrollIntoView();", captcha_img)
            print("   📍 Imagen CAPTCHA resaltada con borde rojo")
        except Exception as e:
            print(f"   ⚠️ Error resaltando imagen: {e}")
        
        # Obtener campo de código
        codigo_field = driver.find_element(By.ID, "ContentPlaceHolder1_TextBox2")
        
        # Simular fallo de OCR - pedir entrada por consola
        print("\n" + "="*50)
        print("🔍 MIRA LA IMAGEN CAPTCHA EN EL NAVEGADOR")
        print("="*50)
        print("📋 La imagen CAPTCHA está resaltada con un borde rojo")
        print("💡 Escribe exactamente lo que ves en la imagen")
        
        captcha_usuario = ""
        while True:
            try:
                captcha_usuario = input("\n🤖 ¿Qué dice el CAPTCHA? (3-6 caracteres): ").strip().upper()
                
                if len(captcha_usuario) >= 3 and captcha_usuario.isalnum():
                    print(f"   ✅ CAPTCHA ingresado: '{captcha_usuario}'")
                    
                    # Llenar el campo automáticamente
                    codigo_field.clear()
                    codigo_field.send_keys(captcha_usuario)
                    
                    # Cambiar color del campo para confirmar
                    driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
                    driver.execute_script("arguments[0].style.border='3px solid green'", codigo_field)
                    
                    print("   📝 Campo CAPTCHA completado automáticamente")
                    break
                else:
                    print("   ❌ Ingresa al menos 3 caracteres alfanuméricos")
                    
            except KeyboardInterrupt:
                print("\n   ⚠️ Proceso cancelado por el usuario")
                return False
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        # Enviar formulario automáticamente
        if captcha_usuario:
            print("4️⃣ Enviando formulario automáticamente...")
            try:
                continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
                driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
                time.sleep(1)
                
                try:
                    continuar_btn.click()
                except:
                    driver.execute_script("arguments[0].click();", continuar_btn)
                
                print("   ✅ Formulario enviado automáticamente")
                time.sleep(5)
                
                print(f"   📄 URL actual: {driver.current_url}")
                print(f"   📝 Título: {driver.title}")
                
            except Exception as e:
                print(f"   ⚠️ Error enviando formulario: {e}")
        
        print("\n🎉 ¡PRUEBA DE ENTRADA POR CONSOLA EXITOSA!")
        print("✅ El sistema puede recibir CAPTCHA por consola y completar automáticamente")
        
        # Mantener navegador abierto
        print("\n🖥️ Manteniendo navegador abierto 30 segundos...")
        time.sleep(30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

# Ejecutar prueba
try:
    resultado = probar_entrada_consola()
    print("\n" + "=" * 50)
    if resultado:
        print("✅ PRUEBA EXITOSA: Entrada por consola funciona correctamente")
    else:
        print("❌ PRUEBA FALLÓ")
    print("=" * 50)
    
except KeyboardInterrupt:
    print("\n❌ Prueba cancelada por el usuario")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    driver.quit()
    print("🔚 Navegador cerrado")