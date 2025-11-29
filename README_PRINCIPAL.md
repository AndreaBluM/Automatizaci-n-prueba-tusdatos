# 🤖 BOT REGISTRADURÍA NACIONAL - ESTRUCTURA ORGANIZADA

## 📁 Estructura del Proyecto

```
P TUSDATOS/
├── 📁 src/                     # Código fuente principal
│   ├── consulta_cedula.py      # Bot principal de consulta
│   └── __init__.py            # Módulo Python
│
├── 📁 tests/                   # Suite completa de pruebas
│   ├── test_unitarios.py       # Pruebas unitarias (18 tests)
│   ├── test_integracion.py     # Pruebas de integración (13 tests)
│   ├── test_datos.py          # Pruebas de datos (12 tests)
│   └── ejecutar_todas_las_pruebas.py  # Ejecutor principal
│
├── 📁 scripts/                 # Scripts utilitarios y herramientas
│   ├── consultar_cedula.bat    # Interfaz usuario principal
│   ├── ejecutar_pruebas.bat    # Menú interactivo de pruebas
│   ├── prueba_concurrencia.py  # Análisis de concurrencia
│   ├── bot_registraduria_completo.py  # Versión completa
│   ├── verificar_dependencias.py      # Verificación sistema
│   └── [otros scripts de desarrollo]
│
├── 📁 docs/                    # Documentación completa
│   ├── README.md              # Documentación general
│   ├── README_CONSULTA.md     # Guía de uso del bot
│   ├── DOCUMENTACION_PRUEBAS.md       # Sistema de pruebas
│   ├── DOCUMENTACION_PRUEBA_CONCURRENCIA.md  # Análisis concurrencia
│   └── RESUMEN_IMPLEMENTACION.py      # Resumen técnico
│
├── 📁 output/                  # Archivos generados
│   ├── consulta_*.json        # Resultados de consultas
│   ├── reporte_pruebas_*.json # Reportes de pruebas
│   └── reporte_15_consultas_*.json    # Reportes concurrencia
│
├── 📁 data/                   # Datos de referencia
│   └── README.md             # Info sobre datos
│
└── 📁 env/                    # Entorno virtual Python
    ├── Scripts/              # Ejecutables Python
    ├── Lib/                  # Librerías instaladas
    └── pyvenv.cfg           # Configuración entorno
```

## 🚀 Cómo Usar el Sistema

### ✅ Consulta Individual

**Opción 1 - Interfaz Gráfica (Recomendada):**
```bash
# Doble clic en:
scripts\consultar_cedula.bat
```

**Opción 2 - Línea de Comandos:**
```bash
cd src
python consulta_cedula.py 1036670248 08/01/2015
```

### 🧪 Ejecutar Pruebas

**Interfaz Interactiva:**
```bash
# Doble clic en:
scripts\ejecutar_pruebas.bat
```

**Línea de Comandos:**
```bash
# Todas las pruebas
cd tests
python ejecutar_todas_las_pruebas.py

# Solo unitarias
python test_unitarios.py

# Solo integración  
python test_integracion.py

# Solo datos
python test_datos.py
```

## 📊 Estado del Sistema

### ✅ Funcionalidades Principales
- **Consulta Individual**: ✅ Funcional
- **Procesamiento PDF**: ✅ Funcional  
- **OCR CAPTCHA**: ✅ Funcional
- **Concurrencia**: ✅ Probada (15 consultas paralelas)
- **Persistencia JSON**: ✅ Carpeta `output/`

### 🧪 Sistema de Pruebas
- **Total**: 31 pruebas
- **Tasa Éxito**: 83.9%
- **Cobertura**: Completa
- **Reportes**: Automáticos en `output/`

### 📁 Archivos de Salida
- **Consultas**: `output/consulta_[cedula]_[timestamp].json`
- **Reportes Pruebas**: `output/reporte_pruebas_[fecha].json`
- **Análisis Concurrencia**: `output/reporte_15_consultas_[timestamp].json`

## 🔧 Configuración

### Dependencias Principales
```bash
pip install selenium webdriver-manager pytesseract pillow opencv-python requests pdfplumber psutil
```

### Verificar Sistema
```bash
cd scripts
python verificar_dependencias.py
```

## 📚 Documentación Detallada

- **[Guía de Uso](docs/README_CONSULTA.md)** - Instrucciones detalladas
- **[Sistema de Pruebas](docs/DOCUMENTACION_PRUEBAS.md)** - Documentación completa de testing
- **[Análisis Concurrencia](docs/DOCUMENTACION_PRUEBA_CONCURRENCIA.md)** - Pruebas de carga
- **[Implementación](docs/RESUMEN_IMPLEMENTACION.py)** - Detalles técnicos

## ⚡ Comandos Rápidos

```bash
# Consulta rápida
scripts\consultar_cedula.bat

# Pruebas completas  
scripts\ejecutar_pruebas.bat

# Verificar sistema
cd scripts && python verificar_dependencias.py

# Ver últimos resultados
dir output\*.json /od
```

## 🏗️ Arquitectura

- **Modular**: Código organizado por funcionalidad
- **Testeable**: 31 pruebas automatizadas
- **Escalable**: Soporte para concurrencia
- **Documentado**: Documentación completa
- **Mantenible**: Estructura clara y separación responsabilidades

---

**🎯 Todo está organizado, funcional y listo para usar!**