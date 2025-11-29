from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def solicitar_datos():
    """
    Función para solicitar datos al usuario de forma interactiva
    """
    print("=" * 60)
    print("🏛️  FORMULARIO REGISTRADURÍA - CONSULTA DE CÉDULA")
    print("=" * 60)
    
    # Solicitar número de cédula
    while True:
        cedula = input("📝 Ingresa el número de cédula (10 dígitos): ").strip()
        if cedula.isdigit() and len(cedula) == 10:
            break
        print("❌ Error: Debe ser un número de 10 dígitos")
    
    # Solicitar día
    while True:
        dia = input("📅 Día de expedición (1-31): ").strip()
        try:
            dia_num = int(dia)
            if 1 <= dia_num <= 31:
                break
            else:
                print("❌ Error: Día debe estar entre 1 y 31")
        except ValueError:
            print("❌ Error: Ingresa un número válido")
    
    # Solicitar mes
    while True:
        mes = input("📅 Mes de expedición (1-12 o nombre): ").strip()
        meses_nombres = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        if mes.isdigit() and 1 <= int(mes) <= 12:
            break
        elif mes.lower() in meses_nombres:
            break
        else:
            print("❌ Error: Ingresa un número (1-12) o nombre del mes")
    
    # Solicitar año
    while True:
        año = input("📅 Año de expedición (ej: 2020): ").strip()
        try:
            año_num = int(año)
            if 1950 <= año_num <= 2025:
                break
            else:
                print("❌ Error: Año debe estar entre 1950 y 2025")
        except ValueError:
            print("❌ Error: Ingresa un año válido")
    
    print("\n✅ Datos ingresados correctamente")
    return cedula, dia, mes, año

def ejecutar_formulario_interactivo():
    """
    Función principal para ejecutar el formulario de forma interactiva
    """
    # Solicitar datos
    cedula, dia, mes, año = solicitar_datos()
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service("C:\\chromedriver\\chromedriver.exe")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("\n🌐 Abriendo página de la Registraduría...")
        driver.get("https://certvigenciacedula.registraduria.gov.co/Datos.aspx")
        
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        print(f"✅ Página cargada: {driver.title}")
        
        # Llenar cédula
        print(f"\n1️⃣ Ingresando cédula: {cedula}")
        cedula_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_TextBox1")))
        cedula_field.clear()
        cedula_field.send_keys(cedula)
        
        # Seleccionar día
        print(f"2️⃣ Seleccionando día: {dia}")
        dia_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList1"))))
        dia_formato = f"{int(dia):02d}"
        dia_dropdown.select_by_value(dia_formato)
        
        # Seleccionar mes
        print(f"3️⃣ Seleccionando mes: {mes}")
        mes_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList2"))))
        
        meses = {
            "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
            "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
            "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
            "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
            "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
            "09": "Septiembre"
        }
        
        if mes.isdigit():
            mes_nombre = meses.get(mes, mes)
        else:
            mes_nombre = mes.capitalize()
        
        mes_dropdown.select_by_visible_text(mes_nombre)
        
        # Seleccionar año
        print(f"4️⃣ Seleccionando año: {año}")
        año_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_DropDownList3"))))
        año_dropdown.select_by_visible_text(str(año))
        
        print("\n" + "="*60)
        print("✅ FORMULARIO COMPLETADO")
        print("="*60)
        print("📝 Datos ingresados:")
        print(f"   • Cédula: {cedula}")
        print(f"   • Fecha: {dia}/{mes}/{año}")
        print("\n🔍 SIGUIENTE PASO:")
        print("1. Observa la imagen CAPTCHA en el navegador")
        print("2. Ingresa el código en el campo correspondiente")
        print("3. Haz clic en 'Continuar'")
        print("="*60)
        
        # Resaltar campo CAPTCHA
        try:
            codigo_field = driver.find_element(By.ID, "ContentPlaceHolder1_TextBox2")
            driver.execute_script("arguments[0].style.border='3px solid red'", codigo_field)
            driver.execute_script("arguments[0].focus()", codigo_field)
            print("🎯 Campo CAPTCHA resaltado en rojo y enfocado")
        except:
            pass
        
        # Esperar para completar CAPTCHA manualmente
        print(f"\n⏰ Tienes 3 minutos para completar el CAPTCHA y enviar el formulario...")
        time.sleep(180)  # 3 minutos
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()
        print("\n🔚 Sesión finalizada.")

# Ejecutar script interactivo
if __name__ == "__main__":
    try:
        ejecutar_formulario_interactivo()
    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")