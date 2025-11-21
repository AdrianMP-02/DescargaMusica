"""
Auto-Compiler para Descargador de Música
=========================================
Detecta automáticamente cambios en main.py y recompila el ejecutable.

USO:
1. Instalar watchdog: pip install watchdog
2. Ejecutar: python auto_compiler.py
3. El script quedará vigilando cambios en main.py
4. Cuando guardes cambios, automáticamente ejecutará crear_ejecutable.bat

Para detener: Presiona Ctrl+C
"""

import sys
import time
import subprocess
import os
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ ERROR: La librería 'watchdog' no está instalada")
    print("\n🔧 Para instalar, ejecuta:")
    print("   pip install watchdog")
    sys.exit(1)


class SourceCodeChangeHandler(FileSystemEventHandler):
    """Maneja eventos de cambios en archivos fuente"""
    
    def __init__(self):
        self.last_modified = {}
        self.debounce_seconds = 2  # Esperar 2 segundos para evitar múltiples compilaciones
        
    def on_modified(self, event):
        """Se ejecuta cuando un archivo es modificado"""
        
        # Ignorar directorios y archivos que no nos interesan
        if event.is_directory:
            return
        
        # Solo reaccionar a cambios en main.py
        if not event.src_path.endswith('main.py'):
            return
        
        # Debounce: evitar múltiples compilaciones por guardados rápidos
        current_time = time.time()
        last_time = self.last_modified.get(event.src_path, 0)
        
        if current_time - last_time < self.debounce_seconds:
            return
        
        self.last_modified[event.src_path] = current_time
        
        # Notificar cambio detectado
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🔔 [{timestamp}] Cambio detectado en: {os.path.basename(event.src_path)}")
        print(f"{'='*60}")
        
        # Compilar el ejecutable
        self.compile_executable()
    
    def compile_executable(self):
        """Ejecuta el script de compilación"""
        try:
            print("🔨 Iniciando compilación del ejecutable...")
            print("⏳ Esto puede tardar unos momentos...\n")
            
            # Ejecutar crear_ejecutable.bat
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['crear_ejecutable.bat'],
                    shell=True,
                    capture_output=True,
                    text=True
                )
            else:  # Linux/Mac
                result = subprocess.run(
                    ['pyinstaller', 'DescargadorMusica.spec'],
                    capture_output=True,
                    text=True
                )
            
            # Verificar resultado
            if result.returncode == 0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"✅ [{timestamp}] ¡Compilación exitosa!")
                print("📦 Ejecutable actualizado en: dist/DescargadorMusica.exe")
            else:
                print(f"❌ Error durante la compilación:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error al compilar: {str(e)}")
        
        print(f"{'='*60}\n")
        print("👀 Vigilando cambios en main.py...")


def main():
    """Función principal"""
    print("=" * 60)
    print("🤖 AUTO-COMPILER para Descargador de Música YouTube")
    print("=" * 60)
    print()
    print("📝 Vigilando cambios en: main.py")
    print("🔨 Auto-compilará cuando detecte cambios")
    print("⏹️  Presiona Ctrl+C para detener")
    print()
    print("=" * 60)
    print()
    
    # Verificar que main.py existe
    if not os.path.exists('main.py'):
        print("❌ ERROR: No se encuentra main.py en el directorio actual")
        print(f"📁 Directorio actual: {os.getcwd()}")
        sys.exit(1)
    
    # Verificar que crear_ejecutable.bat existe
    if os.name == 'nt' and not os.path.exists('crear_ejecutable.bat'):
        print("⚠️  ADVERTENCIA: No se encuentra crear_ejecutable.bat")
        print("   Se usará PyInstaller directamente")
    
    # Crear observador de archivos
    event_handler = SourceCodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    
    try:
        observer.start()
        print("👀 Vigilando cambios en main.py...")
        print()
        
        # Mantener el script corriendo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo auto-compiler...")
        observer.stop()
        
    observer.join()
    print("✅ Auto-compiler detenido correctamente")


if __name__ == "__main__":
    main()
