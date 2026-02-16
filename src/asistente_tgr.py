import sys
import json
import mysql.connector
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# ==========================================
# CONFIGURACIÓN (EDITAR AQUÍ)
# ==========================================

# 1. Cambia esto a False cuando tengas las credenciales de la BD
MODO_TESTING = False

# 2. Configuración de tu MySQL (cuando MODO_TESTING = False)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PON_AQUI_TU_PASSWORD',
    'database': 'notaria_bd'
}

# 3. Datos falsos para probar que el formulario se llena (cuando MODO_TESTING = True)
DATOS_MOCK = {
    'L03': '11111111',       # RUT Cliente
    'L003': '1',             # DV Cliente
    'L34': 'AUTOMOVIL',      # Tipo Vehículo
    'L35': 'TOYOTA',         # Marca
    'L36': 'YARIS',          # Modelo
    'L37': '2023',           # Año Fab
    'L12': 'ABCD12',         # Patente
    'L50': 'MOTOR123',       # N Motor
    'L51': 'CHASIS456',      # N Chasis
    'L19': '2024',           # Año Permiso
    'L9': '12345',           # Cod SII
    'L10': '5000000',        # Precio Venta
    'L11': '4500000',        # Avalúo
    'L23': '9999999',        # RUT Notario (Cuerpo)
    'L21': 'PEREZ',          # Apellido P Notario
    'L22': 'SOTO',           # Apellido M Notario
    'L25': 'JUAN',           # Nombres Notario
    'L26': 'CALLE FALSA 123',# Dirección Notaría
    'L29': '2222222',        # Teléfono
    'L91': '150000'          # Total a Pagar
}

# 4. LA CONSULTA SQL
# Usamos "AS" para renombrar las columnas de tu BD a los IDs del formulario (L03, L34, etc.)
QUERY_SQL = """
SELECT 
    rut_cliente AS L03,
    dv_cliente AS L003,
    tipo_vehiculo AS L34,
    marca AS L35,
    modelo AS L36,
    anio_fab AS L37,
    patente AS L12,
    num_motor AS L50,
    num_chasis AS L51,
    anio_permiso AS L19,
    cod_sii AS L9,
    precio_venta AS L10,
    avaluo_fiscal AS L11,
    rut_notario_cuerpo AS L23,
    apellido_p_notario AS L21,
    apellido_m_notario AS L22,
    nombres_notario AS L25,
    calle_notaria AS L26,
    fono_notaria AS L29,
    repertorio AS L17,
    causa_rol AS L47,
    rut_vendedor AS L43,
    razon_vendedor AS L42,
    apellido_m_vendedor AS L44,
    nombre_vendedor AS L45,
    calle_vendedor AS L32,
    fono_vendedor AS L39,
    rut_comprador AS L33,
    razon_comprador AS L61,
    apellido_m_comprador AS L62,
    nombre_comprador AS L65,
    calle_comprador AS L46,
    fono_comprador AS L49,
    base_impuesto AS L77,
    descuento AS L70,
    derecho_municipal AS L334,
    total_pagar AS L91
FROM tramites 
ORDER BY id DESC LIMIT 1
"""

# ==========================================
# LÓGICA DE LA APLICACIÓN
# ==========================================

class AsistenteTGR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asistente Notaría -> TGR (F23 Directo)")
        self.resize(1280, 800)

        # Layout Principal
        layout = QVBoxLayout()

        # Panel Superior
        self.status_label = QLabel("Estado: Esperando carga del sitio...")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)

        # Botón de Inyección
        self.btn_action = QPushButton("⚡ RELLENAR FORMULARIO DESDE BD")
        self.btn_action.setFixedHeight(50)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; font-size: 14px; font-weight: bold; border-radius: 5px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_action.clicked.connect(self.ejecutar_proceso)
        layout.addWidget(self.btn_action)

        # Navegador Web
        self.browser = QWebEngineView()
        # AQUI ESTÁ EL CAMBIO CLAVE: Usamos la URL directa
        self.browser.setUrl(QUrl("https://www.tesoreria.cl/IntForm23NotarioWeb/"))
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def obtener_datos(self):
        """Devuelve datos reales o falsos según la configuración"""
        if MODO_TESTING:
            print(">>> USANDO DATOS DE PRUEBA (MOCK)")
            return DATOS_MOCK
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(QUERY_SQL)
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"Error conectando a MySQL:\n{e}")
            return None

    def ejecutar_proceso(self):
        datos = self.obtener_datos()
        if not datos:
            self.status_label.setText("Estado: No hay datos para cargar.")
            return

        self.status_label.setText("Estado: Inyectando datos en el formulario...")
        
        # Convertimos datos a JSON para pasarlos a JavaScript
        json_datos = json.dumps(datos)

        # SCRIPT SIMPLIFICADO: Ahora que estamos en la página directa,
        # no necesitamos buscar en iframes. Usamos acceso directo.
        js_code = f"""
        (function() {{
            var data = {json_datos};
            var count = 0;
            var log = [];

            for (var key in data) {{
                if (data.hasOwnProperty(key)) {{
                    var campo = document.getElementById(key);
                    if (campo) {{
                        campo.value = data[key];
                        // Disparamos eventos para asegurar que la web detecte el cambio
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
                console.warn("Campos faltantes:", log);
            }}

            return count;
        }})();
        """

        # Ejecutamos el script en el navegador
        self.browser.page().runJavaScript(js_code, self.confirmar_resultado)

    def confirmar_resultado(self, count):
        if count is None:
            QMessageBox.warning(self, "Alerta", "El script no devolvió nada. ¿La página terminó de cargar?")
        elif count > 0:
            msg = f"¡Éxito! Se rellenaron {count} campos automáticamente."
            self.status_label.setText(msg)
            QMessageBox.information(self, "Carga Completa", msg)
        else:
            QMessageBox.critical(self, "Error", "No se encontró ningún campo. Verifica que la página sea la correcta.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AsistenteTGR()
    window.show()
    sys.exit(app.exec())