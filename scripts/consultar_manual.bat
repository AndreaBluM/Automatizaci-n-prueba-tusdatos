@echo off
echo ========================================
echo  🤖 BOT REGISTRADURIA - MODO MANUAL
echo ========================================
echo.
echo Este modo SIEMPRE pregunta el CAPTCHA manualmente
echo (sin intentar OCR automatico)
echo.
echo Uso: consultar_manual.bat cedula fecha
echo Ejemplo: consultar_manual.bat 1036670248 08/01/2015
echo.
echo ========================================

if "%~2"=="" (
    echo Error: Faltan parametros
    echo Uso: consultar_manual.bat ^<cedula^> ^<fecha^>
    echo Ejemplo: consultar_manual.bat 1036670248 08/01/2015
    pause
    exit /b 1
)

cd /d "%~dp0"
call .\env\Scripts\python.exe consulta_cedula_manual.py %*

echo.
echo ========================================
echo  ✅ Proceso completado
echo ========================================
pause