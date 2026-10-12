# Generador SASISOPA para Windows

Primera versión de una aplicación de escritorio que rellena siete plantillas Word desde una base Excel. Genera copias de los documentos y puede exportarlas a PDF usando Microsoft Word.

## Descargar y ejecutar

1. En GitHub, selecciona **Code → Download ZIP**, o descarga [el ZIP de main](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip).
2. Extrae todo el archivo ZIP.
3. Instala **Python 3.12 o posterior** desde [python.org](https://www.python.org/downloads/windows/). Microsoft Word de escritorio es necesario para exportar PDF.
4. Copia tus **siete documentos Word originales** a la carpeta `plantillas`. Conserva los nombres exactos indicados en la hoja **Plantillas** del Excel. Los documentos originales no se publican en este repositorio.
5. Ejecuta **Instalar.bat** una vez para instalar las dependencias.
6. Completa **Base_SASISOPA.xlsx** siguiendo la hoja **Instrucciones**. Sus ejemplos son ficticios.
7. En **Eventos**, marca el evento como **Revisado** después de comprobar sus datos. En **Generar**, agrega una fila por documento y marca **Sí** en la columna `generar`.
8. Guarda y cierra Excel, ejecuta **Iniciar.bat** y selecciona la carpeta de salida.
9. Abre los resultados en Word y revisa contenido, tablas y saltos de página antes de utilizarlos.

Consulta **LEEME.txt** para las relaciones entre hojas y requisitos de cada documento.

## Límites y comprobaciones

El motor se probó generando las siete plantillas con datos ficticios; se verificaron las cantidades de filas y los archivos de imágenes, y que los originales permanecieran intactos. Se comprobaron los bloqueos de sobrescritura, eventos sin revisar y exceso de asistentes.

La interfaz Windows, la exportación a PDF mediante Word y la apariencia visual final **siguen pendientes de validación en Windows**. Los textos largos pueden cambiar la paginación. El programa no amplía las tablas si se supera su capacidad, no genera firmas ni inventa acuerdos o asistencias.

Esta entrega incluye código Python y lanzadores `.bat`; no es un instalador `.exe`. Los datos de operación se procesan localmente. Internet se necesita para instalar las dependencias.
