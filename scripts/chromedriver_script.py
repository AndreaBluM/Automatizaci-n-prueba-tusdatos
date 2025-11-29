from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Opción 1: Usar webdriver-manager (automático)
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    print("✓ Usando ChromeDriver automático")
except Exception as e:
    print(f"Error con webdriver-manager: {e}")
    # Opción 2: Usar ChromeDriver manual (fallback)
    service = Service("C:\\chromedriver\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    print("✓ Usando ChromeDriver manual")

driver.get("https://google.com")
print(f"✓ Navegando a Google - Título: {driver.title}")

# Mantener el navegador abierto por unos segundos
import time
time.sleep(5)

# Cerrar el navegador
driver.quit()
print("✓ Navegador cerrado")