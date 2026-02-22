# Variables
PYTHON = python
PIP = pip
MAIN_SCRIPT = src/asistente_tgr.py
APP_NAME = asistente_tgr

.PHONY: help install run build clean

# Muestra la lista de comandos disponibles
help:
	@echo "Comandos disponibles:"
	@echo "  make install  - Instala las dependencias necesarias"
	@echo "  make run      - Ejecuta la aplicacion en modo desarrollo"
	@echo "  make build    - Compila el proyecto en un ejecutable (.exe)"
	@echo "  make clean    - Limpia los archivos temporales y de compilacion"

# Instalar dependencias
install:
	$(PIP) install -r requirements.txt

# Ejecutar en modo desarrollo
run:
	$(PYTHON) $(MAIN_SCRIPT)

# Construir el ejecutable con PyInstaller
build:
	$(PYTHON) -m PyInstaller --noconsole --onefile $(MAIN_SCRIPT)
	@echo "¡Compilación terminada! Revisa la carpeta dist/"

# Limpiar archivos generados (PyCache, build, dist)
clean:
	rm -rf build/ dist/ *.spec src/__pycache__/
	@echo "Archivos temporales eliminados."