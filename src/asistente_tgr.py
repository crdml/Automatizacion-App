# ==============================================================================
# Automatizacion-App - Asistente Notarial (TGR F23)
# Desarrollado por Francisca Cardemil para uso interno.
# ==============================================================================

import sys
import json
import os
import mysql.connector

# --- PARCHE PARA PYINSTALLER ---
import mysql.connector.locales.eng.client_error
import mysql.connector.plugins.mysql_native_password
import mysql.connector.plugins.caching_sha2_password
# -------------------------------

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QMessageBox, QLabel, QLineEdit, QFileDialog)
from PySide6.QtGui import QIntValidator
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtCore import QUrl

# Importar los datos de prueba
try:
    from mock_data import DATOS_MOCK
except ImportError:
    DATOS_MOCK = {}

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

MODO_TESTING = False

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'ejemplo'
}

# DATOS FIJOS DEL NOTARIO
DATOS_NOTARIO = {
    'L23': '59898765',       
    'L21': 'PEÑA',        
    'L22': 'PEREZ',         
    'L25': 'ELIANA',          
    'L26': 'ARLEGUI',         
    'L29': '3225965',       
    'L28': 'VINA DEL MAR'     
}

# CONSULTA SQL 
QUERY_SQL = """
SELECT 
    RUT_COM, DV_COM, 
    TIPO_VEHICULO, MARCA, MODELO, ANO, PATENTE, MOTOR, CHASIS, ANNO_PERMISO, COD_SII, PRECIO_VENTA, TASACION, CIUDAD_PERMISO,
    NUM_FOL, AN_PROC,
    RUT_VEN, DV_VEN, APPATERNO_VEN, APMATERNO_VEN, NOMBRES_VEN, CALLE_VEN, NRO_CALLE_VEN, TELEFONO_VEN, COMUNA_VEN,
    APPATERNO_COM, APMATERNO_COM, NOMBRES_COM, CALLE_COM, NRO_CALLE_COM, TELEFONO_COM, COMUNA_COM
FROM not_patente 
WHERE NUM_FOL = %s AND AN_PROC = %s
LIMIT 1
"""

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def limpiar_dato(valor):
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()

# ==========================================
# CLASE NAVEGADOR PERSONALIZADO (NUEVO)
# ==========================================
class NavegadorTGR(QWebEngineView):
    def createWindow(self, windowType):
        # Esta es la magia: Si la TGR intenta abrir una pestaña nueva (ej: para pagar),
        # le decimos que la abra en esta misma ventana para no perderla.
        return self

# ==========================================
# LÓGICA DE LA APLICACIÓN
# ==========================================

