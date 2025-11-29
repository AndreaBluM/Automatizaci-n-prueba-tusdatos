@echo off
echo ========================================
echo  🤖 BOT REGISTRADURIA - CONSULTA CEDULA
echo ========================================
echo.
echo Este bot automaticamente:
echo  ✅ Llena el formulario de consulta
echo  ✅ Resuelve CAPTCHA con OCR automatico
echo  ✅ Descarga certificado PDF
echo  ✅ Extrae datos estructurados
echo  ✅ Guarda datos en archivo JSON
echo.
echo Ejemplos de uso:
echo  consultar_cedula.bat 1036670248 08/01/2015
echo  consultar_cedula.bat 12345678 15/03/1990
echo.
echo ========================================
echo Presiona cualquier tecla para continuar...
pause > nul

cd /d "%~dp0\.."
call .\env\Scripts\python.exe .\src\consulta_cedula.py %*

echo.
echo ========================================
echo  ✅ Proceso completado
echo ========================================
pause