# Rectángulos negros en espacios de firma

La revisión visual de un lote generado encontró dos rectángulos negros sobre un pie de firmas. La base limpia no tenía esos rectángulos: aparecían al procesar una lista de asistencia próxima a imágenes transparentes que habían sustituido firmas retiradas.

Los marcadores eran imágenes de un píxel con una máscara completamente transparente. Al aplicar una redacción de imágenes, MuPDF podía recortarlos y producir una imagen opaca. El texto seguía presente en el PDF, por lo que una comprobación de extracción de texto no detectaba el defecto visual.

La corrección reemplaza **solamente imágenes de 1×1 píxel cuya máscara es totalmente transparente** por objetos gráficos vacíos. Antes de las redacciones tienen exactamente el mismo resultado visual. No elimina imágenes opacas, logos, imágenes mayores ni texto, y no modifica los PDF base en disco. Se aplica tanto a la vista previa como a la exportación.

## Verificaciones

- Pruebas con documentos sintéticos: píxeles, texto y trazos idénticos antes de procesar; persistencia después de guardar; conservación de imágenes opacas y de mayor tamaño; operación repetible.
- Regresión sobre la base privada: el pie de firmas de I, página física 14, queda idéntico al original después de vaciar la lista de asistencia y guardar el documento.
- Suite local completa: **122 pruebas, 117 aprobadas y 5 grupos de plantillas retiradas omitidos; ningún fallo**.
- [Abridor nativo de Windows y extracción normal del ZIP](https://github.com/misaelsainz9-glitch/COG/actions/runs/39321340323): comprobados con PDF sintéticos y una clave pública exclusiva de pruebas. Se verificaron apertura correcta, rechazo de clave equivocada, contenido alterado y componente ausente, conservación de carpetas existentes y limpieza de temporales tras fallos. No se enviaron los documentos privados ni su clave a Windows CI.

En el lote revisado se compararon los píxeles de las **525 páginas** antes y después: sólo cambió I, página física 14, en el área afectada. Las otras **524 páginas quedaron idénticas**. La salida final no conserva imágenes de un píxel; los logos e imágenes reales permanecen. Los 2,104 usos de marcadores en la base se tratan en la copia de trabajo, sin cambiar la base original.

La revisión visual de páginas completas usa láminas de conjunto y ampliaciones de las zonas sospechosas. No equivale a leer y validar técnicamente cada palabra del expediente. Continúan pendientes los datos de proyecto no proporcionados y las discrepancias documentales previamente informadas.
