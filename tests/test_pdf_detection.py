"""
Prueba específica para la búsqueda del PDF del certificado
Este script se enfoca solo en probar la lógica de detección del PDF correcto
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def buscar_pdf_generado(driver, ventanas_originales):
    """Buscar ESPECÍFICAMENTE el PDF generado al hacer clic en 'Generar Certificado'"""
    
    try:
        print("   🔍 Buscando PDF del certificado generado...")
        
        # Método 1: Verificar si se abrió nueva ventana con PDF
        ventanas_actuales = driver.window_handles
        if len(ventanas_actuales) > ventanas_originales:
            print(f"   📄 Se abrieron {len(ventanas_actuales) - ventanas_originales} nuevas ventanas")
            
            # Cambiar a cada nueva ventana y verificar si es PDF
            for i, ventana in enumerate(ventanas_actuales[ventanas_originales:], 1):
                try:
                    driver.switch_to.window(ventana)
                    url_nueva = driver.current_url
                    titulo_nueva = driver.title
                    
                    print(f"   📄 Nueva ventana {i}: {url_nueva}")
                    print(f"   📄 Título: {titulo_nueva}")
                    
                    # Verificar si es PDF
                    if (".pdf" in url_nueva.lower() or 
                        "application/pdf" in driver.page_source.lower()[:500] or
                        "certificado" in url_nueva.lower()):
                        print("   ✅ PDF del certificado encontrado en nueva ventana")
                        return url_nueva
                except Exception as e:
                    print(f"   ⚠️ Error verificando ventana {i}: {e}")
                    continue
            
            # Volver a la ventana original
            driver.switch_to.window(ventanas_actuales[0])
        
        # Método 2: Buscar iframe que se haya creado/actualizado
        print("   🔎 Buscando iframe con PDF del certificado...")
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"   📊 Encontrados {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute("src")
                if src:
                    print(f"   📄 iframe {i+1}: {src}")
                    # Solo PDFs que contengan "certificado" o sean generados recientemente
                    if (".pdf" in src.lower() and 
                        ("certificado" in src.lower() or "cert" in src.lower())):
                        print("   ✅ PDF del certificado encontrado en iframe")
                        return src
        except Exception as e:
            print(f"   ❌ Error buscando iframes: {e}")
        
        # Método 3: Buscar en la URL actual si cambió a PDF
        url_actual = driver.current_url
        if ".pdf" in url_actual.lower():
            print("   ✅ URL actual es PDF del certificado")
            return url_actual
        
        # Método 4: Buscar enlaces que se hayan actualizado
        print("   🔎 Buscando enlaces de descarga del certificado...")
        try:
            enlaces_certificado = driver.find_elements(By.XPATH, 
                "//a[contains(@href, '.pdf') and (contains(text(), 'certificado') or contains(@href, 'certificado'))]")
            
            if enlaces_certificado:
                href = enlaces_certificado[0].get_attribute("href")
                texto = enlaces_certificado[0].text
                print(f"   ✅ Enlace de certificado encontrado: '{texto}' -> {href}")
                return href
        except Exception as e:
            print(f"   ❌ Error buscando enlaces: {e}")
        
        # Método 5: Buscar cualquier PDF nuevo (último recurso)
        print("   🔎 Buscando cualquier PDF como último recurso...")
        try:
            # Buscar todos los enlaces PDF
            enlaces_pdf = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            if enlaces_pdf:
                for i, enlace in enumerate(enlaces_pdf):
                    href = enlace.get_attribute("href")
                    texto = enlace.text.strip()
                    print(f"   📄 PDF {i+1}: '{texto}' -> {href}")
                
                # Retornar el primero como fallback
                if enlaces_pdf:
                    href = enlaces_pdf[0].get_attribute("href")
                    print(f"   ⚠️ Usando primer PDF encontrado como fallback: {href}")
                    return href
        except Exception as e:
            print(f"   ❌ Error en búsqueda de fallback: {e}")
        
        print("   ❌ No se encontró PDF del certificado generado")
        return None
        
    except Exception as e:
        print(f"   ❌ Error buscando PDF generado: {e}")
        return None

def probar_busqueda_pdf():
    """Función de prueba para la detección de PDFs"""
    
    print("🧪 PRUEBA DE DETECCIÓN DE PDF")
    print("=" * 50)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Inicializar driver
    print("🔧 Inicializando Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Ir a la página de prueba
        print("📄 Navegando a Registraduría...")
        driver.get("https://wsp.registraduria.gov.co/ProyectoSCCContratacion/ConsultarEstadoCiudadano.aspx")
        time.sleep(3)
        
        print(f"📊 URL actual: {driver.current_url}")
        print(f"📊 Título: {driver.title}")
        print(f"📊 Ventanas iniciales: {len(driver.window_handles)}")
        
        # Buscar botones disponibles en la página
        print("\n🔍 Analizando botones disponibles...")
        try:
            botones = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button")
            print(f"📊 Botones encontrados: {len(botones)}")
            
            for i, boton in enumerate(botones):
                value = boton.get_attribute("value") or ""
                texto = boton.text.strip()
                tipo = boton.get_attribute("type") or ""
                name = boton.get_attribute("name") or ""
                print(f"   🔘 Botón {i+1}: value='{value}', texto='{texto}', tipo='{tipo}', name='{name}'")
                
        except Exception as e:
            print(f"❌ Error analizando botones: {e}")
        
        # Buscar PDFs existentes
        print("\n🔍 Buscando PDFs existentes...")
        try:
            ventanas_iniciales = len(driver.window_handles)
            pdf_inicial = buscar_pdf_generado(driver, ventanas_iniciales)
            
            if pdf_inicial:
                print(f"✅ PDF encontrado: {pdf_inicial}")
            else:
                print("❌ No se encontraron PDFs")
                
        except Exception as e:
            print(f"❌ Error buscando PDFs: {e}")
        
        print("\n⏳ Manteniendo navegador abierto por 10 segundos...")
        time.sleep(10)
        
    finally:
        print("🔧 Cerrando navegador...")
        driver.quit()
        print("✅ Prueba completada")

if __name__ == "__main__":
    probar_busqueda_pdf()