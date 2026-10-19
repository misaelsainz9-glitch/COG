# Revisión integral del expediente SASISOPA

Se generaron dos lotes completos con datos ficticios distintos sobre los **18 procedimientos y 523 páginas base**. Ambos tienen 525 páginas con las fichas anexas y un PDF unido con 18 marcadores. No se publican la base privada, los PDF de salida ni sus capturas completas.

## Correcciones aplicadas

- **Listado maestro de VIII, páginas físicas 11–12:** sus 19 filas ahora tienen revisión y fecha vinculadas. Las 18 filas de procedimientos toman el valor del procedimiento correspondiente; la del documento maestro usa el valor general. Una revisión particular de II se refleja también en su fila de VIII. Se conservan los bordes y las fechas de reuniones independientes.
- **Fecha junto a las firmas:** nuevo campo opcional `documento.fecha_firmas`, disponible en Documentos. Actualiza las fechas de los cuadros existentes del documento seleccionado; no sustituye la fecha de revisión. Vacío conserva la fecha original. Hay 1,187 ubicaciones calibradas.
- **Revisiones de dos dígitos:** se aprovecha el espacio libre de los rótulos de portada, incluidas las portadas interiores. En referencias estrechas se permite condensación horizontal moderada del número, conservando su tamaño y línea base. Se comprobó que no se borre el texto contiguo. Los valores que exceden el espacio siguen produciendo un aviso.
- **Campos movidos:** una fecha o revisión de referencia conserva el documento al que pertenece al cambiar su ubicación.

## Comprobaciones ejecutadas

| Comprobación | Resultado |
| --- | --- |
| Primer lote: tres combustibles, seis personas, dirección con municipio/estado/CP y fechas nuevas | 6,012 campos de texto comprobados, sin diferencias |
| Segundo lote: otra estación, otras personas, sólo Magna, dos compartimentos y revisión general 12; II con revisión 3 y fecha propia | 5,780 campos y 5 grupos repartidos entre casillas, sin diferencias |
| Imágenes del segundo lote | 1,773 colocaciones dentro de sus regiones |
| Dimensiones y trazos de las tablas | Conservados en las 523 páginas base de cada lote |
| Listas de asistencia | 119 casillas vacías en cada lote, incluso con asignaciones antiguas guardadas |
| PDF unido | 525 páginas y 18 marcadores en cada lote |
| Base original | Los 18 archivos conservan sus SHA-256 de catálogo |
| Revisión 12 | Comprobación de 673 campos independientes de revisión y pruebas de portadas interiores y texto contiguo |

**Suite completa:** 119 pruebas ejecutadas por el corredor: 114 aprobadas y 5 grupos de plantillas retiradas omitidos; ningún fallo. Tras centrar los rótulos de revisión se repitieron 14 pruebas de coherencia y alineación, también sin fallos. Se buscaron además 24 valores modificados del primer perfil en el segundo lote y no se encontraron residuos.

Los controles de texto verifican la presencia del valor esperado en su región, no sólo que el programa termine sin excepción. También se comprobó el caso de una revisión y fecha particulares de II referidas desde VIII.

## Hallazgos que siguen pendientes

**El expediente todavía requiere revisión documental y técnica.** Las comprobaciones de llenado no equivalen a coherencia completa de su contenido.

1. **16 referencias del listado maestro no coinciden con los códigos de los procedimientos III–XVIII.** Por ejemplo, el índice usa `.03.PO.03.R` y III contiene `.03.PO.01.R`. Se registraron los identificadores disponibles. No se renumeran documentos ni se elige un subprocedimiento arbitrariamente cuando hay varios.
2. **Índice de registros, VIII página física 16:** dos referencias de XIII usan `.13.RE.03.R` y `.13.RE.04.R`, mientras sus formatos tienen `.013.RE.03.R` y `.013.RE.04.R`. Además, `.14.RE.03.R` no se localizó entre los identificadores calibrados de XIV. Esto exige confirmar el identificador correcto; no prueba por sí solo que falte una página.
3. **Dirección larga en XI página física 14:** el encabezado compacto no admite la dirección de prueba de 57 caracteres con municipio/estado/CP y el tamaño mínimo permitido. Se comprobó que avisa antes de modificar la página y no genera un lote parcial. Hace falta una versión abreviada del mismo domicilio o ajustar expresamente su ubicación en ese formato.
4. **Capacidad de autotanques de recepción:** los textos de II página 29 y XIII página 34 conservan capacidades de ejemplo de los vehículos de entrega. Son distintas de las capacidades de almacenamiento capturadas y no tienen un vínculo automático propio.
5. **Campos particulares de registros:** folios, evidencias, acuerdos, resultados, periodos, responsables de actividades y datos de eventos requieren captura expresa y, cuando no tengan ubicación, marcarla en el editor. Cambiar los datos generales de la estación no los completa.
6. **Riesgos y emergencias:** el inventario actualiza sus campos vinculados; no recalcula consecuencias, calificaciones HAZOP ni determina que las medidas y recomendaciones anteriores sean suficientes. Los directorios, recursos y condiciones del sitio requieren revisión real.
7. **Campos vacíos e imágenes:** los campos opcionales vacíos conservan la base y los faltantes técnicos pueden mostrar «Pendiente». La revisión de texto no lee las letras incrustadas dentro de imágenes; éstas requieren inspección visual adicional.

