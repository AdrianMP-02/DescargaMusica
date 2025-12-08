@echo off
echo ========================================
echo   CREAR EJECUTABLE INDEPENDIENTE
echo ========================================
echo.
echo Este script convierte la aplicacion en un archivo .exe
echo que NO necesita instalacion de Python ni dependencias.
echo Incluye FFmpeg para conversion a MP3.
echo.
echo ATENCION: Este proceso puede tomar varios minutos.
echo.
pause

REM Activar entorno virtual
if not exist ".venv" (
    echo ERROR: Primero ejecute "instalar.bat"
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Verificando pip...
pip --version >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  pip esta danado, reparando...
    python -m ensurepip --upgrade >nul 2>&1
    python -m pip install --upgrade pip
    echo ✓ pip reparado
    echo.
)

echo Instalando PyInstaller...
python -m pip install pyinstaller

echo.
echo Limpiando compilaciones anteriores...
python -m PyInstaller --clean DescargadorMusica.spec 2>nul

if %errorlevel% neq 0 (
    echo.
    echo Creando ejecutable (primera vez)...
    python -m PyInstaller DescargadorMusica.spec
)

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo       ¡EJECUTABLE CREADO!
    echo ========================================
    echo.
    echo El archivo ejecutable esta en:
    echo dist\DescargadorMusica.exe
    echo.
    echo ✅ INCLUYE FFmpeg para conversion a MP3
    echo ✅ NO requiere Python ni dependencias
    echo ✅ Funciona en cualquier PC Windows
    echo.
    echo Puede copiar este archivo a cualquier PC
    echo y funcionara sin instalar nada mas.
    echo.
) else (
    echo.
    echo ERROR: No se pudo crear el ejecutable.
    echo Verifique que la instalacion sea correcta.
)

pause