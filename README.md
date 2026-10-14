# SASISOPA — nueva base documental

El catálogo anterior de siete plantillas Word se retiró por solicitud del usuario. La base activa ahora es **PROCEDIMIENTO I.pdf**, del ZIP **1. POLITICA**: un PDF de 14 páginas con procedimiento y formatos del apartado de política.

## Estado actual

- Se conserva la aplicación, su diseño, los perfiles de estación, logo y firmas como imágenes.
- El catálogo y el Excel ya contienen únicamente la nueva base `POL-I`.
- **La generación está deshabilitada mientras se adapta el llenado del nuevo documento.** No se ha probado ni habilitado su automatización.
- El PDF no tiene campos rellenables y no contiene archivos Word. Está pendiente confirmar si existe el Word original o si hay que preparar un flujo de llenado sobre PDF.
- Las firmas seguirán colocándose únicamente en espacios existentes, según la preferencia confirmada del usuario.
- Los originales y perfiles privados no se publican en GitHub.

## Descargar y preparar

1. [Descarga el ZIP del programa](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip) y extrae todo.
2. Copia `PROCEDIMIENTO I.pdf` desde tu ZIP en `plantillas`. Los siete Word anteriores ya no se utilizan.
3. Conserva el Excel, el JSON y todos los archivos Python incluidos.
4. Si tienes el Word original del nuevo documento, compártelo para configurar los campos sobre esa versión.
5. `Instalar.bat` prepara las dependencias; `Iniciar.bat` abre la aplicación. Puedes seguir guardando/cargando estaciones. El botón de generación indica que el llenado está pendiente.

El formato de origen es importante para conservar la estructura: los encabezados, imágenes y campos del nuevo PDF deben mapearse específicamente antes de generar copias.

## Validación

Se verificaron el archivo recibido, sus 14 páginas y la ausencia de campos rellenables. Se comprobó que el catálogo y el Excel ya no contienen las siete plantillas anteriores y que se bloquea la generación durante esta transición.

Las pruebas de utilidades y perfiles siguen disponibles. Tres grupos de integración con los Word anteriores se omiten explícitamente porque esas plantillas fueron retiradas; sus resultados históricos no validan el nuevo PDF. La nueva generación, Windows, Word y la inspección visual están pendientes.

Consulta [REVISION.md](REVISION.md) para el historial técnico. La [imagen del diseño](docs/diseno-propuesto.png) es una ilustración de referencia, no una captura de la aplicación.
