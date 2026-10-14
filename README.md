# SASISOPA — documentos PDF

La base activa es **SASISOPA1.zip**: tres PDF originales, **87 páginas** en total. Sustituye a las bases anteriores. El programa crea copias con los campos capturados, manteniendo las páginas, orientación y trazos de las tablas.

## Descargar y usar en Windows

1. [Descarga el programa](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip) y extrae todo.
2. Extrae tu **SASISOPA1.zip** y copia estos tres archivos directamente en la carpeta `plantillas` del programa, conservando sus nombres:
   - `1 POLITICA.pdf` — 14 páginas.
   - `2. ID DE PELIGROS.pdf` — 53 páginas.
   - `3. REQUISITOS LEGALES.pdf` — 20 páginas.
3. Con Python 3.12 o posterior instalado, ejecuta **Instalar.bat** y después **Iniciar.bat**. Este modo no necesita Microsoft Word.
4. Captura solo los datos que quieras cambiar. **Los campos vacíos conservan el contenido original**, incluyendo fechas, puestos y revisión. El número de estación usa el formato `E-00000`.
5. Selecciona representante legal/autoriza y secretario entre las cinco filas de personal. Puedes subir o dibujar firmas, elegir un logo y guardar/cargar un perfil de estación.
6. Marca los documentos que quieras generar. Activa **Crear también un PDF con todos los documentos seleccionados** si quieres reunirlos en un archivo; seleccionando los tres tendrá 87 páginas.
7. Pulsa **Generar documentos** y revisa las copias en un lector de PDF antes de utilizarlas. Cada lote se guarda en una carpeta nueva dentro de `salidas`.

Los originales, resultados, logos, firmas y perfiles reales no se publican en GitHub. Debes copiar tus tres PDF a `plantillas` para usar esta base. El Excel se conserva como catálogo; este modo captura los datos en el formulario y no los importa desde Excel.

## Campos que cambian

- Número de estación en encabezados, códigos y referencias de texto de los tres documentos.
- Razón social y dirección en portadas y encabezados. La razón social también se actualiza en las referencias del cuerpo y las celdas de operador identificadas.
- Logo proporcional dentro de sus espacios originales.
- Número de revisión del encabezado y sufijo R de los códigos. Fecha de revisión como mes y año en portadas/encabezados.
- Nombre de AUTORIZO en las portadas y del representante legal en la política. En Política, convocante/facilitador y secretario según las filas elegidas.
- Fecha común para reuniones y listas de Política; nombres y puestos en sus tres listas de cinco asistentes. Las filas vacías conservan su posición y contenido.
- Firmas cargadas o dibujadas en las listas y los espacios existentes del representante legal/autoriza. **No se crean bloques nuevos.** Los otros bloques históricos de elaboración/revisión/aprobación no reciben nuevas firmas.

Los PDF contienen firmas y sellos anteriores. Al capturar estación, razón social o nombres se retiran esas imágenes de la copia para evitar atribuirlas a una identidad distinta. Sin esos cambios, se conservan; una firma nueva del representante reemplaza la anterior en su espacio. Los diagramas y fotos técnicas se mantienen. El logo original permanece si no seleccionas otro.

Horarios, teléfonos, acuerdos, fechas históricas, historial de cambios, matrices de riesgo, requisitos y demás contenido técnico se conservan. Los nombres del equipo técnico del análisis de riesgo mantienen su contenido original; todavía no tienen una asignación por roles en el formulario. Esta versión no recalcula matrices ni determina obligaciones legales. Revisa el contenido fijo para tu estación.

Los espacios tienen tamaño fijo. El texto nuevo se ajusta dentro de ellos y se rechaza si no cabe; se utiliza una fuente estándar y no se garantiza identidad tipográfica. Se aceptan exclusivamente los tres originales de esta versión del ZIP, comprobados por su huella SHA-256. La preparación de todos los documentos termina antes de guardar el lote; un error no deja documentos incompletos.

## Perfiles

**Guardar estación/Cargar estación** conservan datos, logo y firmas en un archivo local `.sasisopa`. La fecha de reunión y las carpetas se mantienen aparte. Un perfil anterior con una sexta persona se rechaza explícitamente: no se descarta esa persona ni se modifica el perfil original.

## Verificación

La suite completa aprobó 40 pruebas y omitió cuatro grupos de integración de bases retiradas. Las pruebas del motor PDF se ejecutan aquí en Linux con los tres originales privados. Comprueban copias exactas con todos los campos vacíos, cambios de identidad, conservación de campos selectivos, 87 páginas y sus tablas, orden del PDF unido, selección de documentos, imágenes, firmas, originales intactos y errores sin resultados parciales. Los grupos de integración de las bases retiradas se omiten explícitamente.

**Pendiente:** instalación e interacción real con la ventana en Windows y revisión final del contenido por el usuario. Las pruebas del motor no equivalen a abrir la aplicación en Windows.

Para ejecutar las pruebas con tus PDF locales:

```bat
set "SASISOPA1_DIR=%CD%\plantillas"
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Los siguientes ZIP se incorporarán como nuevos lotes calibrados al mismo catálogo. Copiar PDF adicionales a la carpeta no los adapta automáticamente. Las [imágenes del diseño](docs/diseno-propuesto.png) son ilustraciones de referencia y pueden mostrar una versión anterior.
