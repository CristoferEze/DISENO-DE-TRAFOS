# -*- coding: utf-8 -*-
# ==================================================================
# CONSTANTES Y BASES DE DATOS DEL DISEÑO
# Fuente: Guía de Diseño de Transformadores (Revisada)
# ==================================================================

# --- NUEVO: Conexiones Normalizadas (para futura validación en la UI) ---
conexiones_normalizadas_db = [
    'Dyn1', 'Dy0', 'Ynd5', 'Ynd11', 'Ynyn6', 'Dd6',
    'Dyn5', 'Yd1', 'Yd7', 'Yy0', 'Dd0', 'Dd8',
    'Dyn7', 'Ynd1', 'Ynd7', 'Ynyn0', 'Dd2', 'Dd10',
    'Dyn11', 'Yd5', 'Yd11', 'Yy6', 'Dd4'
]

# --- AMPLIADO: Base de datos de Acero Eléctrico al Silicio ---
# Ahora incluye espesor y una referencia directa a la merma para mayor claridad.
acero_electrico_db = {
    '35M6': {'espesor_mm': 0.35, 'fa': 0.975, 'merma': 'Merma 2.5% (35M6)'},
    '30M5': {'espesor_mm': 0.30, 'fa': 0.970, 'merma': 'Merma 3.0% (30M5)'},
    '27M4': {'espesor_mm': 0.27, 'fa': 0.965, 'merma': 'Merma 3.5% (27M4)'},
    '23M3': {'espesor_mm': 0.23, 'fa': 0.960, 'merma': 'Merma 4.0% (23M3)'}
}

# --- AMPLIADO: Coeficiente de Plenitud del Hierro (Kr) ---
# Base de datos completada según la tabla 2.3 de la guía.
coeficiente_kr_db = {
    'Sin merma': {
        1: {5: 0.637}, 2: {15: 0.787}, 3: {50: 0.851}, 
        4: {200: 0.887}, 5: {500: 0.908}, 6: {750: 0.924}
    },
    'Merma 2.5% (35M6)': {
        1: {5: 0.621}, 2: {15: 0.767}, 3: {50: 0.830}, 
        4: {200: 0.865}, 5: {500: 0.885}, 6: {750: 0.900}
    },
    'Merma 3.0% (30M5)': {
        1: {5: 0.618}, 2: {15: 0.763}, 3: {50: 0.825}, 
        4: {200: 0.860}, 5: {500: 0.881}, 6: {750: 0.896}
    },
    'Merma 3.5% (27M4)': {
        1: {5: 0.615}, 2: {15: 0.759}, 3: {50: 0.821}, 
        4: {200: 0.856}, 5: {500: 0.876}, 6: {750: 0.891}
    },
    'Merma 4.0% (23M3)': {
        1: {5: 0.612}, 2: {15: 0.756}, 3: {50: 0.817}, 
        4: {200: 0.852}, 5: {500: 0.872}, 6: {750: 0.887}
    }
}

# --- AMPLIADO: Constante de Flujo Magnético (C) ---
# Base de datos completada según la tabla 3.2 de la guía.
constante_flujo_db = {
    'monofasico_columnas': (1.2, 1.9),
    'monofasico_acorazado': (3.0, 4.0),
    'trifasico_columnas': (1.0, 1.6),
    'trifasico_acorazado': (2.0, 3.0)
}

# --- SIN CAMBIOS (YA ERAN COMPLETOS SEGÚN LA GUÍA) ---

# Densidad de Flujo Magnético (B) en kgauss (Tabla 3.1)
densidad_flujo_db = {
    1: (11, 13), 
    10: (13, 16), 
    100: (16, 17), 
    1000: (17, 18), 
    5000: (17.5, 18)
}

# Densidad de Corriente (J) en A/mm^2 para ONAN
densidad_corriente_db = {
    'ONAN': {'Cobre': (3.0, 4.0)}
}

# Dimensiones de los Escalones como factor del Diámetro (D) (Tabla 2.4)
dimensiones_escalones_db = {
    1: [0.707],
    2: [0.850, 0.526],
    3: [0.906, 0.707, 0.424],
    4: [0.934, 0.796, 0.605, 0.356],
    5: [0.950, 0.846, 0.707, 0.534, 0.313],
    6: [0.959, 0.875, 0.768, 0.640, 0.488, 0.281]
}

# Alias público para compatibilidad con la UI (uso: from core.database import conexiones_normalizadas)
conexiones_normalizadas = conexiones_normalizadas_db