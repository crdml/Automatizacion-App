import sys
import json
import mysql.connector
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QMessageBox, QLabel, QLineEdit)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# ==========================================
# CONFIGURACIÓN (EDITAR AQUÍ)
# ==========================================

MODO_TESTING = True  # Cambia a False para conectar a tu MySQL real

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PON_AQUI_TU_PASSWORD',
    'database': 'notaria_bd'
}

# DATOS FIJOS DEL NOTARIO
DATOS_NOTARIO = {
    'L23': '9999999-9',       
    'L21': 'PEREZ',           
    'L22': 'SOTO',            
    'L25': 'JUAN',            
    'L26': 'CALLE FALSA 123', 
    'L29': '2222222',         
    'L28': 'VALPARAISO'       
}

DATOS_MOCK = {
    'rut_cliente': '11111111', 'dv_cliente': '1',
    'tipo_vehiculo': 'AUTOMOVIL', 'marca': 'TOYOTA', 'modelo': 'YARIS', 'anio_fab': '2023',
    'patente': 'ABCD12', 'num_motor': 'MOTOR123', 'num_chasis': 'CHASIS456', 
    'comuna_permiso': 'VINA DEL MAR', 'anio_permiso': '2024',
    'cod_sii': '12345',
    'precio_venta': 5000000, 
    'avaluo_fiscal': 4500000,
    
    'numero_repertorio': '1540', 'anio_repertorio': '2024',
    
    'rut_vendedor': '22222222', 'dv_vendedor': '2',
    'razon_vendedor': '', 
    'apellido_p_vendedor': 'GONZALEZ', 'apellido_m_vendedor': 'TAPIA', 'nombre_vendedor': 'MARIA',
    'calle_vendedor': 'AV SIEMPRE VIVA 1', 'comuna_vendedor': 'QUILPUE', 'fono_vendedor': '987654321',
    
    'rut_comprador': '77777777', 'dv_comprador': '7',
    'razon_comprador': 'AUTOMOTORA LIMITADA',
    'apellido_p_comprador': '', 'apellido_m_comprador': '', 'nombre_comprador': '',
    'calle_comprador': 'CALLE EMPRESA 2', 'comuna_comprador': 'VILLA ALEMANA', 'fono_comprador': '999888777'
}

