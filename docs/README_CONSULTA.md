# 🤖 Bot Automático - Consulta de Cédula Registraduría

Bot completamente automatizado para consultar el estado de cédulas en la Registraduría Nacional de Colombia.

## 🚀 Uso Rápido

### Opción 1: Script Python
```bash
python consulta_cedula.py <cedula> <fecha_dd/mm/yyyy>
```

### Opción 2: Archivo Batch (Windows)
```cmd
consultar.bat <cedula> <fecha_dd/mm/yyyy>
```

## 📋 Ejemplos

```bash
# Con datos reales de ejemplo
python consulta_cedula.py 1036670248 08/01/2015

# Otro ejemplo
python consulta_cedula.py 1234567890 15/06/2020
```

```cmd
# Con archivo batch
consultar.bat 1036670248 08/01/2015
consultar.bat 1234567890 15/06/2020
```

## 🎯 Características

- ✅ **Completamente automático** - Solo necesitas ejecutar el comando
- 🤖 **OCR inteligente** - Resuelve CAPTCHA automáticamente en la mayoría de casos
- 💬 **Fallback por consola** - Si OCR falla, pregunta por consola
- 📊 **Validación de datos** - Verifica que cédula y fecha sean correctos
- 🔍 **Resultados claros** - Muestra el estado de la consulta
- 🖥️ **Navegador visible** - Puedes ver el proceso y los resultados

## 📝 Formato de Datos

### Cédula
- **Longitud:** Exactamente 10 dígitos
- **Ejemplo:** `1036670248`

### Fecha de Expedición
- **Formato:** DD/MM/YYYY
- **Ejemplos:** `08/01/2015`, `15/06/2020`

## 🔄 Flujo de Ejecución

1. **Validación** - Verifica que los datos sean correctos
2. **Apertura** - Abre la página de la Registraduría
3. **Formulario** - Llena automáticamente cédula y fecha
4. **CAPTCHA** - Intenta resolver automáticamente con OCR
5. **Manual** - Si OCR falla, pregunta por consola
6. **Envío** - Envía el formulario automáticamente
7. **Resultados** - Muestra los resultados en el navegador

## ⚡ Instalación y Configuración

El bot ya está completamente configurado con:
- ✅ ChromeDriver instalado
- ✅ Tesseract OCR configurado
- ✅ Todas las dependencias instaladas

## 🛠️ Archivos del Proyecto

- `consulta_cedula.py` - Script principal ejecutable
- `consultar.bat` - Archivo batch para Windows
- `registraduria_script.py` - Script base con datos predefinidos
- `bot_registraduria_completo.py` - Bot avanzado con clase
- Otros archivos de soporte y pruebas

## 💡 Consejos de Uso

- **Datos reales**: Usa siempre cédula y fecha de expedición reales
- **Conexión**: Asegúrate de tener conexión a internet estable
- **Paciencia**: El proceso toma 20-60 segundos dependiendo del CAPTCHA
- **CAPTCHA manual**: Si el OCR falla, simplemente mira la imagen y escribe lo que ves

## 🎉 ¡Listo para Usar!

El bot está completamente funcional. Solo ejecuta el comando con los datos reales y déjalo trabajar.

```bash
python consulta_cedula.py 1036670248 08/01/2015
```