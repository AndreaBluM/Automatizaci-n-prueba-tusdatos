# Configuración de ChromeDriver

Este proyecto incluye la configuración y uso de ChromeDriver para automatización web con Python.

## Requisitos Previos

1. **Google Chrome**: Debe estar instalado en tu sistema
2. **Python 3.7+**: Ya configurado en el entorno virtual
3. **Dependencias de Python**: Instaladas automáticamente

## Instalación

### Opción 1: Automática (Recomendada)
Los paquetes ya están instalados y configurados. ChromeDriver se descargará automáticamente al ejecutar el código.

### Opción 2: Manual
Si tienes problemas con la instalación automática:

1. Verifica tu versión de Chrome:
   - Abre Chrome
   - Ve a Configuración → Acerca de Chrome
   - Anota la versión (ej: 119.0.6045.105)

2. Descarga ChromeDriver manualmente:
   - Ve a: https://chromedriver.chromium.org/downloads
   - Descarga la versión que coincida con tu Chrome
   - Extrae el archivo `chromedriver.exe`
   - Colócalo en: `C:\chromedriver\chromedriver.exe`

## Uso

### Ejemplo Básico

```python
from src.chrome_driver_setup import ChromeDriverSetup

# Crear instancia
chrome_setup = ChromeDriverSetup(headless=False)

# Configurar driver
driver = chrome_setup.setup_driver()

# Usar el driver
driver.get("https://www.google.com")
print(driver.title)

# Cerrar
chrome_setup.close_driver()
```

### Ejecutar Pruebas

```bash
# Activar entorno virtual (si no está activado)
env\Scripts\activate

# Ejecutar prueba
python tests/test_chrome_driver.py
```

### Ejecutar Ejemplo

```bash
python src/chrome_driver_setup.py
```

## Configuraciones Disponibles

- **headless**: Ejecutar sin interfaz gráfica (True/False)
- **window_size**: Tamaño de ventana ("ancho,alto")
- **Opciones adicionales**: Ver código fuente para más opciones

## Solución de Problemas

### Error: "ChromeDriver no encontrado"
- Verifica que Chrome esté instalado
- Ejecuta: `chrome --version` en terminal
- Reinstala: `pip install selenium webdriver-manager --upgrade`

### Error: "Versiones incompatibles"
- Actualiza Chrome a la última versión
- Reinstala ChromeDriver: elimina cache y vuelve a ejecutar

### Error: "Puerto ya en uso"
- Cierra todas las instancias de Chrome
- Reinicia el script

## Estructura del Proyecto

```
├── src/
│   ├── __init__.py
│   └── chrome_driver_setup.py    # Configuración principal
├── tests/
│   └── test_chrome_driver.py     # Script de prueba
├── requirements.txt              # Dependencias
└── README.md                    # Esta documentación
```

## Recursos Adicionales

- [Documentación de Selenium](https://selenium-python.readthedocs.io/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)