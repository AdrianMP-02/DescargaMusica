@echo off
echo ========================================
echo    DESCARGADOR DE MUSICA YOUTUBE
echo ========================================
echo.
echo Iniciando aplicacion...

REM Verificar si el entorno virtual existe
if not exist ".venv" (
    echo.
    echo ERROR: Las dependencias no estan instaladas.
    echo Por favor ejecute primero "instalar.bat"
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual y ejecutar aplicacion
call .venv\Scripts\activate.bat
python main.py

REM Si hay error, mostrar mensaje
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo ejecutar la aplicacion.
    echo Verifique que la instalacion sea correcta.
    echo.
    pause
)