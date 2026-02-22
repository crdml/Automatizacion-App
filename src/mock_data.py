# ==========================================
# DATOS DE PRUEBA (MOCK) - NOMBRES REALES DE BD
# ==========================================

DATOS_MOCK = {
    # CLIENTE
    'RUT_COM': '11111111',
    'DV_COM': '1',

    # VEHÍCULO
    'TIPO_VEHICULO': 'AUTOMOVIL',
    'MARCA': 'TOYOTA',
    'MODELO': 'YARIS',
    'ANNO': '2023',
    'NOT_PATENTE': 'ABCD12',
    'MOTOR': 'MOTOR123',
    'CHASIS': 'CHASIS456',
    'COMUNA_PERMISO': 'VINA DEL MAR', # Reemplazar si tienes otra columna en BD
    'ANNO_PERMISO': '2024',
    'COD_SII': '12345',
    'PRECIO_VENTA': 5000000,
    'TASACION': 4500000,

    # IDENTIFICACIÓN DEL TRÁMITE
    'NUM_FOL': '1540',
    'AN_PROC': '2024',

    # VENDEDOR
    'RUT_VEN': '22222222-2',
    'AP_PATERNO_VEN': 'GONZALEZ', # Se usa como Razón Social si es empresa
    'AP_MATERNO_VEN': 'TAPIA',
    'NOMBRES_VEN': 'MARIA',
    'CALLE_VEN': 'AV SIEMPRE VIVA',
    'NRO_CALLE_VEN': '1',
    'COMUNA_VEN': 'QUILPUE',
    'TELEFONO_VEN': '987654321',

    # COMPRADOR
    'APPATERNO_COM': 'AUTOMOTORA LIMITADA', # Se usa como Razón Social si es empresa
    'APMATERNO_COM': '',
    'NOMBRES_COM': '',
    'CALLE_COM': 'CALLE EMPRESA',
    'NRO_CALLE_COM': '2',
    'COMUNA_COM': 'VILLA ALEMANA',
    'TELEFONO_COM': '999888777'
}