# Campos identificados en los 18 procedimientos SASISOPA

Revisión de los 18 PDF recibidos: 523 páginas. El editor ya utiliza esta base completa y sus mapas de campos. Los datos identificados tienen ubicaciones predefinidas; los demás se capturan y se ubican una vez desde la vista previa del PDF real. Consulta [las instrucciones de uso](../README.md).

## Datos comunes

| Bloque | Campos |
|---|---|
| Estación | Número, razón social, dirección, localidad/municipio, estado, código postal, teléfono, correo, logo y CURR donde se solicite. |
| Personas | Nombre completo, puesto, iniciales confirmadas, empresa, teléfono, correo, domicilio para notificaciones y firma. |
| Documento/evento | Revisión y su fecha, fecha/hora/lugar de reunión, folio, fecha de designación, fecha de aceptación y periodo. Son independientes. |

## Asignación de personas

Seleccionar por separado alta dirección, representante legal, representante técnico, encargado de estación y jefe de operaciones. La referencia reutiliza una persona en varios cargos: eso no autoriza a unir esos cargos en los datos nuevos. Las firmas y nombres se vinculan a su función y espacio concreto. Una persona se guarda una sola vez y puede seleccionarse en varias funciones; no se duplican sus datos.

El catálogo de personas no debe tener un límite general de cinco: los formatos tienen capacidades distintas y el equipo HAZOP tiene seis funciones. La capacidad de cada tabla se comprobará al calibrarla, sin agregar filas ni bloques de firmas.

También hay convocante, facilitador, secretario de reunión, asistentes, secretario técnico y líder HAZOP, auditores, responsables del área y bloques de elaboración, revisión, autorización y recepción. El secretario de reunión y el secretario HAZOP son funciones diferentes.

El domicilio del representante para notificaciones y su contacto no deben copiarse automáticamente del domicilio/teléfono de la estación. Las empresas externas no se sustituyen por la razón social de la estación. Las iniciales de las matrices se capturan o se confirman; no se heredan del ejemplo.

## Revisión por documento

Las páginas siguientes se cuentan desde la primera hoja de cada PDF; difieren de su numeración impresa. Las páginas citadas son ejemplos relevantes, no una lista completa de todas las repeticiones.

