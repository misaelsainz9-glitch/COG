# Generador SASISOPA para Windows

Primera versión de una aplicación de escritorio que rellena siete plantillas Word desde una base Excel. Genera copias de los documentos y puede exportarlas a PDF usando Microsoft Word.

## Descargar y ejecutar

1. En GitHub, selecciona **Code → Download ZIP**, o descarga [el ZIP de main](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip).
2. Extrae todo el archivo ZIP.
3. Instala **Python 3.12 o posterior** desde [python.org](https://www.python.org/downloads/windows/). Microsoft Word de escritorio es necesario para exportar PDF.
4. Copia tus **siete documentos Word originales** a la carpeta `plantillas`. Conserva los nombres exactos indicados en la hoja **Plantillas** del Excel. Los documentos originales no se publican en este repositorio.
5. Ejecuta **Instalar.bat** una vez para instalar las dependencias.
6. Ejecuta **Iniciar.bat**: se abrirá el modo básico, sin necesidad de editar Excel.
7. Introduce fecha, número y nombre de estación, y los nombres y puestos del personal. Selecciona las filas del representante/responsable y del secretario.
8. Elige la carpeta de salida y pulsa **Generar los siete documentos**. Puedes activar PDF si tienes Word instalado.
9. Abre los resultados en Word y revisa contenido, tablas y saltos de página antes de utilizarlos.

El modo básico conserva los horarios, temas, acuerdos y demás contenido de las plantillas. Aplica la misma fecha y lista de personal a los siete documentos; el representante seleccionado figura como convocante, facilitador y responsable de agenda. Comprueba que estas asignaciones correspondan a tu operación.

El modo avanzado original sigue disponible ejecutando `.venv\Scripts\python.exe programa.py`; usa el Excel y permite eventos y contenidos distintos. Consulta **LEEME.txt** para ese modo.

## Límites y comprobaciones

El motor se probó generando las siete plantillas con datos ficticios; se verificaron las cantidades de filas y los archivos de imágenes, y que los originales permanecieran intactos. Se comprobaron los bloqueos de sobrescritura y exceso de asistentes. El modo avanzado también bloquea eventos sin revisar. El modo básico requiere revisión manual del contenido conservado de las plantillas.

La interfaz Windows, la exportación a PDF mediante Word y la apariencia visual final **siguen pendientes de validación en Windows**. Los textos largos pueden cambiar la paginación. El programa no amplía las tablas si se supera su capacidad, no genera firmas ni inventa acuerdos o asistencias.

Esta entrega incluye código Python y lanzadores `.bat`; no es un instalador `.exe`. Los datos de operación se procesan localmente. Internet se necesita para instalar las dependencias.
