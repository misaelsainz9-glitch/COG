# Generador SASISOPA para Windows

Aplicación para rellenar siete plantillas Word mediante un formulario: fecha, estación, personal, encabezados y firmas como imágenes. Genera copias nuevas y permite exportar a PDF con Microsoft Word de escritorio.

## Descargar y ejecutar

1. Selecciona **Code → Download ZIP** o [descarga el ZIP de main](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip).
2. Extrae todo el archivo. Conserva el Excel y el archivo JSON incluidos: el formulario los necesita como catálogo y comprobación de plantillas.
3. Instala Python 3.12 o posterior desde [python.org](https://www.python.org/downloads/windows/). La disponibilidad de las dependencias se comprobó para Python 3.12 y Windows x64.
4. Copia los **siete Word originales sin modificar** en `plantillas`, con los nombres de la hoja **Plantillas** del Excel.
5. Ejecuta **Instalar.bat**. Si actualizaste una versión anterior, ejecútalo nuevamente para instalar la dependencia de dibujo.
6. Ejecuta **Iniciar.bat**. Completa fecha, número/nombre de estación y hasta seis personas con sus puestos.
7. Introduce la dirección y selecciona el logo PNG/JPG. Los campos vacíos conservan el dato original. Número y fecha de revisión son opcionales; usa un entero (0, 1, 2…) para el número de revisión, que también actualiza el sufijo R del código; los encabezados existentes muestran mes y año de revisión, y la nota no tiene ese bloque.
8. Para cada persona usa **Subir** para seleccionar una firma PNG/JPG, **Dibujar** para capturarla con el mouse o **Quitar** para dejar el espacio sin imagen. Al dibujar, pulsa **Guardar y usar** y elige dónde guardar su PNG.
9. Selecciona representante/responsable y secretario, la carpeta de salida y, opcionalmente, PDF. Pulsa **Generar los siete documentos**.
10. Revisa en Word contenido, imágenes, paginación y los PDF antes de utilizar los documentos.

Las plantillas originales, logos y firmas reales no se incluyen en GitHub. Las imágenes se seleccionan o guardan localmente; las firmas capturadas son imágenes insertadas en Word.

## Alcance y límites

La fecha y lista de personal son comunes a los siete documentos. El representante elegido figura como convocante, facilitador y responsable de agenda. Revisa que corresponda a las reuniones y entregas reales.

Logo y firmas se ajustan proporcionalmente a sus espacios. Las firmas se insertan en los campos existentes del acuse (receptores y entrega), la difusión (asistentes) y la nota informativa (representante). Por tu elección, las otras cuatro plantillas conservan su estructura y no reciben bloques nuevos de firma.

Correos, teléfonos, cargos SASISOPA, horarios, temas, acuerdos y texto de la nota se conservan. Dirección, logo y revisión también se conservan si no se capturan cambios. El formulario no guarda sus datos para la siguiente sesión; los PNG de firmas sí quedan en la ubicación elegida.

Los textos largos o las imágenes de firma pueden cambiar la altura de líneas y la paginación. La versión admite solamente las siete plantillas originales; las modificadas se rechazan antes de generar. Se conserva la cantidad de filas, los párrafos existentes del plan y las fechas históricas de elaboración/revisión.

El modo avanzado sigue disponible ejecutando `.venv\Scripts\python.exe programa.py`; usa el Excel. Los nuevos controles de encabezados y firmas corresponden al formulario básico. Consulta **LEEME.txt** para el modo avanzado.

## Validación

La última ejecución completó **29 pruebas sin fallos ni omisiones** con las siete plantillas reales y datos/imágenes ficticios. Incluye reemplazos, estructura de filas y párrafos, imágenes, encabezados, fechas, logos y firmas, capacidad, duplicados, protección contra sobrescritura, fallos de guardado, captura PNG y limpieza de COM simulada.

**Pendiente en Windows:** instalación desde cero, formulario, dibujo con mouse, Word, PDF real y revisión visual de los siete resultados. La disponibilidad de las dependencias no demuestra ejecución real en Windows.

Con las dependencias y los Word originales locales puedes ejecutar:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Sin los originales, las pruebas que los necesitan se omiten explícitamente. Consulta [REVISION.md](REVISION.md) para el informe técnico.
