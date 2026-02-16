# 🤖 Automatizacion-App - Asistente Notarial (TGR F23)

Aplicación de escritorio desarrollada en Python y PySide6 para automatizar el llenado del **Formulario 23 (F23)** en el portal de la Tesorería General de la República (TGR).

Esta herramienta actúa como un puente entre la base de datos local de la notaría (MySQL) y el formulario web, permitiendo la inyección automática de datos para agilizar trámites y reducir errores humanos. Diseñada para ser ligera y compatible con equipos antiguos.

## 🚀 Características Principales

- **Conexión Directa a BD:** Extrae automáticamente los datos del último trámite desde MySQL.
- **Inyección Inteligente:** Rellena los campos del formulario web TGR (RUTs, Montos, Vehículos, etc.) mediante inyección de JavaScript.
- **Navegador Integrado:** Utiliza un motor Chromium (QtWebEngine) para visualizar y finalizar el trámite sin salir de la app.
- **Modo Offline (Mocking):** Incluye un sistema de datos de prueba para desarrollo y testeo sin necesidad de conexión a la BD real.
- **Portable:** Compilable a un único archivo `.exe` que no requiere instalación de Python en el cliente.

## 🛠️ Requisitos del Sistema

- **Sistema Operativo:** Windows 10/11 (Compatible con versiones anteriores según soporte de Qt).
- **Base de Datos:** Acceso a servidor MySQL/MariaDB con la tabla de trámites.
- **Dependencias:** Python 3.10+ (para desarrollo).

## 📦 Instalación (Para Desarrolladores)

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/Kirijo-Asistente-Notaria.git](https://github.com/TU_USUARIO/Kirijo-Asistente-Notaria.git)
   cd Kirijo-Asistente-Notaria

2. **Crear entorno virtual (Opcional pero recomendado):**
```bash
python -m venv venv
.\venv\Scripts\activate
```
3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

Para conectar la aplicación a la base de datos real, edita el archivo `src/asistente_tgr.py`.

Busca la variable `DB_CONFIG` y actualiza las credenciales:

```python
# src/asistente_tgr.py

MODO_TESTING = False  # Cambiar a 'True' para pruebas sin base de datos

DB_CONFIG = {
    'host': 'localhost',      # IP del servidor de la notaría
    'user': 'root',           # Usuario MySQL
    'password': 'TU_CLAVE',   # ¡NO SUBIR ESTA CLAVE A GITHUB!
    'database': 'nombre_bd'   # Nombre de la base de datos
}

```

## ▶️ Uso y Ejecución

### Modo Desarrollo

Para correr la aplicación desde el código fuente:

```bash
python src/asistente_tgr.py

```

### Generar Ejecutable (.exe)

Para crear el archivo portable para los computadores de la notaría:

1. Ejecuta el siguiente comando en la terminal:
```bash
python -m PyInstaller --noconsole --onefile src/asistente_tgr.py

```


2. El archivo final **`asistente_tgr.exe`** aparecerá en la carpeta `dist/`. Solo necesitas copiar este archivo a los equipos de destino.

## 📂 Estructura del Proyecto

```text
Kirijo-Asistente-Notaria/
├── src/
│   └── asistente_tgr.py   # Código fuente principal
├── dist/                  # Carpeta donde se genera el .exe (No subir a Git)
├── build/                 # Archivos temporales de compilación (No subir a Git)
├── .gitignore             # Configuración de exclusiones de Git
├── requirements.txt       # Lista de librerías necesarias
└── README.md              # Documentación del proyecto

```

## 📄 Licencia

Desarrollado por **Francisca Cardemil** para uso interno.
