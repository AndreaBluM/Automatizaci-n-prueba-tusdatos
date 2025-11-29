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

def inspeccionar_elementos():
    """
    Función para inspeccionar y mostrar información de los elementos del formulario
    """
    try:
        print("🔍 Inspeccionando elementos de la página...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        print("\n📋 ANÁLISIS DE ELEMENTOS DEL FORMULARIO:")
        print("=" * 50)
        
        # Buscar todos los inputs de texto
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n🔸 INPUTS ENCONTRADOS ({len(inputs)}):")
        for i, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type") or "no-type"
                input_id = input_elem.get_attribute("id") or "no-id"
                input_name = input_elem.get_attribute("name") or "no-name"
                input_placeholder = input_elem.get_attribute("placeholder") or "no-placeholder"
                input_class = input_elem.get_attribute("class") or "no-class"
                
                print(f"  Input {i+1}:")
                print(f"    Type: {input_type}")
                print(f"    ID: {input_id}")
                print(f"    Name: {input_name}")
                print(f"    Placeholder: {input_placeholder}")
                print(f"    Class: {input_class}")
                print("    ---")
            except Exception as e:
                print(f"    Error inspeccionando input {i+1}: {e}")
        
        # Buscar todos los selects (dropdowns)
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"\n🔸 SELECTS ENCONTRADOS ({len(selects)}):")
        for i, select_elem in enumerate(selects):
            try:
                select_id = select_elem.get_attribute("id") or "no-id"
                select_name = select_elem.get_attribute("name") or "no-name"
                select_class = select_elem.get_attribute("class") or "no-class"
                
                # Obtener opciones
                options = select_elem.find_elements(By.TAG_NAME, "option")
                option_texts = [opt.text for opt in options[:5]]  # Primeras 5 opciones
                
                print(f"  Select {i+1}:")
                print(f"    ID: {select_id}")
                print(f"    Name: {select_name}")
                print(f"    Class: {select_class}")
                print(f"    Primeras opciones: {option_texts}")
                print("    ---")
            except Exception as e:
                print(f"    Error inspeccionando select {i+1}: {e}")
        
        # Buscar botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        inputs_submit = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], input[type='button']")
        all_buttons = buttons + inputs_submit
        
        print(f"\n🔸 BOTONES ENCONTRADOS ({len(all_buttons)}):")
        for i, button_elem in enumerate(all_buttons):
            try:
                button_text = button_elem.text or button_elem.get_attribute("value") or "no-text"
                button_id = button_elem.get_attribute("id") or "no-id"
                button_name = button_elem.get_attribute("name") or "no-name"
                button_class = button_elem.get_attribute("class") or "no-class"
                
                print(f"  Button {i+1}:")
                print(f"    Text/Value: {button_text}")
                print(f"    ID: {button_id}")
                print(f"    Name: {button_name}")
                print(f"    Class: {button_class}")
                print("    ---")
            except Exception as e:
                print(f"    Error inspeccionando button {i+1}: {e}")
        
        # Buscar imagen del captcha
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"\n🔸 IMÁGENES ENCONTRADAS ({len(images)}):")
        for i, img_elem in enumerate(images):
            try:
                img_src = img_elem.get_attribute("src") or "no-src"
                img_alt = img_elem.get_attribute("alt") or "no-alt"
                img_id = img_elem.get_attribute("id") or "no-id"
                
                print(f"  Imagen {i+1}:")
                print(f"    Src: {img_src}")
                print(f"    Alt: {img_alt}")
                print(f"    ID: {img_id}")
                print("    ---")
            except Exception as e:
                print(f"    Error inspeccionando imagen {i+1}: {e}")
        
        print("\n✅ Inspección completada. Navegador permanecerá abierto por 30 segundos.")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error durante inspección: {e}")

# Ejecutar inspección
try:
    inspeccionar_elementos()
except Exception as e:
    print(f"Error general: {e}")
finally:
    driver.quit()
    print("🔚 Navegador cerrado.")