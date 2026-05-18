# Calculadora de Diseño de Transformadores

Este proyecto implementa en Python un flujo completo para el diseño de transformadores eléctricos y la generación de reportes en LaTeX. Incluye una interfaz gráfica para introducir las opciones iniciales del transformador, motores de cálculo por fases (núcleo, ventana, bobinados, pérdidas, rendimiento diario), generación de gráficos y exportación de un reporte compilado en PDF/PNG. Además, en el repositorio se incluyen scripts para crear un instalador (.exe) mediante PyInstaller y NSIS.

> Principales capacidades:

- Diseñar transformadores monofásicos y trifásicos mediante código Python.
- Configurar las opciones iniciales del transformador desde la UI: tipo, potencia (kVA), tensiones primaria/secundaria, frecuencia, conexión, TAPs, tipo de acero, tipo de corte, refrigeración y material conductor.
- Calcular automáticamente fases como núcleo, ventana y bobinados, estimar pérdidas y rendimiento diario.
- Generar gráficos y ensamblar un reporte LaTeX que se compila con TinyTeX / pdflatex y se convierte a PNG para previsualización.
- Empaquetado: contiene `build.bat` y `publish.bat` para generar el instalador y publicarlo.

Instalación rápida

- Recomendado: usar `uv` para gestionar el entorno y ejecutar comandos (ver `pyproject.toml` si está presente).
- Alternativa sin `uv` (Windows):
  - Crear entorno: `py -3 -m venv .venv`
  - Activar: `.\.venv\Scripts\activate`
  - Instalar dependencias: `pip install -r requirements.txt`

Ejecución

- Desde la raíz del proyecto puedes ejecutar la aplicación gráfica:


# Pseudo-npm nativo para Windows (scripts/)

Organizamos los atajos y comandos en una carpeta `scripts/` para evitar depender de herramientas externas. Ejecuta los `.bat` directamente desde la raíz del proyecto.

Estructura recomendada:

```
D:\...\SEM3\
├── .venv/
├── installer.nsi
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
└── scripts/
  ├── init.bat
  ├── install.bat
  ├── start.bat
  ├── start_prod.bat
  ├── build.bat
  ├── publish.bat
  └── update_reqs.bat
```

Comandos rápidos (desde la raíz):

```
scripts\init       # Crea .venv
scripts\install    # Instala dependencias
scripts\start      # Ejecuta la app en modo desarrollo
scripts\start_prod # Ejecuta la app en modo producción
scripts\build      # Genera el instalador (.exe)
scripts\publish    # Publica el instalador
scripts\update_reqs# Actualiza requirements.txt
```

Flujo típico:

1. Primera vez:
```
scripts\init
scripts\install
```
2. Desarrollo:
```
scripts\start
```
3. Empaquetado y publicación:
```
scripts\build
scripts\publish
```

Notas:
- Los `.bat` son nativos de Windows y no fallan con rutas que contienen espacios.
- `pyproject.toml` fue simplificado a metadatos básicos; los scripts se gestionan con los `.bat` en `scripts/`.

Limpieza de la raíz
-------------------
Si deseas borrar los archivos antiguos que quedaron en la raíz, ejecuta:

```
cleanup_root_scripts.bat
```

El script pedirá confirmación antes de borrar archivos.
- El punto de entrada principal es `src/main.py`.
- Si quieres que incluya las dependencias del `requirements.txt` dentro de `pyproject.toml` (bloque `dependencies`), lo puedo añadir para que `uv` maneje todo desde el pyproject.

Créditos

- Elaborado por C.E.A.T., Facultad de Ingeniería Eléctrica y Electrónica (UNCP).
