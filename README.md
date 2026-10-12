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

## Revisión de esta versión

Se corrigió la inicialización de COM para la exportación PDF desde el hilo de trabajo. Ahora se comprueba que Word realmente haya creado cada PDF y se libera la conexión incluso cuando falla. Estas comprobaciones se probaron con una simulación de COM; no sustituyen una prueba con Microsoft Word real.

La ventana tiene desplazamiento vertical para pantallas pequeñas. Se rechazan nombres duplicados, carpetas vacías, catálogos incompletos y campos con saltos de línea. El instalador verifica Python 3.12 o posterior.

**Datos que siguen fijos:** domicilio de la estación, correos, teléfonos, cargos SASISOPA, horarios, temas, acuerdos y logotipos. El modo básico conserva esos datos del documento original. La nota informativa mantiene su afirmación original de que no hubo cambios; cambiar fecha o nombre no verifica esa afirmación. La aplicación muestra esta limitación antes de generar.

La misma fecha y lista se aplican a reuniones, asistentes y receptores; confirma que corresponda. Algunas plantillas solo tienen espacio para seis personas: el lote completo se bloquea si una plantilla no admite la lista. Los recuentos asociados al personal se recalculan cuando corresponde. Las fechas históricas de elaboración/revisión permanecen fijas.

**Validación pendiente en Windows:** instalación desde cero, interfaz con escalado de pantalla, exportación con Word, encabezados visibles, fuentes, textos largos, alturas de filas y saltos de página. Esta versión es para pruebas, no una garantía de apariencia idéntica.

### Pruebas reproducibles

Después de instalar dependencias y colocar los siete Word originales en `plantillas`:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Se ejecutaron seis pruebas y todas pasaron: generación de los siete documentos, preservación de filas/medios/fechas históricas, actualización de encabezados, rechazo de exceso de personal y duplicados, bloqueo de sobrescritura y limpieza de COM ante fallos. Sin las plantillas locales, las pruebas de documentos se omiten explícitamente; las pruebas simuladas de COM siguen ejecutándose.
