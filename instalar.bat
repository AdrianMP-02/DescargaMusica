@echo off
echo ========================================
echo    INSTALADOR DESCARGADOR DE MUSICA
echo ========================================
echo.
echo Instalando las dependencias necesarias...
echo Por favor espere...
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado en su computadora.
    echo.
    echo Por favor descargue Python desde: https://www.python.org/downloads/
    echo Asegurese de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
echo.

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    echo ✓ Entorno virtual creado
) else (
    echo ✓ Entorno virtual ya existe
)

echo.
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo Instalando dependencias (esto puede tomar unos minutos)...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudieron instalar las dependencias.
    echo Verifique su conexion a internet e intente nuevamente.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    ¡INSTALACION COMPLETADA!
echo ========================================
echo.
echo Para usar el programa:
echo 1. Haga doble clic en "ejecutar.bat"
echo 2. O ejecute "python main.py" en esta carpeta
echo.
echo ¡Ya puede cerrar esta ventana!
pause