| Documento | Páginas | Campos y particularidades | Referencias físicas |
|---|---:|---|---|
| I. Política | 14 | Reuniones, convocante/facilitador, secretario y asistentes; nombre y firma del representante. | 9, 10, 11, 12, 13, 14 |
| II. Peligros y riesgos | 57 | Equipo HAZOP por seis funciones distintas, compañía e iniciales en las matrices. Fechas de estudio independientes. | 33 |
| III. Requisitos legales | 26 | Registros de requisitos y su evaluación: responsables/fechas se capturan por registro; resultados y obligaciones se revisan aparte. | Revisión del documento completo |
| IV. Objetivos, metas e indicadores | 13 | Registro de objetivos/metas/indicadores y programa anual: datos de estación y responsables; metas, resultados y calendario son propios del registro. | 11, 13 |
| V. Funciones y autoridad | 21 | Organigrama por cinco funciones, designación/aceptación del representante técnico y sus datos de contacto/notificaciones. | 6, 16, 17, 18, 19 |
| VI. Competencia y capacitación | 45 | Ficha de personal: nombres y apellidos, contacto, fecha/lugar de nacimiento, sexo, edad, estado civil, nacionalidad, CURP, RFC, NSS, estudios, experiencia y puesto; opcional y por empleado. | 28 |
| VII. Comunicación | 15 | Bitácora y distribución de comunicaciones; remitente/destinatario y responsables por registro. La encuesta de la página 14 está en imagen. | 12, 14, 15 |
| VIII. Control documental | 18 | Acuse: folio, fecha, entrega/recepción y documentos. Catálogos e índices: actualizar estación dentro de códigos sin cambiar identificadores de formatos. | 11, 12, 13, 14, 15, 16, 17, 18 |
| IX. Mejores prácticas | 16 | Reunión y asistencia: fecha/hora/lugar, responsables y participantes; acuerdos capturados por evento. | 10, 11 |
| X. Control de actividades y procesos | 24 | Permisos/AST: lugar, horarios, responsables del área, ejecución y autorización; cada firma se asigna al bloque que la pide. | 23, 24 |
| XI. Integridad mecánica | 33 | Orden de trabajo: fecha, inicio, equipo y responsables propios de la orden. Los datos técnicos y resultados de mantenimiento no se deducen de nombres. | 17 |
| XII. Contratistas | 44 | Proveedor/contratista, personal participante, evaluador y responsables de acuerdos; empresa externa distinta de razón social de la estación. | 42, 43 |
| XIII. Emergencias | 70 | Responsables/brigadas y programa de simulacros; contactos públicos, escenarios y calendario requieren revisión propia. Encabezado del cronograma incrustado en imagen. | 16 |
| XIV. Monitoreo y evaluación | 39 | Responsables por registro de monitoreo/evaluación. Matriz legal y hallazgos requieren captura específica; no llenar instrucciones como si fueran celdas. | 30, 31 |
| XV. Auditorías | 31 | Equipo auditor, auditor líder, contactos, fechas/folios, responsables de atender hallazgos, elaborar/autorizar/recibir y seguimiento. | 14, 17, 20, 28, 29, 30, 31 |
| XVI. Incidentes y accidentes | 39 | Quien reporta: nombre, cargo, teléfono y correo; CURR, folio, ID y fecha/hora del evento. Páginas 15–17 explican el llenado y se conservan. | 13, 14 |
| XVII. Revisión de resultados | 10 | Informe de reunión: número de informe, tipo/fecha/lugar y responsables; conclusiones, resultados y acuerdos se capturan expresamente. | 8, 9, 10 |
| XVIII. Informe de desempeño | 8 | Indicadores y avance de desempeño: valores y periodo del informe requieren datos reales; no se infieren por cambiar la estación. | 7, 8 |

## Cómo se aplicará el llenado

1. Capturar estación y personas una vez; asignar cada función explícitamente.
2. Elegir documentos y capturar sus datos de evento, fecha o registro.
3. Mostrar una vista previa y avisar de textos que no quepan o funciones sin asignación.
4. Generar copias sin modificar la base; los vacíos conservan el contenido de la base limpia.

El número de estación aparece en encabezados, cuerpo, códigos e índices. Hay encabezados incrustados en imágenes en IV/13, XI/15 y XIII/16, además de la encuesta en imagen VII/14. Buscar/reemplazar texto por sí solo no cubre esos casos.

No se cambia una fecha histórica porque cambie la fecha de reunión. No se escriben datos sobre instrucciones, títulos, fórmulas, matrices técnicas, criterios legales ni números de página. Los cálculos y resultados requieren su propia captura y validación.

## Diseño tipográfico acordado

Conservar las fuentes Aptos/Calibri correspondientes al original. Estación/empresa en Arial 9 negrita y dirección en Arial 9 normal, alineada a la derecha; ajustar líneas dentro del bloque y reducir como máximo a 8 antes de avisar. El título conserva su tamaño y no se recorta. Cualquier ampliación de altura debe comprobar su impacto en el contenido.

## Estado de implementación

Implementado: importación local del ZIP original o limpio, editor por estación/personas/funciones, ubicaciones predefinidas, listas vinculadas, campos particulares con ubicación visual, guardado/carga, vista previa del PDF real y generación de los 18 archivos o un PDF unido. No todos los campos tienen ubicación automática: el editor señala los que necesitan configurarse. Las matrices y resultados técnicos no se deducen automáticamente. La instalación y el uso directo en Windows siguen pendientes de prueba.
