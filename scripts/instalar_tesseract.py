"""
Script para descargar e instalar Tesseract OCR en Windows
"""

import os
import requests
import subprocess
import sys
from pathlib import Path

def descargar_tesseract():
    """
    Descarga e instala Tesseract OCR para Windows
    """
    print("🔧 INSTALADOR DE TESSERACT OCR")
    print("=" * 40)
    
    # Verificar si ya está instalado
    rutas_comunes = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    
    for ruta in rutas_comunes:
        if os.path.exists(ruta):
            print(f"✅ Tesseract ya está instalado en: {ruta}")
            return ruta
    
    print("📥 Tesseract no encontrado. Procediendo con la descarga...")
    
    # URL del instalador más reciente (actualizar según necesidad)
    url_instalador = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    nombre_archivo = "tesseract-installer.exe"
    
    try:
        print("🌐 Descargando Tesseract...")
        response = requests.get(url_instalador, timeout=30)
        response.raise_for_status()
        
        # Guardar archivo
        with open(nombre_archivo, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Descarga completada: {nombre_archivo}")
        
        # Ejecutar instalador
        print("🚀 Ejecutando instalador...")
        print("⚠️ Sigue las instrucciones del instalador")
        print("💡 Recomendado: instalar en la ruta predeterminada")
        
        subprocess.run([nombre_archivo], check=True)
        
        # Verificar instalación
        for ruta in rutas_comunes:
            if os.path.exists(ruta):
                print(f"✅ Tesseract instalado exitosamente en: {ruta}")
                
                # Limpiar archivo de instalación
                try:
                    os.remove(nombre_archivo)
                    print("🧹 Archivo de instalación eliminado")
                except:
                    pass
                
                return ruta
        
        print("⚠️ Instalación completada pero no se puede verificar la ubicación")
        return None
        
    except requests.RequestException as e:
        print(f"❌ Error descargando: {e}")
        print("📋 INSTALACIÓN MANUAL:")
        print("1. Ve a: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Descarga el instalador para Windows")
        print("3. Ejecuta el instalador")
        print("4. Reinicia este script")
        return None
        
    except subprocess.CalledProcessError:
        print("❌ Error ejecutando el instalador")
        return None
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def configurar_tesseract_python():
    """
    Configura la ruta de Tesseract en el script de Python
    """
    print("\n🔧 Configurando pytesseract...")
    
    # Buscar Tesseract instalado
    rutas_buscar = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    
    tesseract_path = None
    for ruta in rutas_buscar:
        if os.path.exists(ruta):
            tesseract_path = ruta
            break
    
    if tesseract_path:
        print(f"✅ Tesseract encontrado en: {tesseract_path}")
        
        # Actualizar el script principal
        script_path = "registraduria_script.py"
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Buscar y actualizar la línea de configuración
                linea_config = f"pytesseract.pytesseract.tesseract_cmd = r'{tesseract_path}'"
                
                if "pytesseract.pytesseract.tesseract_cmd" in contenido:
                    # Reemplazar línea existente
                    import re
                    contenido = re.sub(
                        r'# pytesseract\.pytesseract\.tesseract_cmd.*',
                        linea_config,
                        contenido
                    )
                    contenido = re.sub(
                        r'pytesseract\.pytesseract\.tesseract_cmd.*',
                        linea_config,
                        contenido
                    )
                else:
                    # Agregar línea después del import
                    contenido = contenido.replace(
                        "import pytesseract",
                        f"import pytesseract\n{linea_config}"
                    )
                
                # Guardar archivo actualizado
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                print(f"✅ Script actualizado con la ruta de Tesseract")
                
            except Exception as e:
                print(f"⚠️ Error actualizando script: {e}")
                print(f"🔧 Agrega manualmente esta línea al script:")
                print(f"   {linea_config}")
        
        return tesseract_path
    else:
        print("❌ No se encontró Tesseract instalado")
        return None

def probar_tesseract():
    """
    Prueba que Tesseract funcione correctamente
    """
    print("\n🧪 Probando Tesseract...")
    
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen de prueba
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "PRUEBA123", fill='black')
        
        # Extraer texto
        texto = pytesseract.image_to_string(img).strip()
        
        if "PRUEBA" in texto or "123" in texto:
            print("✅ Tesseract funciona correctamente")
            print(f"📝 Texto extraído: '{texto}'")
            return True
        else:
            print(f"⚠️ Tesseract funciona pero con baja precisión: '{texto}'")
            return False
            
    except ImportError:
        print("❌ pytesseract no está instalado")
        print("💡 Ejecuta: pip install pytesseract Pillow")
        return False
        
    except Exception as e:
        print(f"❌ Error probando Tesseract: {e}")
        return False

def main():
    """Función principal"""
    print("🤖 CONFIGURADOR DE TESSERACT PARA CAPTCHA OCR")
    print("=" * 50)
    
    # Paso 1: Descargar/instalar Tesseract
    tesseract_path = descargar_tesseract()
    
    # Paso 2: Configurar en Python
    if not tesseract_path:
        tesseract_path = configurar_tesseract_python()
    else:
        configurar_tesseract_python()
    
    # Paso 3: Probar funcionamiento
    if tesseract_path:
        funciona = probar_tesseract()
        
        if funciona:
            print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("🚀 Ahora puedes usar el script con resolución automática de CAPTCHA")
        else:
            print("\n⚠️ Configuración completada con advertencias")
            print("💡 El OCR puede necesitar ajustes para mejor precisión")
    else:
        print("\n❌ No se pudo completar la configuración")
        print("📋 Sigue las instrucciones de instalación manual")

if __name__ == "__main__":
    main()