class AsistenteTGR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asistente Notaría -> TGR (F23 Directo)")
        self.resize(1280, 800)

        layout = QVBoxLayout()

        # --- PANEL DE BÚSQUEDA ---
        search_layout = QHBoxLayout()
        validador_numeros = QIntValidator()
        
        label_folio = QLabel("<b>N° Folio:</b>")
        label_folio.setStyleSheet("color: white; font-size: 14px;")
        
        self.input_repertorio = QLineEdit()
        self.input_repertorio.setPlaceholderText("N° Folio (Ej: 1540)")
        self.input_repertorio.setFixedHeight(35)
        self.input_repertorio.setValidator(validador_numeros)
        self.input_repertorio.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        
        label_anio = QLabel("<b>Año:</b>")
        label_anio.setStyleSheet("color: white; font-size: 14px;")
        
        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("Año (Ej: 2024)")
        self.input_anio.setFixedHeight(35)
        self.input_anio.setValidator(validador_numeros)
        self.input_anio.setMaxLength(4)
        self.input_anio.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        self.btn_action = QPushButton("⚡ BUSCAR Y RELLENAR")
        self.btn_action.setFixedHeight(35)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 0 15px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_action.clicked.connect(self.ejecutar_proceso)

        self.btn_nuevo = QPushButton("🔄 NUEVO TRÁMITE")
        self.btn_nuevo.setFixedHeight(35)
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #192A56; color: #C0B9D6; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 0 15px;
            }
            QPushButton:hover { background-color: #0d1630; color: white; }
        """)
        self.btn_nuevo.clicked.connect(self.reiniciar_formulario)

        search_layout.addWidget(label_folio)
        search_layout.addWidget(self.input_repertorio)
        search_layout.addWidget(label_anio)
        search_layout.addWidget(self.input_anio)
        search_layout.addWidget(self.btn_action)
        search_layout.addWidget(self.btn_nuevo)
        search_layout.addStretch()

        layout.addLayout(search_layout)

        # --- ESTADO Y NAVEGADOR ---
        self.status_label = QLabel("Estado: Esperando búsqueda...")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px; color: #f1c40f; font-size: 14px;")
        layout.addWidget(self.status_label)

        # Usamos nuestro nuevo navegador con soporte para pestañas emergentes
        self.browser = NavegadorTGR()
        
        # Habilitamos Pop-ups, Plugins y el Lector de PDFs interno
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        
        # Conectamos el gestor de descargas
        self.browser.page().profile().downloadRequested.connect(self.gestionar_descarga)

        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # --- NUEVA FUNCIÓN: GESTOR DE DESCARGAS ---
    def gestionar_descarga(self, download):
        """Abre la ventana de 'Guardar como...' si la TGR intenta descargar un archivo"""
        ruta_guardado, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Archivo (TGR)", 
            download.downloadFileName()
        )
        if ruta_guardado:
            download.setDownloadDirectory(os.path.dirname(ruta_guardado))
            download.setDownloadFileName(os.path.basename(ruta_guardado))
            download.accept()
            self.status_label.setText("Estado: Archivo descargado con éxito.")

    def reiniciar_formulario(self):
        self.input_repertorio.clear()
        self.input_anio.clear()
        self.status_label.setText("Estado: Cargando nuevo formulario en blanco...")
        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))

    def procesar_reglas_negocio(self, row):
        datos_form = DATOS_NOTARIO.copy()

        datos_form['L03'] = limpiar_dato(row.get('RUT_COM'))
        datos_form['L003'] = limpiar_dato(row.get('DV_COM'))

        datos_form['L34'] = limpiar_dato(row.get('TIPO_VEHICULO'))
        datos_form['L35'] = limpiar_dato(row.get('MARCA'))
        datos_form['L36'] = limpiar_dato(row.get('MODELO'))
        datos_form['L37'] = limpiar_dato(row.get('ANO'))
        datos_form['L12'] = limpiar_dato(row.get('PATENTE')) 
        datos_form['L50'] = limpiar_dato(row.get('MOTOR'))
        datos_form['L51'] = limpiar_dato(row.get('CHASIS'))

        datos_form['L18'] = limpiar_dato(row.get('CIUDAD_PERMISO')) 
        datos_form['L19'] = limpiar_dato(row.get('ANNO_PERMISO'))
        datos_form['L9']  = limpiar_dato(row.get('COD_SII'))
        
        try:
            precio_venta = float(row.get('PRECIO_VENTA') or 0)
            tasacion = float(row.get('TASACION') or 0)
        except ValueError:
            precio_venta, tasacion = 0.0, 0.0
            
        datos_form['L10'] = str(int(precio_venta))
        datos_form['L11'] = str(int(tasacion))

        datos_form['L17'] = limpiar_dato(row.get('NUM_FOL'))
        datos_form['L47'] = limpiar_dato(row.get('AN_PROC')) 

        rut_ven = limpiar_dato(row.get('RUT_VEN'))
        dv_ven = limpiar_dato(row.get('DV_VEN'))
        datos_form['L43'] = f"{rut_ven}-{dv_ven}" if rut_ven and dv_ven else rut_ven
        
        datos_form['L42'] = limpiar_dato(row.get('APPATERNO_VEN')) 
        datos_form['L44'] = limpiar_dato(row.get('APMATERNO_VEN')) 
        datos_form['L45'] = limpiar_dato(row.get('NOMBRES_VEN'))
        
        calle_ven = limpiar_dato(row.get('CALLE_VEN'))
        nro_ven = limpiar_dato(row.get('NRO_CALLE_VEN'))
        datos_form['L32'] = f"{calle_ven} {nro_ven}".strip()
        
        datos_form['L38'] = limpiar_dato(row.get('COMUNA_VEN')) 
        datos_form['L39'] = limpiar_dato(row.get('TELEFONO_VEN'))

        rut_com = limpiar_dato(row.get('RUT_COM'))
        dv_com = limpiar_dato(row.get('DV_COM'))
        datos_form['L33'] = f"{rut_com}-{dv_com}" if rut_com and dv_com else rut_com
        
        datos_form['L61'] = limpiar_dato(row.get('APPATERNO_COM')) 
        datos_form['L62'] = limpiar_dato(row.get('APMATERNO_COM'))
        datos_form['L65'] = limpiar_dato(row.get('NOMBRES_COM'))
        
        calle_com = limpiar_dato(row.get('CALLE_COM'))
        nro_com = limpiar_dato(row.get('NRO_CALLE_COM'))
        datos_form['L46'] = f"{calle_com} {nro_com}".strip()
        
        datos_form['L48'] = limpiar_dato(row.get('COMUNA_COM'))
        datos_form['L49'] = limpiar_dato(row.get('TELEFONO_COM'))

        base_impuesto = max(precio_venta, tasacion)
        derecho_municipal = round(base_impuesto * 0.015)
        
        datos_form['L77'] = str(int(base_impuesto))
        datos_form['L70'] = "" 
        datos_form['L334'] = str(int(derecho_municipal))
        datos_form['L91'] = str(int(derecho_municipal)) 

        return datos_form

    def obtener_datos(self, rep, anio):
        row_db = None
        if MODO_TESTING:
            if rep == '1540' and anio == '2024':
                DATOS_MOCK['NUM_FOL'] = rep
                DATOS_MOCK['AN_PROC'] = anio
                row_db = DATOS_MOCK
            else:
                row_db = None
        else:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                cursor.execute(QUERY_SQL, (rep, anio))
                row_db = cursor.fetchone()
                conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Error BD", f"Error conectando a MySQL:\n{e}")
                return None
        
        if row_db:
            return self.procesar_reglas_negocio(row_db)
        return None

    def ejecutar_proceso(self):
        rep = self.input_repertorio.text().strip()
        anio = self.input_anio.text().strip()

        if not rep or not anio:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingresa el N° Folio y el Año.")
            return
        if len(anio) != 4:
            QMessageBox.warning(self, "Año Inválido", "El año debe tener 4 dígitos.")
            return

        self.status_label.setText(f"Estado: Buscando Folio {rep} del año {anio}...")
        QApplication.processEvents()

        datos = self.obtener_datos(rep, anio)
        if not datos:
            self.status_label.setText("Estado: Trámite no encontrado en la base de datos.")
            QMessageBox.information(self, "No encontrado", f"No se encontró el folio {rep} del año {anio}.")
            return

        self.status_label.setText("Estado: Inyectando datos en el formulario...")
        json_datos = json.dumps(datos)

        js_code = f"""
        (function() {{
            var data = {json_datos};
            var count = 0;
            var log = [];

            for (var key in data) {{
                if (data.hasOwnProperty(key)) {{
                    var campo = document.getElementById(key);
                    if (campo) {{
                        if (campo.readOnly) {{
                            campo.readOnly = false;
                        }}
                        campo.value = data[key];
                        campo.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        campo.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        campo.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                        count++;
                    }} else {{
                        log.push("No encontrado: " + key);
                    }}
                }}
            }}
            
            if (log.length > 0) {{
                console.warn("Campos ignorados o no encontrados en TGR:", log);
            }}

            return count;
        }})();
        """

        self.browser.page().runJavaScript(js_code, self.confirmar_resultado)

    def confirmar_resultado(self, count):
        if count is None:
            QMessageBox.warning(self, "Alerta", "El script no devolvió nada.")
        elif count > 0:
            msg = f"¡Éxito! Se rellenaron {count} campos automáticamente."
            self.status_label.setText(msg)
            QMessageBox.information(self, "Carga Completa", msg)
        else:
            QMessageBox.critical(self, "Error", "No se encontró ningún campo.")

if __name__ == "__main__":
    sys.argv.append("--disable-gpu")
    sys.argv.append("--no-sandbox")
    os.environ["QT_OPENGL"] = "software"

    app = QApplication(sys.argv)
    window = AsistenteTGR()
    window.show()
    sys.exit(app.exec())