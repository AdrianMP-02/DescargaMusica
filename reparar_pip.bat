@echo off
echo ========================================
echo   REPARAR PIP EN ENTORNO VIRTUAL
echo ========================================
echo.

REM Verificar que existe el entorno virtual
if not exist ".venv" (
    echo ERROR: No se encuentra el entorno virtual .venv
    echo Ejecute "instalar.bat" primero
    pause
    exit /b 1
)

echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo Reparando pip...
python -m ensurepip --upgrade
python -m pip install --upgrade pip

echo.
echo Verificando pip...
pip --version

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo       ¡PIP REPARADO!
    echo ========================================
    echo.
    echo Ahora puedes ejecutar crear_ejecutable.bat
) else (
    echo.
    echo ERROR: No se pudo reparar pip.
    echo Intenta recrear el entorno virtual con:
    echo    recrear_entorno.bat
)

echo.
pause
