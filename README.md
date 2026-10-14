# SASISOPA — Política en PDF

Por solicitud del usuario, las siete plantillas Word anteriores se retiraron. La nueva base es **PROCEDIMIENTO I.pdf**, del ZIP **1. POLITICA**: un archivo de 14 páginas con el procedimiento y sus formatos. El programa rellena una copia de ese PDF directamente, sin convertirlo a Word.

## Descargar y usar

1. [Descarga el ZIP del programa](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip) y extrae todo.
2. Del ZIP que compartiste, entra en `1. POLITICA` y copia **PROCEDIMIENTO I.pdf** directamente dentro de `plantillas` del programa. No coloques los siete Word anteriores.
3. Ejecuta **Instalar.bat** otra vez al actualizar: se agregó PyMuPDF. Se comprobó la disponibilidad de su dependencia para Windows x64 y Python 3.12.
4. Ejecuta **Iniciar.bat**. Introduce número de estación con formato `E-00000`, razón social, dirección, fecha de reuniones y hasta **cinco personas** con sus puestos.
5. Elige quién figura como **representante legal / autoriza** y quién como secretario. La primera selección actualiza también el nombre de AUTORIZO de la portada y el representante legal de la política.
6. Opcionalmente, selecciona logo, revisión y fecha de revisión. Usa **Subir** o **Dibujar** para las firmas.
7. Pulsa **Generar documentos**. Se guarda un único PDF de **14 páginas**, conservando la geometría de las tablas.
8. Abre la copia en un lector de PDF y revisa los campos, las firmas, los textos fijos y los espacios antes de utilizarla.

Este modo no necesita Microsoft Word. Los datos se capturan en el formulario; el Excel se conserva como catálogo. El modo Excel anterior se deshabilitó para evitar generar documentos con la base retirada.

## Campos y límites

- Estación en encabezados, códigos y texto del procedimiento/política.
- Razón social y dirección en portada y encabezados; logo proporcional dentro de su espacio.
- Revisión y sufijo R de códigos; mes/año del encabezado y portada cuando se indica fecha de revisión.
- Fecha común para las reuniones y las listas; nombres y puestos en las tres listas de cinco asistentes.
- Convocante/facilitador usan la selección de representante y Secretario usa su selección.
- Firmas seleccionadas en las listas y en los espacios de autorización/representante legal existentes. **No se añaden bloques nuevos.** Los bloques genéricos ELABORÓ/REVISADO POR/APROBADO POR permanecen sin imágenes de firma; su asignación por roles no está implementada.

El PDF original trae imágenes de firmas y sellos. Se retiran de las zonas de firma de la **copia generada**; el original permanece intacto. Las firmas seleccionadas son imágenes, no firmas digitales criptográficas.

Horarios, teléfono, temas, acuerdos, contenido del procedimiento, historial de actualización y fechas históricas de elaboración/revisión se conservan. La aplicación no verifica que los acuerdos se hayan realizado. Revisa esos datos antes de usar la copia.

Los campos tienen espacios fijos: el texto se ajusta dentro de ellos y se rechaza si no cabe. Se usa una fuente estándar en los campos nuevos; no se garantiza identidad tipográfica con la fuente original. Se admite esta versión exacta del PDF; una base modificada se rechaza antes de guardar.

## Estaciones guardadas

**Guardar estación** y **Cargar estación** conservan datos, logo y firmas en un archivo local `.sasisopa`. La fecha de reunión y las carpetas de trabajo se mantienen aparte. Un perfil anterior con una sexta persona se rechaza de forma explícita en este modo: no se descarta esa persona ni se modifica el perfil original.

Los PDF originales, resultados, logos, firmas y perfiles reales no se publican en GitHub.

## Comprobaciones

Se ejecutaron **35 pruebas aprobadas** con el PDF original local, incluyendo siete pruebas del nuevo llenado PDF. **Tres grupos de integración de Word se omiten explícitamente** porque sus plantillas se retiraron; sus resultados no validan este flujo.

Se comprobó generación de 14 páginas, dimensiones y geometría/color de líneas de tablas, campos actualizados, imagen proporcional, firmas en sus espacios, retiro de imágenes antiguas, original intacto, exceso de asistentes, texto excesivo, PDF alterado y sobrescritura. Se inspeccionaron imágenes renderizadas de portada y difusión durante el desarrollo.

**Pendiente:** instalación e interacción real con la ventana en Windows y revisión visual de todas las páginas por el usuario. Las pruebas PDF se ejecutaron aquí en Linux; no equivalen a una prueba de Windows.

Para ejecutar las pruebas del nuevo PDF local:

```bat
set "SASISOPA_NEW_PDF=%CD%\plantillas\PROCEDIMIENTO I.pdf"
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Consulta [REVISION.md](REVISION.md) para el historial. La [imagen del diseño](docs/diseno-propuesto.png) es una ilustración de referencia.
