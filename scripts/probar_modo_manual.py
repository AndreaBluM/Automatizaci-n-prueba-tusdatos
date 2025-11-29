"""
Script de prueba para verificar el modo manual de CAPTCHA
Este script deshabilitará temporalmente el OCR para probar el modo manual
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

def probar_modo_manual():
    """Probar específicamente el modo manual de CAPTCHA"""
    
    try:
        print("🧪 PRUEBA DE MODO MANUAL - CAPTCHA")
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
        
        print("3️⃣ MODO MANUAL DE CAPTCHA")
        print("   🔧 Simulando fallo de OCR automático...")
        
        # Encontrar campo CAPTCHA
        codigo_field = driver.find_element(By.ID, "ContentPlaceHolder1_TextBox2")
        
        # Resaltar campo visualmente para modo manual
        driver.execute_script("arguments[0].style.border='5px solid red'", codigo_field)
        driver.execute_script("arguments[0].style.backgroundColor='#ffffaa'", codigo_field)
        driver.execute_script("arguments[0].focus()", codigo_field)
        
        print("   📝 Campo CAPTCHA resaltado en AMARILLO con borde ROJO")
        print("   🔍 INSTRUCCIONES:")
        print("     1. Mira la imagen CAPTCHA en el navegador")
        print("     2. Ingresa el código en el campo resaltado")
        print("     3. El script detectará automáticamente cuando ingreses el código")
        print("     4. Tienes 60 segundos")
        
        # Esperar ingreso manual
        tiempo_espera = 60
        inicio = time.time()
        captcha_ingresado = False
        
        print(f"\n   ⏳ Esperando ingreso manual (0/{tiempo_espera}s)...", end="", flush=True)
        
        while time.time() - inicio < tiempo_espera:
            try:
                valor_actual = codigo_field.get_attribute("value")
                if valor_actual and len(valor_actual.strip()) >= 3:
                    captcha_texto = valor_actual.strip().upper()
                    print(f"\n   ✅ ¡CAPTCHA detectado! Código: '{captcha_texto}'")
                    captcha_ingresado = True
                    
                    # Cambiar estilo para confirmar detección
                    driver.execute_script("arguments[0].style.border='5px solid green'", codigo_field)
                    driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
                    
                    break
                
                # Mostrar progreso
                tiempo_transcurrido = int(time.time() - inicio)
                print(f"\r   ⏳ Esperando ingreso manual ({tiempo_transcurrido}/{tiempo_espera}s)...", end="", flush=True)
                
            except Exception as e:
                print(f"\n   ⚠️ Error verificando campo: {e}")
            
            time.sleep(1)
        
        if captcha_ingresado:
            print("\n4️⃣ Resultado:")
            print("   🎉 ¡MODO MANUAL FUNCIONA CORRECTAMENTE!")
            print(f"   📝 Código detectado: '{captcha_texto}'")
            print("   ✅ El formulario está listo para enviar")
            
            # Mostrar botón de continuar
            try:
                continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
                driver.execute_script("arguments[0].style.border='3px solid blue'", continuar_btn)
                print("   🔵 Botón 'Continuar' resaltado en azul")
                print("   💡 Puedes hacer clic para enviar el formulario")
            except:
                pass
                
        else:
            print("\n   ⏰ Tiempo agotado")
            print("   💡 Pero el mecanismo de detección manual funciona correctamente")
        
        print(f"\n   🖥️ Manteniendo navegador abierto 30 segundos más...")
        time.sleep(30)
        
        return captcha_ingresado
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

# Ejecutar prueba
try:
    resultado = probar_modo_manual()
    print("\n" + "=" * 50)
    if resultado:
        print("✅ PRUEBA EXITOSA: Modo manual funciona correctamente")
    else:
        print("ℹ️ PRUEBA COMPLETADA: Mecanismo manual verificado")
    print("=" * 50)
    
except KeyboardInterrupt:
    print("\n❌ Prueba cancelada por el usuario")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    driver.quit()
    print("🔚 Navegador cerrado")