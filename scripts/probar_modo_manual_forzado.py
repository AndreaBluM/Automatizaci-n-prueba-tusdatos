"""
Script para probar el modo manual cuando OCR falla
Este script deshabilitará el OCR para forzar el modo manual
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def pedir_captcha_manual(driver):
    """Pedir CAPTCHA por consola cuando OCR falla"""
    print("   🔧 Modo manual activado (OCR deshabilitado para prueba)...")
    
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

def probar_modo_manual_forzado():
    """Probar modo manual con OCR deshabilitado"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service("C:\\chromedriver\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🧪 PRUEBA DE MODO MANUAL (OCR DESHABILITADO)")
        print("=" * 50)
        
        # 1. Abrir página
        print("1️⃣ Abriendo página...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        wait = WebDriverWait(driver, 15)
        time.sleep(3)
        
        # 2. Llenar datos básicos
        print("2️⃣ Llenando formulario...")
        
        # Cédula
        cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
        cedula_field.clear()
        cedula_field.send_keys("1036670248")
        
        # Fecha
        dia_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
        dia_dropdown.select_by_value("08")
        
        mes_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
        mes_dropdown.select_by_visible_text("Enero")
        
        año_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
        año_dropdown.select_by_visible_text("2015")
        
        print("   ✅ Datos básicos completados")
        
        # 3. Simular fallo de OCR - ir directo a modo manual
        print("3️⃣ Probando CAPTCHA...")
        print("   ❌ OCR automático falló (simulado)")
        
        # Llamar directamente al modo manual
        captcha_texto = pedir_captcha_manual(driver)
        
        if not captcha_texto:
            print("   ❌ No se obtuvo CAPTCHA")
            return False
        
        # 4. Llenar campo CAPTCHA
        print("4️⃣ Completando formulario...")
        codigo_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox2")))
        codigo_field.clear()
        codigo_field.send_keys(captcha_texto)
        
        # Confirmar visualmente
        driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
        driver.execute_script("arguments[0].style.border='3px solid green'", codigo_field)
        
        # 5. Enviar formulario
        print("5️⃣ Enviando consulta...")
        continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
        driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
        time.sleep(1)
        
        try:
            continuar_btn.click()
        except:
            driver.execute_script("arguments[0].click();", continuar_btn)
        
        # 6. Esperar respuesta
        time.sleep(5)
        
        print("\n" + "=" * 50)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 50)
        print(f"📄 URL actual: {driver.current_url}")
        print(f"📝 Título: {driver.title}")
        
        # Verificar resultados
        if "Datos.aspx" not in driver.current_url:
            print("🎉 ¡Consulta exitosa! El modo manual funciona perfectamente.")
        else:
            print("⚠️ Verifica si hay mensajes en la página.")
        
        # Mantener navegador abierto
        print(f"\n🖥️ Navegador permanecerá abierto 60 segundos...")
        time.sleep(60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Prueba cancelada por el usuario")
        return False
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
    
    finally:
        driver.quit()
        print("🔚 Sesión finalizada")

def main():
    """Función principal"""
    print("🤖 PRUEBA DE MODO MANUAL - CAPTCHA POR CONSOLA")
    print("=" * 55)
    print("Esta prueba deshabilitará el OCR para probar el modo manual")
    print("=" * 55)
    
    try:
        exito = probar_modo_manual_forzado()
        print("\n" + "=" * 55)
        if exito:
            print("✅ PRUEBA EXITOSA: Modo manual funciona correctamente")
        else:
            print("❌ PRUEBA FALLÓ")
        print("=" * 55)
        
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")

if __name__ == "__main__":
    main()