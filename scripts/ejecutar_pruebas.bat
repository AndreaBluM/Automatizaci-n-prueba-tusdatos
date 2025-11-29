@echo off
cls
echo ========================================
echo   BOT REGISTRADURIA - SUITE DE PRUEBAS
echo ========================================
echo.

:menu
echo Seleccione el tipo de pruebas a ejecutar:
echo.
echo 1. Todas las pruebas (Completo)
echo 2. Solo pruebas unitarias
echo 3. Solo pruebas de integracion
echo 4. Solo pruebas de datos  
echo 5. Pruebas con salida detallada
echo 6. Ver ultimo reporte JSON
echo 7. Salir
echo.
set /p opcion="Ingrese su opcion (1-7): "

if "%opcion%"=="1" goto todas
if "%opcion%"=="2" goto unitarias
if "%opcion%"=="3" goto integracion
if "%opcion%"=="4" goto datos
if "%opcion%"=="5" goto verbose
if "%opcion%"=="6" goto reporte
if "%opcion%"=="7" goto salir
goto menu

:todas
echo.
echo ^>^>^> Ejecutando TODAS las pruebas...
echo.
python ..\tests\ejecutar_todas_las_pruebas.py
pause
goto menu

:unitarias
echo.
echo ^>^>^> Ejecutando solo pruebas UNITARIAS...
echo.
python ..\tests\test_unitarios.py
pause
goto menu

:integracion
echo.
echo ^>^>^> Ejecutando solo pruebas de INTEGRACION...
echo.
python ..\tests\test_integracion.py
pause
goto menu

:datos
echo.
echo ^>^>^> Ejecutando solo pruebas de DATOS...
echo.
python ..\tests\test_datos.py
pause
goto menu

:verbose
echo.
echo ^>^>^> Ejecutando con salida DETALLADA...
echo.
python ..\tests\ejecutar_todas_las_pruebas.py --verbose
pause
goto menu

:reporte
echo.
echo ^>^>^> Buscando ultimo reporte JSON...
echo.
for /f %%i in ('dir /b /od ..\output\reporte_pruebas_*.json 2^>nul') do set ultimo=%%i
if defined ultimo (
    echo Ultimo reporte encontrado: %ultimo%
    echo.
    type "..\output\%ultimo%"
) else (
    echo No se encontraron reportes JSON.
)
pause
goto menu

:salir
echo.
echo Saliendo del sistema de pruebas...
exit /b 0