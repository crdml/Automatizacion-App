# 🤖 Automatizacion-App - Asistente Notarial (TGR F23)

Aplicación de escritorio desarrollada en Python y PySide6 para automatizar el llenado del **Formulario 23 (F23)** en el portal de la Tesorería General de la República (TGR).

Esta herramienta actúa como un puente entre la base de datos local de la notaría (MySQL) y el formulario web, permitiendo la inyección automática de datos para agilizar trámites y reducir errores humanos. Diseñada para ser ligera y compatible con equipos antiguos.

## 🚀 Características Principales

- **Conexión Directa a BD:** Extrae automáticamente los datos desde MySQL.
- **Inyección Inteligente:** Rellena los campos del formulario web TGR (RUTs, Montos, Vehículos, etc.) mediante inyección de JavaScript.
- **Navegador Integrado:** Utiliza un motor Chromium (QtWebEngine) para visualizar, descargar PDFs y finalizar el trámite sin salir de la app.
- **Modo Offline (Mocking):** Incluye un sistema de datos de prueba para desarrollo y testeo sin necesidad de conexión a la BD real.
- **Compilación Nativa:** Utiliza Nuitka para generar un ejecutable `.exe` nativo en C, optimizando la velocidad y evitando bloqueos de antivirus en Windows 10/11.

## 🛠️ Requisitos del Sistema

- **Sistema Operativo:** Windows 10/11 de 64 bits. (Requiere Visual C++ Redistributable instalado).
- **Base de Datos:** Acceso a servidor MySQL/MariaDB en red local.
- **Dependencias:** Python 3.10+ (para desarrollo).

## 📦 Instalación (Para Desarrolladores)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/crdml/Automatizacion-App.git
   cd Automatizacion-App

2. **Crear entorno virtual (Opcional pero recomendado):**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt

## ▶️ Uso y Ejecución

### Modo Desarrollo

Para correr la aplicación directamente desde el código fuente y probar cambios:

```bash
python src/asistente_tgr.py

```

### Generar Ejecutable (.exe) para Producción

Para crear el archivo portable para los computadores de la notaría, utilizamos Nuitka. Ejecuta el siguiente comando en tu terminal:

```bash
python -m nuitka --standalone --onefile --enable-plugin=pyside6 --windows-disable-console src/asistente_tgr.py

```

*(Nota: La compilación puede tardar varios minutos ya que traduce el código a C).*

El archivo final `asistente_tgr.exe` aparecerá en la raíz de tu proyecto. Solo necesitas copiar este archivo a los equipos.

## 📂 Estructura del Proyecto

```text
Automatizacion-App/
├── src/
│   ├── asistente_tgr.py   # Código fuente principal y navegador personalizado
│   └── mock_data.py       # Datos de prueba para modo offline
├── .gitignore             # Configuración de exclusiones de Git
├── requirements.txt       # Lista de librerías necesarias (incluye Nuitka)
└── README.md              # Documentación del proyecto

```

## 📄 Licencia

Desarrollado por **Francisca Cardemil** para uso interno.
