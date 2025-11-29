"""
Script para consulta de cédula con CAPTCHA MANUAL FORZADO
Uso: python consulta_cedula_manual.py <cedula> <fecha_dd/mm/yyyy>
Ejemplo: python consulta_cedula_manual.py 1036670248 08/01/2015
"""

# Importar todo del script principal
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Importar funciones específicas del script principal
try:
    from consulta_cedula import (
        pedir_captcha_manual, 
        procesar_certificado_pdf, 
        mostrar_resultados_certificado, 
        guardar_datos_json
    )
except ImportError:
    print("❌ Error: No se pueden importar las funciones necesarias")
    sys.exit(1)

def configurar_chrome():
    """Configurar ChromeDriver con opciones optimizadas"""
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def resolver_captcha_manual_forzado(driver):
    """Forzar SIEMPRE el modo manual, sin intentar OCR"""
    print("4️⃣ Resolviendo CAPTCHA (MODO MANUAL FORZADO)...")
    print("   🔧 Saltando OCR automático - Modo manual directo")
    
    # Directamente activar modo manual sin intentar OCR
    captcha_texto = pedir_captcha_manual(driver)
    
    if not captcha_texto:
        print("   ❌ No se pudo obtener CAPTCHA manualmente")
        return ""
    
    return captcha_texto

def consultar_cedula_manual(cedula, fecha):
    """Función principal con CAPTCHA manual forzado"""
    
    print("🚀 Iniciando bot con CAPTCHA MANUAL FORZADO...")
    print(f"📋 Cédula: {cedula}")
    print(f"📅 Fecha: {fecha}")
    print("=" * 50)
    
    try:
        # 1. Configurar Chrome
        print("1️⃣ Configurando ChromeDriver...")
        driver = configurar_chrome()
        wait = WebDriverWait(driver, 20)
        
        # 2. Navegar
        print("2️⃣ Navegando a la página...")
        driver.get("https://wsp.registraduria.gov.co/censo/consultar/")
        time.sleep(3)
        
        print("   ✅ Página cargada correctamente")
        
        # 3. Llenar cédula
        print(f"3️⃣ Llenando cédula: {cedula}")
        cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
        cedula_field.clear()
        cedula_field.send_keys(cedula)
        
        # Resaltar campo
        driver.execute_script("arguments[0].style.backgroundColor='#ffffaa'", cedula_field)
        driver.execute_script("arguments[0].style.border='3px solid orange'", cedula_field)
        print("   ✅ Cédula ingresada")
        
        # 4. Llenar fecha (usando la función del script original)
        partes_fecha = fecha.split('/')
        dia, mes, año = partes_fecha[0], partes_fecha[1], partes_fecha[2]
        
        print(f"4️⃣ Llenando fecha: {fecha}")
        
        # Día
        dia_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
        dia_dropdown.select_by_visible_text(dia)
        
        # Mes
        mes_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
        mes_dropdown.select_by_visible_text(mes)
        
        # Año
        año_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
        año_dropdown.select_by_visible_text(año)
        
        print("   ✅ Fecha ingresada")
        
        # 5. Resolver CAPTCHA (MANUAL FORZADO)
        captcha_texto = resolver_captcha_manual_forzado(driver)
        
        if not captcha_texto:
            print("   ❌ No se pudo obtener CAPTCHA")
            return False
        
        # 6. Llenar campo CAPTCHA
        print("5️⃣ Completando formulario...")
        codigo_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox2")))
        codigo_field.clear()
        codigo_field.send_keys(captcha_texto)
        
        # Confirmar visualmente
        driver.execute_script("arguments[0].style.backgroundColor='#aaffaa'", codigo_field)
        driver.execute_script("arguments[0].style.border='3px solid green'", codigo_field)
        
        # 7. Enviar formulario
        print("6️⃣ Enviando consulta...")
        continuar_btn = driver.find_element(By.ID, "ContentPlaceHolder1_Button1")
        driver.execute_script("arguments[0].scrollIntoView();", continuar_btn)
        time.sleep(1)
        
        try:
            continuar_btn.click()
        except:
            driver.execute_script("arguments[0].click();", continuar_btn)
        
        # 8. Esperar respuesta
        time.sleep(5)
        
        print("\n" + "=" * 50)
        print("✅ CONSULTA PROCESADA")
        print("=" * 50)
        print(f"📄 URL actual: {driver.current_url}")
        print(f"📝 Título: {driver.title}")
        
        # Verificar resultados y procesar PDF
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
            print("💡 Puede que el CAPTCHA haya sido incorrecto.")
            print(f"\n🖥️ Navegador permanecerá abierto 60 segundos...")
            time.sleep(60)
            return False
        
    except Exception as e:
        print(f"❌ Error durante la consulta: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Uso correcto:")
        print("   python consulta_cedula_manual.py <cedula> <fecha_dd/mm/yyyy>")
        print("   Ejemplo: python consulta_cedula_manual.py 1036670248 08/01/2015")
        sys.exit(1)
    
    cedula = sys.argv[1]
    fecha = sys.argv[2]
    
    # Validaciones básicas
    if not cedula.isdigit() or len(cedula) < 6:
        print("❌ Cédula debe ser solo números y tener al menos 6 dígitos")
        sys.exit(1)
    
    # Validar formato de fecha
    try:
        partes = fecha.split('/')
        if len(partes) != 3:
            raise ValueError("Formato incorrecto")
        dia, mes, año = map(int, partes)
        if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1900 <= año <= 2025):
            raise ValueError("Fecha fuera de rango")
    except:
        print("❌ Fecha debe estar en formato DD/MM/YYYY")
        print("   Ejemplo: 08/01/2015")
        sys.exit(1)
    
    # Ejecutar consulta
    resultado = consultar_cedula_manual(cedula, fecha)
    
    if resultado:
        print("\n🎉 ¡Consulta completada exitosamente!")
    else:
        print("\n❌ La consulta no pudo completarse.")
        sys.exit(1)