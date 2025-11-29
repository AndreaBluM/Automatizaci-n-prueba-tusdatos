#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script de prueba para la funcionalidad JSON del bot"""

import sys
import os
import json
from datetime import datetime

# Simular datos de prueba como los que generaría el bot
datos_prueba = {
    "cedula": "1036670248",
    "nombre": "JUAN CARLOS RODRIGUEZ MARTINEZ",
    "estado": "VIGENTE",
    "fecha_expedicion": "08/01/2015",
    "lugar_expedicion": "BOGOTÁ D.C.",
    "fecha_consulta": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "vigente": True,
    "archivo_pdf": "certificado_1036670248_prueba.pdf",
    "texto_completo": "Texto completo del PDF de prueba..."
}

def probar_guardado_json():
    """Probar la funcionalidad de guardado JSON"""
    
    print("🧪 PROBANDO GUARDADO JSON")
    print("=" * 40)
    
    try:
        # Importar función del script principal
        sys.path.append(os.getcwd())
        from consulta_cedula import guardar_datos_json
        
        print("✅ Función importada correctamente")
        
        # Probar guardado
        archivo_generado = guardar_datos_json(datos_prueba, "1036670248")
        
        if archivo_generado and os.path.exists(archivo_generado):
            print(f"✅ Archivo JSON creado: {archivo_generado}")
            
            # Verificar contenido
            with open(archivo_generado, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
            
            print("✅ Archivo JSON válido")
            print("\n📊 ESTRUCTURA DEL JSON:")
            print("-" * 30)
            
            # Mostrar metadatos
            if "metadatos" in datos_cargados:
                print("📋 METADATOS:")
                for clave, valor in datos_cargados["metadatos"].items():
                    print(f"  • {clave}: {valor}")
            
            # Mostrar datos ciudadano
            if "datos_ciudadano" in datos_cargados:
                print("\n👤 DATOS CIUDADANO:")
                for clave, valor in datos_cargados["datos_ciudadano"].items():
                    if clave != "texto_completo":  # No mostrar texto completo
                        print(f"  • {clave}: {valor}")
            
            print(f"\n📄 Tamaño del archivo: {os.path.getsize(archivo_generado)} bytes")
            print("=" * 40)
            print("🎉 ¡PRUEBA EXITOSA!")
            
            return True
        else:
            print("❌ Error: Archivo no se creó")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    probar_guardado_json()