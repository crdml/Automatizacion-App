# ==============================================================================
# Automatizacion-App - Asistente Notarial (TGR F23)
# Desarrollado por Francisca Cardemil para uso interno.
# ==============================================================================

import sys
import json
import os
import mysql.connector
from dotenv import load_dotenv
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QMessageBox, QLabel, QLineEdit)
from PySide6.QtGui import QIntValidator
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# Importar los datos de prueba
try:
    from mock_data import DATOS_MOCK
except ImportError:
    DATOS_MOCK = {}

# Cargar las variables del archivo .env
load_dotenv()

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

# MODO_TESTING = True  -> Usa los datos falsos de mock_data.py.
# MODO_TESTING = False -> Se conecta a la base de datos MySQL real.
MODO_TESTING = False

# La configuración viene del archivo .env
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# DATOS FIJOS DEL NOTARIO
DATOS_NOTARIO = {
    'L23': '5920860-8',       
    'L21': 'GERVASIO',        
    'L22': 'ZAMUDIO',         
    'L25': 'ELIANA',          
    'L26': 'ARLEGUI',         
    'L29': '322186925',       
    'L28': 'VINA DEL MAR'     
}

# CONSULTA SQL
QUERY_SQL = """
SELECT 
    RUT_COM, DV_COM, 
    TIPO_VEHICULO, MARCA, MODELO, ANO, PATENTE, MOTOR, CHASIS, ANNO_PERMISO, COD_SII, PRECIO_VENTA, TASACION,
    NUM_FOL, AN_PROC,
    RUT_VEN, APPATERNO_VEN, APMATERNO_VEN, NOMBRES_VEN, CALLE_VEN, NRO_CALLE_VEN, TELEFONO_VEN,
    APPATERNO_COM, APMATERNO_COM, NOMBRES_COM, CALLE_COM, NRO_CALLE_COM, TELEFONO_COM
FROM not_patente 
WHERE NUM_FOL = %s AND AN_PROC = %s
LIMIT 1
"""

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
                background-color: #C0B9D6; color: #192A56; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 0 15px;
            }
            QPushButton:hover { background-color: #a8a0c0; color: #0d1630; }
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

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def reiniciar_formulario(self):
        """Limpia las cajas de texto y recarga la web original de la TGR"""
        self.input_repertorio.clear()
        self.input_anio.clear()
        self.status_label.setText("Estado: Cargando nuevo formulario en blanco...")
        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))

    def procesar_reglas_negocio(self, row):
        datos_form = DATOS_NOTARIO.copy()

        datos_form['L03'] = str(row.get('RUT_COM', ''))
        datos_form['L003'] = str(row.get('DV_COM', ''))

        datos_form['L34'] = str(row.get('TIPO_VEHICULO', ''))
        datos_form['L35'] = str(row.get('MARCA', ''))
        datos_form['L36'] = str(row.get('MODELO', ''))
        datos_form['L37'] = str(row.get('ANO', ''))
        datos_form['L12'] = str(row.get('NOT_PATENTE', ''))
        datos_form['L50'] = str(row.get('MOTOR', ''))
        datos_form['L51'] = str(row.get('CHASIS', ''))

        datos_form['L18'] = str(row.get('COMUNA_PERMISO', '')) 
        datos_form['L19'] = str(row.get('ANNO_PERMISO', ''))
        datos_form['L9']  = str(row.get('COD_SII', ''))
        
        try:
            precio_venta = float(row.get('PRECIO_VENTA', 0))
            tasacion = float(row.get('TASACION', 0))
        except ValueError:
            precio_venta, tasacion = 0.0, 0.0
            
        datos_form['L10'] = str(int(precio_venta))
        datos_form['L11'] = str(int(tasacion))

        datos_form['L17'] = str(row.get('NUM_FOL', ''))
        datos_form['L47'] = str(row.get('AN_PROC', '')) 

        datos_form['L43'] = str(row.get('RUT_VEN', '')) 
        datos_form['L42'] = str(row.get('AP_PATERNO_VEN', ''))
        datos_form['L44'] = str(row.get('AP_MATERNO_VEN', ''))
        datos_form['L45'] = str(row.get('NOMBRES_VEN', ''))
        
        calle_ven = str(row.get('CALLE_VEN', ''))
        nro_ven = str(row.get('NRO_CALLE_VEN', ''))
        datos_form['L32'] = f"{calle_ven} {nro_ven}".strip()
        
        datos_form['L38'] = str(row.get('COMUNA_VEN', '')) 
        datos_form['L39'] = str(row.get('TELEFONO_VEN', ''))

        rut_com = str(row.get('RUT_COM', ''))
        dv_com = str(row.get('DV_COM', ''))
        datos_form['L33'] = f"{rut_com}-{dv_com}" if rut_com and dv_com else rut_com
        
        datos_form['L61'] = str(row.get('APPATERNO_COM', '')) 
        datos_form['L62'] = str(row.get('APMATERNO_COM', ''))
        datos_form['L65'] = str(row.get('NOMBRES_COM', ''))
        
        calle_com = str(row.get('CALLE_COM', ''))
        nro_com = str(row.get('NRO_CALLE_COM', ''))
        datos_form['L46'] = f"{calle_com} {nro_com}".strip()
        
        datos_form['L48'] = str(row.get('COMUNA_COM', ''))
        datos_form['L49'] = str(row.get('TELEFONO_COM', ''))

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
    app = QApplication(sys.argv)
    window = AsistenteTGR()
    window.show()
    sys.exit(app.exec())