"""
Sistema de Auto-Actualización
==============================
Módulo para verificar y descargar actualizaciones desde GitHub Releases

Este módulo permite que la aplicación se actualice automáticamente
descargando la última versión desde GitHub.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import shutil
from pathlib import Path


# Configuración del repositorio
REPO_OWNER = "TU_USUARIO_GITHUB"  # ⚠️ CAMBIAR por tu usuario de GitHub
REPO_NAME = "DescargaMusica"      # ⚠️ CAMBIAR por el nombre de tu repositorio
CURRENT_VERSION = "1.0.0"         # ⚠️ CAMBIAR cuando publiques nuevas versiones


class UpdateChecker:
    """Verifica y descarga actualizaciones desde GitHub Releases"""
    
    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        
    def check_for_updates(self):
        """
        Verifica si hay una nueva versión disponible
        
        Returns:
            dict: Información de la actualización o None si no hay actualizaciones
                  {
                      'available': bool,
                      'version': str,
                      'download_url': str,
                      'release_notes': str
                  }
        """
        try:
            # Realizar petición a GitHub API
            req = urllib.request.Request(
                self.api_url,
                headers={'User-Agent': 'DescargadorMusica-AutoUpdater'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Obtener información de la última versión
            latest_version = data.get('tag_name', '').lstrip('v')
            release_notes = data.get('body', 'Sin notas de versión')
            
            # Buscar el ejecutable en los assets
            download_url = None
            for asset in data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break
            
            # Comparar versiones
            if self._is_newer_version(latest_version, self.current_version):
                return {
                    'available': True,
                    'version': latest_version,
                    'download_url': download_url,
                    'release_notes': release_notes,
                    'current_version': self.current_version
                }
            else:
                return {
                    'available': False,
                    'version': self.current_version,
                    'message': 'Ya tienes la última versión'
                }
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    'available': False,
                    'error': 'No se encontraron releases en GitHub'
                }
            else:
                return {
                    'available': False,
                    'error': f'Error HTTP: {e.code}'
                }
        except Exception as e:
            return {
                'available': False,
                'error': f'Error al verificar actualizaciones: {str(e)}'
            }
    
    def download_update(self, download_url, progress_callback=None):
        """
        Descarga la actualización
        
        Args:
            download_url (str): URL del ejecutable
            progress_callback (callable): Función para reportar progreso
            
        Returns:
            str: Ruta del archivo descargado o None si hubo error
        """
        try:
            # Crear carpeta temporal para la descarga
            temp_dir = Path.home() / 'AppData' / 'Local' / 'Temp' / 'DescargadorMusica'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_file = temp_dir / 'DescargadorMusica_new.exe'
            
            # Descargar con reporte de progreso
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, (downloaded * 100) / total_size)
                    progress_callback(percent, downloaded, total_size)
            
            urllib.request.urlretrieve(download_url, temp_file, report_progress)
            
            return str(temp_file)
            
        except Exception as e:
            print(f"Error descargando actualización: {str(e)}")
            return None
    
    def install_update(self, update_file):
        """
        Instala la actualización
        
        Args:
            update_file (str): Ruta del nuevo ejecutable
            
        Returns:
            bool: True si se inició la instalación correctamente
        """
        try:
            # Obtener ruta del ejecutable actual
            if getattr(sys, 'frozen', False):
                # Ejecutando como .exe
                current_exe = sys.executable
            else:
                # Ejecutando como script Python (modo desarrollo)
                return False
            
            # Crear script de actualización que:
            # 1. Espera que la app actual se cierre
            # 2. Reemplaza el ejecutable
            # 3. Reinicia la aplicación
            
            updater_script = Path(update_file).parent / 'updater.bat'
            
            with open(updater_script, 'w') as f:
                f.write(f'''@echo off
echo Actualizando Descargador de Música...
timeout /t 2 /nobreak >nul

echo Reemplazando ejecutable...
move /Y "{update_file}" "{current_exe}"

echo Reiniciando aplicación...
start "" "{current_exe}"

echo Limpiando archivos temporales...
del "%~f0"
''')
            
            # Ejecutar script de actualización y cerrar la app actual
            subprocess.Popen(['cmd.exe', '/c', str(updater_script)], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            print(f"Error instalando actualización: {str(e)}")
            return False
    
    def _is_newer_version(self, latest, current):
        """
        Compara dos versiones en formato X.Y.Z
        
        Args:
            latest (str): Versión más reciente
            current (str): Versión actual
            
        Returns:
            bool: True si latest es más nueva que current
        """
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Rellenar con ceros si las versiones tienen diferentes longitudes
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return latest_parts > current_parts
            
        except ValueError:
            return False


# Función auxiliar para uso sencillo
def check_for_updates():
    """
    Función simple para verificar actualizaciones
    
    Returns:
        dict: Información de actualización
    """
    checker = UpdateChecker(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
    return checker.check_for_updates()


# Ejemplo de uso
if __name__ == "__main__":
    print("🔍 Verificando actualizaciones...")
    
    checker = UpdateChecker(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
    update_info = checker.check_for_updates()
    
    if update_info.get('error'):
        print(f"❌ Error: {update_info['error']}")
    elif update_info.get('available'):
        print(f"✨ Nueva versión disponible: {update_info['version']}")
        print(f"📝 Notas: {update_info['release_notes'][:100]}...")
    else:
        print(f"✅ Ya tienes la última versión ({CURRENT_VERSION})")