# LA CONSULTA SQL ACTUALIZADA PARA BUSCAR POR REPERTORIO Y AÑO
QUERY_SQL = """
SELECT 
    rut_cliente, dv_cliente,
    tipo_vehiculo, marca, modelo, anio_fab, patente, num_motor, num_chasis, comuna_permiso, anio_permiso, cod_sii,
    precio_venta, avaluo_fiscal,
    numero_repertorio, anio_repertorio,
    rut_vendedor, dv_vendedor, razon_vendedor, apellido_p_vendedor, apellido_m_vendedor, nombre_vendedor, calle_vendedor, comuna_vendedor, fono_vendedor,
    rut_comprador, dv_comprador, razon_comprador, apellido_p_comprador, apellido_m_comprador, nombre_comprador, calle_comprador, comuna_comprador, fono_comprador
FROM tramites 
WHERE numero_repertorio = %s AND anio_repertorio = %s
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
        
        self.input_repertorio = QLineEdit()
        self.input_repertorio.setPlaceholderText("N° Repertorio (Ej: 1540)")
        self.input_repertorio.setFixedHeight(35)
        
        self.input_anio = QLineEdit()
        self.input_anio.setPlaceholderText("Año (Ej: 2024)")
        self.input_anio.setFixedHeight(35)

        self.btn_action = QPushButton("⚡ BUSCAR EN BD Y RELLENAR")
        self.btn_action.setFixedHeight(35)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 0 15px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_action.clicked.connect(self.ejecutar_proceso)

        search_layout.addWidget(QLabel("<b>Repertorio:</b>"))
        search_layout.addWidget(self.input_repertorio)
        search_layout.addWidget(QLabel("<b>Año:</b>"))
        search_layout.addWidget(self.input_anio)
        search_layout.addWidget(self.btn_action)
        search_layout.addStretch() # Empuja todo a la izquierda

        layout.addLayout(search_layout)

        # --- ESTADO Y NAVEGADOR ---
        self.status_label = QLabel("Estado: Esperando búsqueda...")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px; color: #333;")
        layout.addWidget(self.status_label)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def procesar_reglas_negocio(self, row):
        """Mapea los datos de la base de datos exactamente a los IDs del HTML"""
        datos_form = DATOS_NOTARIO.copy()

        # RUT Cliente
        datos_form['L03'] = str(row.get('rut_cliente', ''))
        datos_form['L003'] = str(row.get('dv_cliente', ''))

        # Repertorio e Identificación
        datos_form['L17'] = str(row.get('numero_repertorio', ''))
        datos_form['L47'] = str(row.get('anio_repertorio', '')) 

        # VENDEDOR
        datos_form['L43'] = f"{row.get('rut_vendedor', '')}-{row.get('dv_vendedor', '')}"
        if row.get('razon_vendedor') and str(row.get('razon_vendedor')).strip():
            datos_form['L42'] = str(row.get('razon_vendedor'))
        else:
            datos_form['L42'] = str(row.get('apellido_p_vendedor', ''))
        
        datos_form['L44'] = str(row.get('apellido_m_vendedor', ''))
        datos_form['L45'] = str(row.get('nombre_vendedor', ''))
        datos_form['L32'] = str(row.get('calle_vendedor', ''))
        datos_form['L38'] = str(row.get('comuna_vendedor', '')) 
        datos_form['L39'] = str(row.get('fono_vendedor', ''))

        # COMPRADOR
        datos_form['L33'] = f"{row.get('rut_comprador', '')}-{row.get('dv_comprador', '')}"
        if row.get('razon_comprador') and str(row.get('razon_comprador')).strip():
            datos_form['L61'] = str(row.get('razon_comprador'))
        else:
            datos_form['L61'] = str(row.get('apellido_p_comprador', ''))
            
        datos_form['L62'] = str(row.get('apellido_m_comprador', ''))
        datos_form['L65'] = str(row.get('nombre_comprador', ''))
        datos_form['L46'] = str(row.get('calle_comprador', ''))
        datos_form['L48'] = str(row.get('comuna_comprador', ''))
        datos_form['L49'] = str(row.get('fono_comprador', ''))

        # Cálculos de Impuestos
        try:
            precio_venta = float(row.get('precio_venta', 0))
            avaluo = float(row.get('avaluo_fiscal', 0))
            base_impuesto = max(precio_venta, avaluo)
            derecho_municipal = round(base_impuesto * 0.015)
            
            datos_form['L10'] = str(int(precio_venta))
            datos_form['L11'] = str(int(avaluo))
            datos_form['L77'] = str(int(base_impuesto))
            datos_form['L334'] = str(int(derecho_municipal))
            datos_form['L91'] = str(int(derecho_municipal)) 
        except ValueError:
            pass 

        # Datos del Vehículo
        datos_form['L34'] = str(row.get('tipo_vehiculo', ''))
        datos_form['L35'] = str(row.get('marca', ''))
        datos_form['L36'] = str(row.get('modelo', ''))
        datos_form['L37'] = str(row.get('anio_fab', ''))
        datos_form['L12'] = str(row.get('patente', ''))
        datos_form['L50'] = str(row.get('num_motor', ''))
        datos_form['L51'] = str(row.get('num_chasis', ''))
        datos_form['L18'] = str(row.get('comuna_permiso', '')) 
        datos_form['L19'] = str(row.get('anio_permiso', ''))
        datos_form['L9']  = str(row.get('cod_sii', ''))

        return datos_form

    def obtener_datos(self, rep, anio):
        row_db = None
        if MODO_TESTING:
            print(f">>> USANDO DATOS DE PRUEBA (Buscando Rep: {rep} - Año: {anio})")
            # En modo testing devolvemos el mock solo si coincide (o siempre, para probar)
            # Aquí lo forzamos a actualizar el mock con lo que escribiste para simular la búsqueda
            DATOS_MOCK['numero_repertorio'] = rep
            DATOS_MOCK['anio_repertorio'] = anio
            row_db = DATOS_MOCK
        else:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                # Ejecutamos la consulta pasando los parámetros de forma segura
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
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingresa el Número de Repertorio y el Año.")
            return

        self.status_label.setText(f"Estado: Buscando Repertorio {rep} del año {anio}...")
        QApplication.processEvents() # Fuerza a la interfaz a actualizar el texto

        datos = self.obtener_datos(rep, anio)
        if not datos:
            self.status_label.setText("Estado: Trámite no encontrado en la base de datos.")
            QMessageBox.information(self, "No encontrado", f"No se encontró el repertorio {rep} del año {anio}.")
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