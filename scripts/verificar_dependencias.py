#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script para verificar dependencias antes de usar el bot"""

import sys

def verificar_dependencias():
    """Verificar que todos los módulos necesarios estén instalados"""
    
    modulos = [
        ('selenium', 'WebDriver de Selenium'),
        ('webdriver_manager', 'Gestor de ChromeDriver'),
        ('PIL', 'Procesamiento de imágenes'),
        ('cv2', 'OpenCV para vision computacional'),
        ('pytesseract', 'OCR con Tesseract'),
        ('requests', 'Descarga de archivos'),
        ('pdfplumber', 'Procesamiento de PDF')
    ]
    
    print("Verificando dependencias...")
    print("-" * 40)
    
    todo_ok = True
    
    for modulo, descripcion in modulos:
        try:
            __import__(modulo)
            print(f"OK  - {descripcion}")
        except ImportError as e:
            print(f"ERROR - {descripcion}: {e}")
            todo_ok = False
    
    print("-" * 40)
    
    if todo_ok:
        print("Todas las dependencias están disponibles!")
        return True
    else:
        print("Faltan algunas dependencias. Instálalas con pip.")
        return False

if __name__ == "__main__":
    verificar_dependencias()