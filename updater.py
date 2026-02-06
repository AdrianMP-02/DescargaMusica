"""
Sistema de Auto-Actualización
==============================
Módulo para verificar y descargar actualizaciones desde GitHub Releases.

Soporta:
- Verificación automática al inicio de la app
- Actualización de la app (.exe o código fuente)
- Actualización automática de yt-dlp
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import shutil
import time
from pathlib import Path


# ============================================================
# Configuración del repositorio
# ============================================================
REPO_OWNER = "AdrianMP-02"
REPO_NAME = "DescargaMusica"
CURRENT_VERSION = "1.0"  # Versión semántica de la app


class YtDlpUpdater:
    """Gestiona la actualización de yt-dlp"""

    @staticmethod
    def get_installed_version():
        """Retorna la versión instalada de yt-dlp"""
        try:
            import yt_dlp
            return yt_dlp.version.__version__
        except Exception:
            return None

    @staticmethod
    def get_latest_version():
        """Consulta PyPI para obtener la última versión de yt-dlp"""
        try:
            req = urllib.request.Request(
                "https://pypi.org/pypi/yt-dlp/json",
                headers={"User-Agent": "DescargadorMusica-Updater"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["info"]["version"]
        except Exception:
            return None

    @staticmethod
    def needs_update():
        """Retorna True si yt-dlp necesita actualización"""
        installed = YtDlpUpdater.get_installed_version()
        latest = YtDlpUpdater.get_latest_version()
        if not installed or not latest:
            return False
        # Normalizar versiones: quitar ceros iniciales en cada parte (2026.02.04 → 2026.2.4)
        try:
            installed_parts = [int(x) for x in installed.split(".")]
            latest_parts = [int(x) for x in latest.split(".")]
            return latest_parts > installed_parts
        except ValueError:
            return latest > installed  # Fallback lexicográfico

    @staticmethod
    def update(progress_callback=None):
        """
        Actualiza yt-dlp a la última versión.

        Args:
            progress_callback: callable(status_text: str) para reportar progreso

        Returns:
            dict con 'success', 'old_version', 'new_version', 'error'
        """
        old_version = YtDlpUpdater.get_installed_version()
        try:
            if progress_callback:
                progress_callback("Actualizando yt-dlp...")

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                # Forzar reimportación para obtener nueva versión
                if "yt_dlp" in sys.modules:
                    del sys.modules["yt_dlp"]
                if "yt_dlp.version" in sys.modules:
                    del sys.modules["yt_dlp.version"]

                new_version = YtDlpUpdater.get_installed_version()
                return {
                    "success": True,
                    "old_version": old_version,
                    "new_version": new_version,
                }
            else:
                return {
                    "success": False,
                    "old_version": old_version,
                    "error": result.stderr[:300],
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "old_version": old_version,
                "error": "Tiempo de espera agotado al actualizar yt-dlp",
            }
        except Exception as e:
            return {
                "success": False,
                "old_version": old_version,
                "error": str(e),
            }


class UpdateChecker:
    """Verifica y descarga actualizaciones de la app desde GitHub Releases"""

    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.api_url = (
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        )

    # ----------------------------------------------------------
    # Verificación de versión de la app
    # ----------------------------------------------------------
    def check_for_updates(self):
        """
        Verifica si hay una nueva versión de la app disponible en GitHub Releases.

        Returns:
            dict con información de la actualización
        """
        try:
            req = urllib.request.Request(
                self.api_url,
                headers={"User-Agent": "DescargadorMusica-AutoUpdater"},
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            latest_version = data.get("tag_name", "").lstrip("v")
            release_notes = data.get("body", "Sin notas de versión")

            # Buscar asset .exe
            download_url = None
            source_zip_url = data.get("zipball_url")  # Código fuente como fallback
            for asset in data.get("assets", []):
                name_lower = asset["name"].lower()
                if name_lower.endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    break
                elif name_lower.endswith(".zip"):
                    download_url = asset["browser_download_url"]

            if self._is_newer_version(latest_version, self.current_version):
                return {
                    "available": True,
                    "version": latest_version,
                    "download_url": download_url,
                    "source_zip_url": source_zip_url,
                    "release_notes": release_notes,
                    "current_version": self.current_version,
                }
            else:
                return {
                    "available": False,
                    "version": self.current_version,
                    "message": "Ya tienes la última versión",
                }

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {
                    "available": False,
                    "error": "No se encontraron releases en GitHub",
                }
            return {"available": False, "error": f"Error HTTP: {e.code}"}
        except Exception as e:
            return {
                "available": False,
                "error": f"Error al verificar actualizaciones: {str(e)}",
            }

    # ----------------------------------------------------------
    # Descarga
    # ----------------------------------------------------------
    def download_update(self, download_url, progress_callback=None):
        """
        Descarga la actualización con verificación de integridad.

        Args:
            download_url: URL del ejecutable o zip
            progress_callback: callable(percent, downloaded, total)

        Returns:
            str con ruta del archivo descargado o None
        """
        try:
            temp_dir = Path.home() / "AppData" / "Local" / "Temp" / "DescargadorMusica"
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Limpiar descargas previas fallidas
            for old_file in temp_dir.glob("DescargadorMusica_new.*"):
                try:
                    old_file.unlink()
                except OSError:
                    pass

            # Determinar extensión
            if download_url.endswith(".exe"):
                temp_file = temp_dir / "DescargadorMusica_new.exe"
            else:
                temp_file = temp_dir / "DescargadorMusica_update.zip"

            req = urllib.request.Request(
                download_url,
                headers={"User-Agent": "DescargadorMusica-AutoUpdater"},
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                block_size = 8192
                with open(temp_file, "wb") as f:
                    while True:
                        chunk = response.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            percent = min(100, (downloaded * 100) / total_size)
                            progress_callback(percent, downloaded, total_size)

            # Verificar descarga completa
            actual_size = temp_file.stat().st_size
            if total_size > 0 and actual_size != total_size:
                print(f"Error: descarga incompleta ({actual_size}/{total_size} bytes)")
                temp_file.unlink(missing_ok=True)
                return None

            # Verificar tamaño mínimo para .exe (>1MB)
            if download_url.endswith(".exe") and actual_size < 1_000_000:
                print(f"Error: ejecutable descargado demasiado pequeño ({actual_size} bytes)")
                temp_file.unlink(missing_ok=True)
                return None

            print(f"Descarga completada: {actual_size} bytes en {temp_file}")
            return str(temp_file)

        except Exception as e:
            print(f"Error descargando actualización: {str(e)}")
            return None

    # ----------------------------------------------------------
    # Instalación
    # ----------------------------------------------------------
    def install_update(self, update_file):
        """
        Instala la actualización.

        Para modo .exe (frozen): reemplaza el ejecutable y reinicia.
        Para modo script: extrae los archivos fuente y reinicia.

        Returns:
            bool: True si se inició la instalación
        """
        try:
            if getattr(sys, "frozen", False):
                return self._install_exe_update(update_file)
            else:
                return self._install_source_update(update_file)
        except Exception as e:
            print(f"Error instalando actualización: {str(e)}")
            return False

    def _install_exe_update(self, update_file):
        """
        Instala actualización en modo ejecutable (.exe) usando rename trick.
        
        Windows permite renombrar un .exe que está en ejecución, aunque no
        permite borrarlo ni sobreescribirlo. Aprovechamos esto para:
        1. Renombrar el exe actual → _old.exe
        2. Copiar el nuevo exe → nombre original
        3. Lanzar el nuevo exe
        4. Cerrar la app actual
        Al siguiente inicio, se limpia el _old.exe.
        """
        current_exe = Path(sys.executable)
        update_path = Path(update_file)
        old_exe = current_exe.with_name(current_exe.stem + "_old" + current_exe.suffix)

        # --- Validaciones previas ---
        if not update_path.exists():
            print("Error: archivo de actualización no encontrado")
            return False

        file_size = update_path.stat().st_size
        if file_size < 1_000_000:
            print(f"Error: archivo de actualización muy pequeño ({file_size} bytes)")
            update_path.unlink(missing_ok=True)
            return False

        # Validar que es un ejecutable PE válido (header MZ)
        if not self._validate_exe_header(update_path):
            print("Error: el archivo descargado no es un ejecutable válido")
            update_path.unlink(missing_ok=True)
            return False

        # --- Proceso de actualización ---
        try:
            # Paso 1: Eliminar _old.exe de una actualización anterior si existe
            if old_exe.exists():
                try:
                    old_exe.unlink()
                except OSError:
                    # Si no se puede borrar, intentar con otro nombre
                    old_exe = current_exe.with_name(
                        current_exe.stem + "_old2" + current_exe.suffix
                    )

            # Paso 2: Renombrar el exe actual → _old.exe
            # Windows permite renombrar un exe en ejecución
            os.rename(str(current_exe), str(old_exe))

            # Paso 3: Copiar el nuevo exe al nombre original
            shutil.copy2(str(update_path), str(current_exe))

            # Paso 4: Verificar que la copia fue exitosa
            if not current_exe.exists() or current_exe.stat().st_size < 1_000_000:
                # Rollback: restaurar el exe original
                print("Error: la copia del nuevo exe falló, restaurando...")
                if current_exe.exists():
                    current_exe.unlink()
                os.rename(str(old_exe), str(current_exe))
                return False

            # Paso 5: Lanzar el nuevo exe
            subprocess.Popen(
                [str(current_exe)],
                creationflags=subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
                if hasattr(subprocess, "DETACHED_PROCESS")
                else 0,
            )

            # Paso 6: Limpiar archivo descargado
            update_path.unlink(missing_ok=True)

            return True

        except PermissionError as e:
            print(f"Error de permisos durante actualización: {e}")
            # Intentar rollback si el rename ya se hizo
            if old_exe.exists() and not current_exe.exists():
                try:
                    os.rename(str(old_exe), str(current_exe))
                except OSError:
                    pass
            return False
        except Exception as e:
            print(f"Error durante actualización: {e}")
            # Intentar rollback
            if old_exe.exists() and not current_exe.exists():
                try:
                    os.rename(str(old_exe), str(current_exe))
                except OSError:
                    pass
            return False

    @staticmethod
    def _validate_exe_header(exe_path):
        """Verifica que un archivo tiene header MZ válido (ejecutable PE de Windows)"""
        try:
            with open(exe_path, "rb") as f:
                header = f.read(2)
                return header == b"MZ"
        except Exception:
            return False

    @staticmethod
    def cleanup_old_exe():
        """
        Limpia el exe antiguo tras una actualización exitosa.
        Llamar al inicio de la app.
        """
        if not getattr(sys, "frozen", False):
            return

        current_exe = Path(sys.executable)
        exe_dir = current_exe.parent

        # Buscar y eliminar archivos _old*.exe
        for old_file in exe_dir.glob(f"{current_exe.stem.replace('_old', '').replace('_old2', '')}*_old*.exe"):
            try:
                # Esperar un momento para que el proceso anterior termine
                time.sleep(1)
                old_file.unlink()
                print(f"Limpieza: eliminado {old_file.name}")
            except PermissionError:
                # El proceso anterior aún existe, intentar más tarde
                print(f"Limpieza: {old_file.name} aún en uso, se eliminará después")
            except Exception as e:
                print(f"Limpieza: error eliminando {old_file.name}: {e}")

    def _install_source_update(self, update_file):
        """Instala actualización en modo script (código fuente)"""
        if not update_file.endswith(".zip"):
            return False

        try:
            import zipfile

            app_dir = os.path.dirname(os.path.abspath(__file__))
            temp_extract = Path(update_file).parent / "extracted"

            # Extraer zip
            with zipfile.ZipFile(update_file, "r") as zf:
                zf.extractall(temp_extract)

            # Buscar la carpeta raíz dentro del zip (GitHub añade prefijo)
            extracted_dirs = list(temp_extract.iterdir())
            source_dir = extracted_dirs[0] if extracted_dirs else temp_extract

            # Copiar archivos relevantes
            files_to_update = ["main.py", "updater.py", "requirements.txt"]
            for fname in files_to_update:
                src = source_dir / fname
                dst = Path(app_dir) / fname
                if src.exists():
                    shutil.copy2(str(src), str(dst))

            # Limpiar
            shutil.rmtree(str(temp_extract), ignore_errors=True)
            if os.path.exists(update_file):
                os.remove(update_file)

            return True

        except Exception as e:
            print(f"Error instalando actualización de fuente: {e}")
            return False

    # ----------------------------------------------------------
    # Comparador de versiones
    # ----------------------------------------------------------
    def _is_newer_version(self, latest, current):
        """Compara dos versiones semánticas o numéricas"""
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]

            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))

            return latest_parts > current_parts
        except ValueError:
            # Fallback: comparación de cadenas
            return latest != current and latest > current


# ============================================================
# Funciones auxiliares
# ============================================================
def check_for_updates():
    """Función simple para verificar actualizaciones de la app"""
    checker = UpdateChecker(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
    return checker.check_for_updates()


def check_ytdlp_update():
    """Función simple para verificar actualización de yt-dlp"""
    return YtDlpUpdater.needs_update()


def update_ytdlp(progress_callback=None):
    """Función simple para actualizar yt-dlp"""
    return YtDlpUpdater.update(progress_callback)


# ============================================================
# Ejecución directa
# ============================================================
if __name__ == "__main__":
    print("🔍 Verificando actualizaciones de la app...")

    checker = UpdateChecker(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
    update_info = checker.check_for_updates()

    if update_info.get("error"):
        print(f"❌ Error: {update_info['error']}")
    elif update_info.get("available"):
        print(f"✨ Nueva versión disponible: {update_info['version']}")
        print(f"📝 Notas: {update_info['release_notes'][:100]}...")
    else:
        print(f"✅ App al día ({CURRENT_VERSION})")

    print("\n🔍 Verificando yt-dlp...")
    installed = YtDlpUpdater.get_installed_version()
    latest = YtDlpUpdater.get_latest_version()
    print(f"  Instalada: {installed}")
    print(f"  Última:    {latest}")
    if YtDlpUpdater.needs_update():
        print("  ⚠️ Actualización de yt-dlp disponible")
    else:
        print("  ✅ yt-dlp al día")
