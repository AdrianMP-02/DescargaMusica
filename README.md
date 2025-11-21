# YouTube Music Downloader

Una aplicación de escritorio simple y elegante para descargar música de YouTube en formato MP3.

## Características

- 🎵 Descarga audio de YouTube en formato MP3
- 🖥️ Interfaz gráfica simple e intuitiva
- 📁 Selección personalizada de carpeta de descarga
- ℹ️ Información detallada del video antes de descargar
- 🔄 Barra de progreso visual
- ⚡ Procesamiento en segundo plano

## Requisitos del Sistema

- Windows 10/11 (o cualquier sistema compatible con Python)
- Python 3.8 o superior
- Conexión a Internet

## Instalación y Uso

### 🚀 MÉTODO FÁCIL (Para principiantes y personas mayores)

**¡Solo 2 pasos!**

1. **Instalar Python** (solo la primera vez):
   - Descargar de: https://www.python.org/downloads/
   - ⚠️ **IMPORTANTE**: Marcar "Add Python to PATH" durante la instalación

2. **Instalar y usar el programa**:
   - Hacer doble clic en `instalar.bat` (esperar a que termine)
   - Usar `ejecutar.bat` para abrir el programa
   - 🎵 ¡Listo para descargar música!

📄 **Ver `README_INSTALACION.txt` para instrucciones más detalladas**

### 💻 MÉTODO TÉCNICO (Para desarrolladores)

1. **Clonar o descargar el proyecto**
```bash
git clone <repository-url>
cd DescargaMusica
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**
```bash
python main.py
```

### 📦 CREAR EJECUTABLE (Opcional)

Para crear un archivo .exe que no necesite instalación:
```bash
# Hacer doble clic en:
crear_ejecutable.bat
```

## Uso de la Aplicación

1. **Pegar URL**: Copia la URL del video de YouTube que quieres descargar
2. **Seleccionar carpeta**: Elige dónde guardar el archivo MP3 (por defecto: Descargas)
3. **Descargar**: Haz clic en "Descargar MP3" y espera a que termine
4. **Listo**: El archivo MP3 se guardará en la carpeta seleccionada

## Crear Ejecutable (Opcional)

Para crear un archivo ejecutable independiente:

### Instalar PyInstaller

```bash
pip install pyinstaller
```

### Crear ejecutable

```bash
# Ejecutable simple
pyinstaller --onefile --windowed main.py

# Ejecutable con icono personalizado (opcional)
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

El ejecutable se creará en la carpeta `dist/`.

## Estructura del Proyecto

```
DescargaMusica/
│
├── main.py              # Archivo principal de la aplicación
├── requirements.txt     # Dependencias de Python
├── README.md           # Este archivo
├── .github/
│   └── copilot-instructions.md  # Instrucciones para GitHub Copilot
│
├── assets/             # Recursos (iconos, imágenes)
│   └── icon.ico        # Icono de la aplicación (opcional)
│
└── dist/               # Ejecutables generados (después de usar PyInstaller)
```

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación principal
- **Tkinter**: Interfaz gráfica de usuario (incluido con Python)
- **yt-dlp**: Biblioteca para descargar contenido de YouTube
- **Threading**: Para procesamiento en segundo plano

## Solución de Problemas

### Error: "No se puede descargar el video"

- Verifica que la URL sea correcta y el video sea público
- Algunos videos pueden tener restricciones de descarga
- Asegúrate de tener conexión a Internet estable

### Error: "FFmpeg no encontrado"

Este error aparece cuando intentas convertir audio a MP3. Tienes varias opciones:

**Opción 1: Instalación automática (más fácil)**
1. Haz clic en el botón "Instalar FFmpeg" en la aplicación
2. Espera a que termine la instalación
3. Reinicia la aplicación

**Opción 2: Descargar sin conversión**
1. Desmarca la opción "Convertir a MP3" en la aplicación
2. El audio se descargará en su formato original (generalmente M4A)

**Opción 3: Instalación manual**
1. Descarga FFmpeg desde: https://ffmpeg.org/download.html
2. Extrae el archivo y agrega la carpeta `bin` al PATH del sistema
3. Reinicia la aplicación

**Opción 4: Actualizar dependencias**
```bash
pip install --upgrade yt-dlp[default]
```

### La aplicación no inicia

- Verifica que Python esté instalado correctamente
- Asegúrate de haber instalado las dependencias: `pip install -r requirements.txt`
- Ejecuta desde la terminal para ver mensajes de error

## Características Avanzadas

- **Calidad de audio**: El audio se descarga en calidad 192 kbps MP3
- **Información del video**: Muestra título, canal, duración y descripción
- **Interfaz responsive**: Se adapta al tamaño de la ventana
- **Manejo de errores**: Mensajes informativos para diferentes tipos de errores

## Notas Importantes

- Esta aplicación es solo para uso personal y educativo
- Respeta los derechos de autor y términos de servicio de YouTube
- No uses esta herramienta para descargar contenido protegido por derechos de autor

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para la comunidad**