## Cobertura por procedimiento

Todas las filas incluyen los campos generales disponibles: estación, domicilio, empresa, logo, revisión, fecha, referencias y firmas según sus espacios existentes. La columna final indica información particular que no debe inferirse de esos datos generales.

| Procedimiento | Páginas base | Campos de texto comprobados en lote B | Captura/revisión particular |
| --- | ---: | ---: | --- |
| I. Política | 14 | 162 | Reuniones, convocante/facilitador, secretario y asistentes; nombre y firma del representante. |
| II. Peligros y riesgos | 57 | 781 | Equipo HAZOP por seis funciones distintas, compañía e iniciales en las matrices. Fechas de estudio independientes. |
| III. Requisitos legales | 26 | 266 | Registros de requisitos y su evaluación: responsables/fechas se capturan por registro; resultados y obligaciones se revisan aparte. |
| IV. Objetivos, metas e indicadores | 13 | 136 | Registro de objetivos/metas/indicadores y programa anual: datos de estación y responsables; metas, resultados y calendario son propios del registro. |
| V. Funciones y autoridad | 21 | 238 | Organigrama por cinco funciones, designación/aceptación del representante técnico y sus datos de contacto/notificaciones. |
| VI. Competencia y capacitación | 45 | 477 | Ficha de personal: nombres y apellidos, contacto, fecha/lugar de nacimiento, sexo, edad, estado civil, nacionalidad, CURP, RFC, NSS, estudios, experiencia y puesto; opcional y por empleado. |
| VII. Comunicación | 15 | 153 | Bitácora y distribución de comunicaciones; remitente/destinatario y responsables por registro. La encuesta de la página 14 está en imagen. |
| VIII. Control documental | 18 | 395 | Acuse: folio, fecha, entrega/recepción y documentos. Catálogos e índices: actualizar estación dentro de códigos sin cambiar identificadores de formatos. |
| IX. Mejores prácticas | 16 | 164 | Reunión y asistencia: fecha/hora/lugar, responsables y participantes; acuerdos capturados por evento. |
| X. Control de actividades y procesos | 24 | 225 | Permisos/AST: lugar, horarios, responsables del área, ejecución y autorización; cada firma se asigna al bloque que la pide. |
| XI. Integridad mecánica | 33 | 315 | Orden de trabajo: fecha, inicio, equipo y responsables propios de la orden. Los datos técnicos y resultados de mantenimiento no se deducen de nombres. |
| XII. Contratistas | 44 | 424 | Proveedor/contratista, personal participante, evaluador y responsables de acuerdos; empresa externa distinta de razón social de la estación. |
| XIII. Emergencias | 70 | 717 | Responsables/brigadas y programa de simulacros; contactos públicos, escenarios y calendario requieren revisión propia. Encabezado del cronograma incrustado en imagen. |
| XIV. Monitoreo y evaluación | 39 | 412 | Responsables por registro de monitoreo/evaluación. Matriz legal y hallazgos requieren captura específica; no llenar instrucciones como si fueran celdas. |
| XV. Auditorías | 31 | 335 | Equipo auditor, auditor líder, contactos, fechas/folios, responsables de atender hallazgos, elaborar/autorizar/recibir y seguimiento. |
| XVI. Incidentes y accidentes | 39 | 399 | Quien reporta: nombre, cargo, teléfono y correo; CURR, folio, ID y fecha/hora del evento. Páginas 15–17 explican el llenado y se conservan. |
| XVII. Revisión de resultados | 10 | 99 | Informe de reunión: número de informe, tipo/fecha/lugar y responsables; conclusiones, resultados y acuerdos se capturan expresamente. |
| XVIII. Informe de desempeño | 8 | 82 | Indicadores y avance de desempeño: valores y periodo del informe requieren datos reales; no se infieren por cambiar la estación. |

## Reproducir la auditoría

Con la base privada y un perfil guardado, ejecutar fuera de las carpetas públicas:

```sh
python scripts/auditar_coherencia.py RUTA_BASE PERFIL.json CARPETA_NUEVA
```

Genera el lote y `auditoria_coherencia.json`, con comprobaciones por procedimiento, campos pendientes, referencias documentales por confirmar y límites explícitos. No sobrescribe carpetas existentes. `passed` se refiere a las comprobaciones mecánicas indicadas en `passed_scope`; `coherence_status` mantiene la revisión documental y técnica pendiente.

[Resultados sin documentos privados](resultados-coherencia-integral.json).

Estos cambios corresponden al proyecto fuente. El ZIP público v0.2.2 anterior no se actualiza automáticamente con esta revisión.
