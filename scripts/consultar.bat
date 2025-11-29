@echo off
echo ========================================
echo    CONSULTA CEDULA - REGISTRADURIA
echo ========================================
echo.

if "%~1"=="" (
    echo USO: consultar.bat [cedula] [fecha]
    echo.
    echo EJEMPLOS:
    echo   consultar.bat 1036670248 08/01/2015
    echo   consultar.bat 1234567890 15/06/2020
    echo.
    echo NOTA: La fecha debe estar en formato DD/MM/YYYY
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: Falta la fecha
    echo USO: consultar.bat [cedula] [fecha]
    echo EJEMPLO: consultar.bat 1036670248 08/01/2015
    echo.
    pause
    exit /b 1
)

echo Consultando cedula %1 con fecha %2...
echo.

"C:/Users/123/OneDrive/Escritorio/ANDRE/Pruebas Tecnicas/P TUSDATOS/env/Scripts/python.exe" "consulta_cedula.py" %1 %2

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul