import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
import subprocess
import sys
import shutil
import zipfile
import urllib.request
from pathlib import Path

# Importar sistema de actualización
try:
    from updater import UpdateChecker, CURRENT_VERSION, REPO_OWNER, REPO_NAME
    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False
    CURRENT_VERSION = "1.0"

class YouTubeMusicDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Música")
        self.root.geometry("600x600")
        self.root.resizable(False, False)  # Ventana fija para evitar confusión
        self.root.configure(bg='#f0f0f0')  # Fondo más claro
        
        # Variables
        self.download_path = tk.StringVar()
        self.download_path.set(str(Path.home() / "Downloads"))
        self.use_conversion = tk.BooleanVar()
        self.use_conversion.set(True)  # Por defecto intentar conversión a MP3
        
        # Variable para formato de descarga (mp3 o mp4)
        self.download_format = tk.StringVar()
        self.download_format.set('mp3')  # Por defecto música (MP3)
        
        # Variables para progreso avanzado
        self.current_percent = tk.StringVar()
        self.download_speed = tk.StringVar()
        self.eta = tk.StringVar()
        self.file_size = tk.StringVar()
        
        # Variable para playlists
        self.allow_playlists = tk.BooleanVar()
        self.allow_playlists.set(False)
        
        self.setup_styles()
        self.setup_ui()
    
    def setup_styles(self):
        """Configurar estilos simples y accesibles"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Colores simples y contrastados
        colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'select_bg': '#ffffff',
            'select_fg': '#000000',
            'accent': '#0066cc',
            'accent_hover': '#0052a3',
            'success': '#008000',
            'warning': '#ff6600',
            'error': '#cc0000',
            'card_bg': '#ffffff',
            'entry_bg': '#ffffff'
        }
        
        # Configurar estilos simples y accesibles
        style.configure('Simple.TFrame', 
                       background=colors['bg'],
                       relief='flat')
        
        style.configure('Simple.TLabel', 
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Arial', 12))
        
        style.configure('Title.TLabel', 
                       background=colors['bg'],
                       foreground=colors['accent'],
                       font=('Arial', 24, 'bold'))
        
        style.configure('Label.TLabel', 
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Arial', 14, 'bold'))
        
        style.configure('Instruction.TLabel', 
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Arial', 11))
        
        style.configure('Simple.TEntry', 
                       fieldbackground=colors['entry_bg'],
                       foreground=colors['fg'],
                       borderwidth=2,
                       relief='solid',
                       font=('Arial', 12))
        
        style.configure('Simple.TButton', 
                       background=colors['select_bg'],
                       foreground=colors['fg'],
                       borderwidth=2,
                       relief='raised',
                       font=('Arial', 12))
        
        style.configure('Big.TButton', 
                       background=colors['accent'],
                       foreground='white',
                       borderwidth=3,
                       relief='raised',
                       font=('Arial', 18, 'bold'))
        
        style.map('Big.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])])
        
        # Progressbar simple
        style.configure('Simple.Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor='#e0e0e0',
                       borderwidth=1,
                       relief='solid')

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="30", style='Simple.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título simple
        title_label = ttk.Label(main_frame, text="Descargador de Música YouTube", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Campo de URL
        url_label = ttk.Label(main_frame, text="Enlace del video:", 
                             style='Label.TLabel')
        url_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.url_entry = ttk.Entry(main_frame, font=("Arial", 14), width=60, style='Simple.TEntry')
        self.url_entry.pack(fill=tk.X, pady=(0, 30), ipady=10)
        
        # Selector de formato (MP3 o MP4)
        format_label = ttk.Label(main_frame, text="¿Qué desea descargar?", style='Label.TLabel')
        format_label.pack(anchor=tk.W, pady=(0, 15))
        
        format_frame = ttk.Frame(main_frame, style='Simple.TFrame')
        format_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Radio button para MP3 (Música)
        mp3_radio = tk.Radiobutton(format_frame, 
                                   text="🎵 Música (MP3) - Solo audio", 
                                   variable=self.download_format, 
                                   value='mp3',
                                   font=("Arial", 14, 'bold'),
                                   bg='#f0f0f0',
                                   fg='#000000',
                                   activebackground='#f0f0f0',
                                   selectcolor='#ffffff',
                                   command=self.update_download_button,
                                   cursor='hand2',
                                   padx=10,
                                   pady=10)
        mp3_radio.pack(anchor=tk.W, pady=(0, 15))
        
        # Radio button para MP4 (Video)
        mp4_radio = tk.Radiobutton(format_frame, 
                                   text="🎬 Video (MP4) - Video completo", 
                                   variable=self.download_format, 
                                   value='mp4',
                                   font=("Arial", 14, 'bold'),
                                   bg='#f0f0f0',
                                   fg='#000000',
                                   activebackground='#f0f0f0',
                                   selectcolor='#ffffff',
                                   command=self.update_download_button,
                                   cursor='hand2',
                                   padx=10,
                                   pady=10)
        mp4_radio.pack(anchor=tk.W, pady=(0, 0))
        
        # Carpeta de descarga
        path_label = ttk.Label(main_frame, text="Guardar en:", style='Label.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 10))
        
        path_frame = ttk.Frame(main_frame, style='Simple.TFrame')
        path_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.download_path, 
                                   style='Simple.TEntry', font=("Arial", 12))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        browse_btn = ttk.Button(path_frame, text="Cambiar", style='Simple.TButton',
                               command=self.select_download_path)
        browse_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Botón principal de descarga (grande y claro)
        self.download_btn = ttk.Button(main_frame, text="DESCARGAR MÚSICA", 
                                      command=self.start_download, style="Big.TButton")
        self.download_btn.pack(pady=(0, 30), fill=tk.X, ipady=15)
        
        # Configurar opciones automáticas (sin mostrar al usuario)
        self.use_conversion = tk.BooleanVar(value=True)  # Siempre convertir a MP3
        self.allow_playlists = tk.BooleanVar(value=False)  # Nunca descargar playlists
        
        # Barra de progreso simple
        progress_label = ttk.Label(main_frame, text="Progreso:", style='Label.TLabel')
        progress_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate', 
                                       style='Simple.Horizontal.TProgressbar', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Estado de descarga simple
        self.status_label = ttk.Label(main_frame, text="Listo para descargar", 
                                     style='Label.TLabel')
        self.status_label.pack(pady=(0, 20))
        
        # Información básica de progreso
        self.percent_label = ttk.Label(main_frame, text="", style='Label.TLabel')
        self.percent_label.pack()
        
        # Variables para datos que no se muestran pero se usan internamente
        self.speed_label = None
        self.eta_label = None  
        self.size_label = None
        
        # Área de información simple
        info_label = ttk.Label(main_frame, text="Información del archivo:", style='Label.TLabel')
        info_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.info_text = tk.Text(main_frame, height=4, wrap=tk.WORD, 
                                state=tk.DISABLED, font=("Arial", 11),
                                bg='white', fg='black', relief='solid', borderwidth=1)
        self.info_text.pack(fill=tk.X, padx=0, pady=(0, 20))
        
        # Botón de actualización (si está disponible)
        if UPDATER_AVAILABLE:
            update_frame = ttk.Frame(main_frame, style='Simple.TFrame')
            update_frame.pack(fill=tk.X, pady=(0, 10))
            
            update_btn = ttk.Button(update_frame, text="🔄 Buscar Actualizaciones", 
                                   command=self.check_updates, style='Simple.TButton')
            update_btn.pack(side=tk.LEFT)
            
            self.version_label = ttk.Label(update_frame, text=f"v{CURRENT_VERSION}", 
                                          style='Instruction.TLabel')
            self.version_label.pack(side=tk.RIGHT, padx=(10, 0))
        
    def select_download_path(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)
    
    def update_download_button(self):
        """Actualiza el texto del botón según el formato seleccionado"""
        if self.download_format.get() == 'mp3':
            self.download_btn.config(text="DESCARGAR MÚSICA")
        else:
            self.download_btn.config(text="DESCARGAR VIDEO")
    
    def get_ffmpeg_path(self):
        """Busca FFmpeg en varias ubicaciones (orden de prioridad)"""
        app_dir = os.path.dirname(__file__)
        
        # Ubicaciones posibles de FFmpeg (orden de prioridad)
        possible_paths = []
        
        # 1. imageio-ffmpeg (más confiable)
        try:
            import imageio_ffmpeg
            imageio_path = imageio_ffmpeg.get_ffmpeg_exe()
            if imageio_path:
                possible_paths.append(imageio_path)
        except ImportError:
            pass
        
        # 2. Instalación portable en carpeta del proyecto
        possible_paths.extend([
            os.path.join(app_dir, 'ffmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(app_dir, 'ffmpeg.exe'),
        ])
        
        # 3. FFmpeg en PATH del sistema
        possible_paths.append('ffmpeg')
        
        # 4. Ubicaciones comunes de Windows
        if os.name == 'nt':
            possible_paths.extend([
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            ])
        
        # Probar cada ubicación
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                continue
        
        return None
    
    def get_ffmpeg_and_ffprobe_paths(self):
        """Obtiene las rutas de ffmpeg y ffprobe"""
        try:
            import imageio_ffmpeg
            
            # Obtener la ruta base de imageio-ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Para imageio-ffmpeg, ffprobe generalmente está en la misma ubicación
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                
                # Buscar ffprobe en la misma carpeta
                possible_ffprobe_names = [
                    'ffprobe.exe',
                    'ffprobe-win-x86_64-v7.1.exe',  # Nombre específico como ffmpeg
                    os.path.basename(ffmpeg_path).replace('ffmpeg', 'ffprobe')
                ]
                
                ffprobe_path = None
                for name in possible_ffprobe_names:
                    test_path = os.path.join(ffmpeg_dir, name)
                    if os.path.exists(test_path):
                        ffprobe_path = test_path
                        break
                
                return ffmpeg_path, ffprobe_path
        except ImportError:
            pass
        
        return None, None

    def run_diagnostics(self):
        """Ejecuta un diagnóstico completo del sistema"""
        def diagnose():
            try:
                self.update_status("Ejecutando diagnóstico...")
                self.progress.start()
                
                report = "=== DIAGNÓSTICO COMPLETO FFmpeg ===\n\n"
                
                # 1. Información del sistema
                report += f"Sistema: {os.name}\n"
                report += f"Python: {sys.version}\n"
                report += f"Directorio trabajo: {os.getcwd()}\n\n"
                
                # 2. Verificar imageio-ffmpeg
                report += "--- imageio-ffmpeg ---\n"
                try:
                    import imageio_ffmpeg
                    report += f"✅ imageio-ffmpeg instalado\n"
                    try:
                        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                        report += f"Ruta FFmpeg: {ffmpeg_exe}\n"
                        report += f"Existe archivo: {os.path.exists(ffmpeg_exe)}\n"
                        
                        if os.path.exists(ffmpeg_exe):
                            # Probar ejecución
                            result = subprocess.run([ffmpeg_exe, '-version'], 
                                                  capture_output=True, text=True, timeout=10)
                            report += f"Código retorno: {result.returncode}\n"
                            if result.returncode == 0:
                                report += f"✅ FFmpeg funciona correctamente\n"
                            else:
                                report += f"❌ Error al ejecutar: {result.stderr[:200]}\n"
                        else:
                            report += f"❌ Archivo no existe\n"
                    except Exception as e:
                        report += f"❌ Error obteniendo ruta: {str(e)}\n"
                except ImportError as e:
                    report += f"❌ imageio-ffmpeg no instalado: {str(e)}\n"
                
                # 3. Verificar FFmpeg en PATH
                report += "\n--- FFmpeg en PATH ---\n"
                try:
                    result = subprocess.run(['ffmpeg', '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        report += f"✅ FFmpeg en PATH funciona\n"
                    else:
                        report += f"❌ FFmpeg en PATH con error\n"
                except Exception as e:
                    report += f"❌ FFmpeg no en PATH: {str(e)}\n"
                
                # 4. Verificar instalación local
                report += "\n--- FFmpeg local ---\n"
                local_paths = [
                    os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                    os.path.join(os.path.dirname(__file__), 'ffmpeg.exe'),
                ]
                
                for path in local_paths:
                    report += f"Verificando: {path}\n"
                    report += f"Existe: {os.path.exists(path)}\n"
                
                # 5. Verificar permisos de escritura
                report += "\n--- Permisos ---\n"
                app_dir = os.path.dirname(__file__)
                report += f"Directorio app: {app_dir}\n"
                report += f"Escritura permitida: {os.access(app_dir, os.W_OK)}\n"
                
                # Mostrar reporte completo
                self.update_info(report)
                messagebox.showinfo("Diagnóstico Completo", 
                    "Diagnóstico completado.\nRevisa la información en el panel inferior.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error durante diagnóstico: {str(e)}")
            finally:
                self.progress.stop()
                self.update_status("Diagnóstico completado")
        
        thread = threading.Thread(target=diagnose)
        thread.daemon = True
        thread.start()

    def check_ffmpeg(self):
        """Verifica si FFmpeg está instalado"""
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            messagebox.showinfo("FFmpeg", f"✅ FFmpeg encontrado en:\n{ffmpeg_path}")
            return True
        else:
            messagebox.showerror("FFmpeg", 
                               "❌ FFmpeg no está instalado\n\n" +
                               "Para diagnosticar el problema:\n" +
                               "1. Haz clic en 'Diagnóstico' para ver detalles\n" +
                               "2. Haz clic en 'Instalar FFmpeg' para instalar\n" +
                               "3. O descárgalo desde: https://ffmpeg.org/download.html")
            return False
    
    def install_ffmpeg(self):
        """Instala FFmpeg de varias maneras"""
        def install():
            try:
                self.update_status("Instalando FFmpeg...")
                self.progress.start()
                
                success = False
                
                # Método 1: Instalar imageio-ffmpeg (más confiable)
                try:
                    self.update_status("Instalando imageio-ffmpeg...")
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'imageio-ffmpeg'], 
                                          capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        # Verificar que funcione
                        try:
                            import imageio_ffmpeg
                            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                            test_result = subprocess.run([ffmpeg_path, '-version'], 
                                                       capture_output=True, text=True, timeout=5)
                            if test_result.returncode == 0:
                                success = True
                                messagebox.showinfo("FFmpeg", 
                                    f"✅ FFmpeg instalado correctamente!\n\n" +
                                    f"Ubicación: {ffmpeg_path}\n\n" +
                                    "Ahora puedes descargar y convertir audio a MP3.")
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Error instalando imageio-ffmpeg: {e}")
                
                # Método 2: Instalación portable para Windows
                if not success and os.name == 'nt':
                    success = self.install_portable_ffmpeg()
                
                # Método 3: Instalación simple usando executable directo
                if not success:
                    success = self.install_simple_ffmpeg()
                
                # Si todo falló
                if not success:
                    messagebox.showwarning("FFmpeg", 
                        "⚠️ No se pudo instalar FFmpeg automáticamente\n\n" +
                        "Opciones:\n" +
                        "1. Desmarca 'Convertir a MP3' para descargar sin conversión\n" +
                        "2. Descarga FFmpeg manualmente desde: https://ffmpeg.org\n" +
                        "3. Instala FFmpeg usando un gestor de paquetes como Chocolatey")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Error durante la instalación: {str(e)}")
            finally:
                self.progress.stop()
                self.update_status("Listo")
        
        thread = threading.Thread(target=install)
        thread.daemon = True
        thread.start()
    
    def install_portable_ffmpeg(self):
        """Instala FFmpeg portable en la carpeta del proyecto"""
        try:
            self.update_status("Instalando FFmpeg portable...")
            app_dir = os.path.dirname(__file__)
            ffmpeg_dir = os.path.join(app_dir, 'ffmpeg')
            
            # Si ya existe, verificar que funcione
            ffmpeg_exe = os.path.join(ffmpeg_dir, 'bin', 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                try:
                    result = subprocess.run([ffmpeg_exe, '-version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        messagebox.showinfo("FFmpeg", 
                            f"✅ FFmpeg portable ya instalado!\n\nUbicación: {ffmpeg_exe}")
                        return True
                except:
                    pass
            
            # Descargar FFmpeg portable
            self.update_status("Descargando FFmpeg portable...")
            
            # URL más pequeña y confiable
            url = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-4.4.1-essentials_build.zip"
            zip_path = os.path.join(app_dir, 'ffmpeg_portable.zip')
            
            # Descargar con progress
            def download_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) / total_size)
                    self.update_status(f"Descargando FFmpeg: {percent:.1f}%")
            
            urllib.request.urlretrieve(url, zip_path, download_progress)
            
            self.update_status("Extrayendo FFmpeg...")
            
            # Extraer
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(app_dir)
            
            # Buscar carpeta extraída y renombrarla
            extracted_folders = [f for f in os.listdir(app_dir) 
                               if f.startswith('ffmpeg-') and os.path.isdir(os.path.join(app_dir, f))]
            
            if extracted_folders:
                old_name = os.path.join(app_dir, extracted_folders[0])
                if os.path.exists(ffmpeg_dir):
                    shutil.rmtree(ffmpeg_dir)
                os.rename(old_name, ffmpeg_dir)
            
            # Limpiar archivo zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            # Verificar instalación
            if os.path.exists(ffmpeg_exe):
                try:
                    result = subprocess.run([ffmpeg_exe, '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        messagebox.showinfo("FFmpeg", 
                            f"✅ FFmpeg portable instalado correctamente!\n\n" +
                            f"Ubicación: {ffmpeg_exe}\n\n" +
                            "Ahora puedes descargar y convertir audio a MP3.")
                        return True
                except Exception as e:
                    messagebox.showerror("Error", 
                        f"FFmpeg descargado pero no funciona: {str(e)}")
            
            return False
            
        except Exception as e:
            messagebox.showerror("Error", 
                f"Error instalando FFmpeg portable: {str(e)}\n\n" +
                "Intenta descargar manualmente desde https://ffmpeg.org")
            return False
    
    def install_simple_ffmpeg(self):
        """Método simple: descargar solo el ejecutable FFmpeg"""
        try:
            self.update_status("Instalando FFmpeg simple...")
            app_dir = os.path.dirname(__file__)
            ffmpeg_exe = os.path.join(app_dir, 'ffmpeg.exe')
            
            if os.path.exists(ffmpeg_exe):
                try:
                    result = subprocess.run([ffmpeg_exe, '-version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        messagebox.showinfo("FFmpeg", 
                            f"✅ FFmpeg ya está instalado!\n\nUbicación: {ffmpeg_exe}")
                        return True
                except:
                    pass
            
            # URL directa a ffmpeg.exe (más pequeño)
            url = "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4.0/win32-x64"
            
            self.update_status("Descargando FFmpeg ejecutable...")
            urllib.request.urlretrieve(url, ffmpeg_exe)
            
            # Verificar que funcione
            try:
                result = subprocess.run([ffmpeg_exe, '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    messagebox.showinfo("FFmpeg", 
                        f"✅ FFmpeg instalado correctamente!\n\n" +
                        f"Ubicación: {ffmpeg_exe}\n\n" +
                        "Ahora puedes descargar y convertir audio a MP3.")
                    return True
            except Exception as e:
                messagebox.showerror("Error", f"FFmpeg descargado pero no funciona: {str(e)}")
                
            return False
            
        except Exception as e:
            messagebox.showerror("Error", 
                f"Error instalando FFmpeg simple: {str(e)}")
            return False
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def reset_progress_info(self):
        """Reinicia la información de progreso"""
        self.progress.configure(mode='indeterminate')
        self.progress['value'] = 0
        self.percent_label.config(text="0%")
    
    def update_info(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Extraer información de progreso
            percent_str = d.get('_percent_str', '0%').strip()
            percent_num = 0
            
            try:
                # Extraer número del porcentaje
                if '%' in percent_str:
                    percent_num = float(percent_str.replace('%', ''))
            except (ValueError, TypeError):
                percent_num = 0
            
            # Actualizar barra de progreso
            self.progress.configure(mode='determinate')
            self.progress['value'] = percent_num
            
            # Actualizar información básica
            self.percent_label.config(text=f"Descargando: {percent_str}")
            
            # Actualizar estado
            filename = d.get('filename', 'archivo')
            if filename:
                short_name = os.path.basename(filename)[:30] + "..." if len(os.path.basename(filename)) > 30 else os.path.basename(filename)
                self.update_status(f"📥 Descargando: {short_name}")
            
        elif d['status'] == 'finished':
            # Completar la barra de progreso
            self.progress['value'] = 100
            self.percent_label.config(text="Descarga completada")
            
            filename = d.get('filename', '')
            if filename:
                short_name = os.path.basename(filename)[:30] + "..." if len(os.path.basename(filename)) > 30 else os.path.basename(filename)
                self.update_status(f"✅ Descarga completada: {short_name}")
            else:
                self.update_status("✅ Descarga completada, procesando...")
                
        elif d['status'] == 'error':
            self.progress.configure(mode='indeterminate')
            self.progress.stop()
            self.update_status("❌ Error durante la descarga")
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Atención", "Por favor escriba la dirección del video")
            return
        
        if not os.path.exists(self.download_path.get()):
            messagebox.showerror("Atención", "La carpeta seleccionada no existe")
            return
        
        # Verificar configuración de playlist
        single_video = True
        if self.detect_playlist(url):
            if not self.allow_playlists.get():
                # Mostrar advertencia y preguntar
                response = messagebox.askyesno(
                    "🎵 Playlist Detectada",
                    "Esta URL contiene una playlist o mix.\n\n" +
                    "Por defecto se descargará SOLO el video actual para mayor velocidad.\n\n" +
                    "¿Continuar con descarga rápida del video individual?"
                )
                if not response:
                    return
                single_video = True
            else:
                single_video = False
                # Confirmar descarga de playlist
                response = messagebox.askyesno(
                    "📋 Descargar Playlist",
                    "Se descargará la playlist completa (máximo 50 videos).\n\n" +
                    "Esto puede tardar mucho tiempo.\n\n" +
                    "¿Continuar?"
                )
                if not response:
                    return
        
        # Iniciar descarga en hilo separado
        thread = threading.Thread(target=self.download_audio, args=(url, single_video))
        thread.daemon = True
        thread.start()
    
    def download_audio(self, url, single_video=True):
        try:
            self.download_btn.config(state=tk.DISABLED)
            self.reset_progress_info()
            self.progress.start()
            
            # Obtener formato seleccionado
            download_format = self.download_format.get()
            
            if download_format == 'mp4':
                self.update_status("🔍 Obteniendo información del video...")
            else:
                self.update_status("🔍 Obteniendo información del audio...")
            
            # Configuración base de yt-dlp
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path.get(), '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noplaylist': single_video,
                'extract_flat': False,
                'writeinfojson': False,
                'writedescription': False,
                'writethumbnail': False,
                'writesubtitles': False,
                'ignoreerrors': True,
            }
            
            if not single_video:
                ydl_opts['outtmpl'] = os.path.join(self.download_path.get(), '%(playlist_index)02d - %(title)s.%(ext)s')
                ydl_opts['playlistend'] = 50
                self.update_status("⚠️ Modo playlist: Se descargarán máximo 50 videos")
            else:
                if download_format == 'mp4':
                    self.update_status("🎯 Modo video individual: Descarga rápida")
                else:
                    self.update_status("🎯 Modo audio individual: Descarga rápida")
            
            # Configurar según formato seleccionado
            if download_format == 'mp4':
                # Configuración para descargar VIDEO (MP4)
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                self.update_status("📹 Preparando descarga de video MP4...")
                
                # Para MP4, usar ffmpeg para combinar video y audio si es necesario
                ffmpeg_path = self.get_ffmpeg_path()
                if ffmpeg_path:
                    ffmpeg_full_path, ffprobe_full_path = self.get_ffmpeg_and_ffprobe_paths()
                    if ffmpeg_full_path and 'imageio_ffmpeg' in ffmpeg_full_path:
                        ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_full_path)
                        os.environ['FFMPEG_BINARY'] = ffmpeg_full_path
                        if ffprobe_full_path:
                            os.environ['FFPROBE_BINARY'] = ffprobe_full_path
                    elif ffmpeg_path != 'ffmpeg':
                        ffmpeg_dir = os.path.dirname(ffmpeg_path)
                        ydl_opts['ffmpeg_location'] = ffmpeg_dir
                else:
                    # Si no hay FFmpeg, descargar el mejor formato único disponible
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                    
            else:
                # Configuración para descargar AUDIO (MP3)
                ydl_opts['format'] = 'bestaudio/best'
                
                if self.use_conversion.get():
                    ffmpeg_path = self.get_ffmpeg_path()
                    
                    if ffmpeg_path:
                        self.update_status(f"Usando FFmpeg: {os.path.basename(ffmpeg_path)}")
                        
                        ffmpeg_full_path, ffprobe_full_path = self.get_ffmpeg_and_ffprobe_paths()
                        
                        if ffmpeg_full_path and 'imageio_ffmpeg' in ffmpeg_full_path:
                            self.update_status("Configurando imageio-ffmpeg...")
                            ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_full_path)
                            os.environ['FFMPEG_BINARY'] = ffmpeg_full_path
                            if ffprobe_full_path:
                                os.environ['FFPROBE_BINARY'] = ffprobe_full_path
                                
                        elif ffmpeg_path != 'ffmpeg':
                            ffmpeg_dir = os.path.dirname(ffmpeg_path)
                            ydl_opts['ffmpeg_location'] = ffmpeg_dir
                        
                        # Configurar postprocessor para MP3
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                        
                        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
                        
                        print(f"DEBUG: FFmpeg path: {ffmpeg_path}")
                        print(f"DEBUG: FFmpeg full path: {ffmpeg_full_path}")
                        print(f"DEBUG: FFprobe full path: {ffprobe_full_path}")
                        print(f"DEBUG: ffmpeg_location: {ydl_opts.get('ffmpeg_location', 'No configurado')}")
                        print(f"DEBUG: FFMPEG_BINARY env: {os.environ.get('FFMPEG_BINARY', 'No configurado')}")
                        
                    else:
                        self.update_status("FFmpeg no encontrado")
                        response = messagebox.askyesno("FFmpeg no encontrado", 
                            "FFmpeg no está instalado.\n\n" +
                            "¿Quieres descargar sin conversión a MP3?\n" +
                            "(Se descargará en formato original)")
                        
                        if response:
                            self.use_conversion.set(False)
                        else:
                            self.update_status("Descarga cancelada")
                            return
            
            # Configurar FFmpeg en variables de entorno si es necesario
            ffmpeg_full_path, ffprobe_full_path = self.get_ffmpeg_and_ffprobe_paths()
            original_env = {}
            
            if ffmpeg_full_path and 'imageio_ffmpeg' in ffmpeg_full_path:
                # Guardar variables originales
                original_env['PATH'] = os.environ.get('PATH', '')
                
                # Agregar directorio de imageio-ffmpeg al PATH temporalmente
                ffmpeg_dir = os.path.dirname(ffmpeg_full_path)
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                
                # Crear enlaces simbólicos temporales con nombres estándar
                standard_ffmpeg = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
                standard_ffprobe = os.path.join(ffmpeg_dir, 'ffprobe.exe')
                
                try:
                    if not os.path.exists(standard_ffmpeg):
                        shutil.copy2(ffmpeg_full_path, standard_ffmpeg)
                    
                    if ffprobe_full_path and not os.path.exists(standard_ffprobe):
                        if os.path.exists(ffprobe_full_path):
                            shutil.copy2(ffprobe_full_path, standard_ffprobe)
                except Exception as e:
                    print(f"Error creando copias de FFmpeg: {e}")
            
            # Descargar el video/audio con yt-dlp
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if download_format == 'mp4':
                        self.update_status("📥 Descargando video...")
                    else:
                        self.update_status("📥 Descargando audio...")
                    
                    info = ydl.extract_info(url, download=True)
                    
                    # Obtener información del archivo descargado
                    if info:
                        title = info.get('title', 'Desconocido')
                        duration = info.get('duration', 0)
                        uploader = info.get('uploader', 'Desconocido')
                        
                        info_text = f"Título: {title}\n"
                        info_text += f"Duración: {self.format_duration(duration)}\n"
                        info_text += f"Canal: {uploader}\n"
                        
                        if download_format == 'mp4':
                            info_text += f"Formato: Video MP4"
                        else:
                            info_text += f"Formato: Audio MP3"
                        
                        self.update_info(info_text)
            finally:
                # Restaurar variables de entorno
                if original_env:
                    if 'PATH' in original_env:
                        os.environ['PATH'] = original_env['PATH']
            
            self.progress['value'] = 100
            self.percent_label.config(text="¡Completado!")
            
            self.update_status("¡Descarga completada!")
            
            # Mensaje personalizado según el formato
            if download_format == 'mp4':
                messagebox.showinfo("¡Listo!", f"Su video se descargó correctamente.\n\nLo puede encontrar en:\n{self.download_path.get()}")
            else:
                messagebox.showinfo("¡Listo!", f"Su música se descargó correctamente.\n\nLa puede encontrar en:\n{self.download_path.get()}")
            
        except Exception as e:
            error_msg = str(e)
            
            # Manejo específico de errores de FFmpeg
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                self.update_status("Error: FFmpeg no encontrado")
                response = messagebox.askyesno("Error FFmpeg", 
                    "FFmpeg no está instalado o no se encuentra.\n\n" +
                    "¿Quieres descargar sin conversión a MP3?\n" +
                    "(Se descargará en formato original)")
                
                if response:
                    # Reintentar sin conversión
                    self.use_conversion.set(False)
                    self.download_audio(url)
                    return
                else:
                    messagebox.showinfo("Instalación FFmpeg", 
                        "Para instalar FFmpeg:\n\n" +
                        "1. Haz clic en 'Instalar FFmpeg'\n" +
                        "2. O descarga desde: https://ffmpeg.org/download.html\n" +
                        "3. Agrega FFmpeg al PATH del sistema")
            else:
                self.update_status("Error en la descarga")
                messagebox.showerror("Error", f"Error durante la descarga: {error_msg}")
        
        finally:
            self.progress.stop()
            self.download_btn.config(state=tk.NORMAL)
    
    def format_duration(self, seconds):
        if not seconds:
            return "N/A"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def detect_playlist(self, url):
        """Detecta si la URL contiene una playlist"""
        playlist_indicators = [
            'list=', 'playlist?list=', '&list=',
            'watch?v=', '&start_radio=1',
            'mix', 'radio'
        ]
        
        url_lower = url.lower()
        has_video = 'watch?v=' in url_lower or 'youtu.be/' in url_lower
        has_playlist = any(indicator in url_lower for indicator in ['list=', '&list=', 'start_radio=1'])
        
        return has_video and has_playlist
    
    def ask_playlist_preference(self, url):
        """Pregunta al usuario si quiere descargar solo el video o toda la playlist"""
        if self.detect_playlist(url):
            response = messagebox.askyesnocancel(
                "🎵 Playlist Detectada",
                "Esta URL contiene una playlist o mix de YouTube.\n\n" +
                "¿Qué quieres descargar?\n\n" +
                "✅ SÍ = Solo el video actual (recomendado)\n" +
                "❌ NO = Toda la playlist\n" +
                "🚫 Cancelar = Cancelar descarga"
            )
            
            if response is None:  # Cancelar
                return None
            elif response:  # Solo video actual
                return True
            else:  # Toda la playlist
                return False
        
        return True  # Por defecto, solo el video
    
    def check_updates(self):
        """Verifica si hay actualizaciones disponibles"""
        if not UPDATER_AVAILABLE:
            messagebox.showinfo("Actualizador no disponible", 
                              "El módulo de actualización no está configurado")
            return
        
        def check_in_thread():
            try:
                self.update_status("🔍 Verificando actualizaciones...")
                
                checker = UpdateChecker(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
                update_info = checker.check_for_updates()
                
                if update_info.get('error'):
                    messagebox.showerror("Error", 
                                       f"No se pudo verificar actualizaciones:\n{update_info['error']}")
                    self.update_status("Listo para descargar")
                    
                elif update_info.get('available'):
                    # Hay actualización disponible
                    response = messagebox.askyesno(
                        "✨ Actualización Disponible",
                        f"¡Nueva versión disponible!\n\n" +
                        f"Versión actual: {update_info['current_version']}\n" +
                        f"Nueva versión: {update_info['version']}\n\n" +
                        f"¿Deseas descargar e instalar la actualización?"
                    )
                    
                    if response:
                        self.download_and_install_update(checker, update_info)
                    else:
                        self.update_status("Listo para descargar")
                else:
                    messagebox.showinfo("Sin Actualizaciones", 
                                      f"✅ Ya tienes la última versión ({CURRENT_VERSION})")
                    self.update_status("Listo para descargar")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error verificando actualizaciones:\n{str(e)}")
                self.update_status("Listo para descargar")
        
        thread = threading.Thread(target=check_in_thread)
        thread.daemon = True
        thread.start()
    
    def download_and_install_update(self, checker, update_info):
        """Descarga e instala una actualización"""
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                messagebox.showerror("Error", "No se encontró el archivo de actualización")
                return
            
            self.update_status("📥 Descargando actualización...")
            self.progress.configure(mode='determinate')
            self.progress['value'] = 0
            
            # Callback para actualizar progreso
            def progress_callback(percent, downloaded, total):
                self.progress['value'] = percent
                size_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                self.update_status(f"📥 Descargando: {size_mb:.1f} / {total_mb:.1f} MB ({percent:.0f}%)")
                self.root.update_idletasks()
            
            # Descargar actualización
            update_file = checker.download_update(download_url, progress_callback)
            
            if update_file:
                self.progress['value'] = 100
                self.update_status("✅ Descarga completa, instalando...")
                
                response = messagebox.askyesno(
                    "Instalar Actualización",
                    "La actualización se ha descargado correctamente.\n\n" +
                    "La aplicación se cerrará y se actualizará automáticamente.\n" +
                    "¿Continuar?"
                )
                
                if response:
                    # Instalar y reiniciar
                    if checker.install_update(update_file):
                        # Cerrar la aplicación (el script de actualización la reiniciará)
                        self.root.quit()
                    else:
                        messagebox.showerror("Error", "No se pudo instalar la actualización")
                        self.update_status("Listo para descargar")
            else:
                messagebox.showerror("Error", "No se pudo descargar la actualización")
                self.update_status("Listo para descargar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error instalando actualización:\n{str(e)}")
            self.update_status("Listo para descargar")
        finally:
            self.progress.configure(mode='indeterminate')

def main():
    root = tk.Tk()
    
    # Configurar icono de ventana (opcional)
    try:
        root.iconbitmap(default='assets/icon.ico')
    except:
        pass  # Si no existe el icono, continuar sin él
    
    app = YouTubeMusicDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()