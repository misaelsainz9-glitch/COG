# Revisión profunda de HAZOP y documentos vinculados

Se revisó el llenado de instalaciones, miembros del equipo, iniciales, fechas del proyecto, ubicaciones personalizadas y generación de documentos completos. La revisión encontró fallos y se agregaron pruebas que los reproducen antes de corregirlos.

## Correcciones

| Caso encontrado | Resultado corregido |
| --- | --- |
| Muchos tanques no cabían en la casilla del nodo. | La casilla remite al inventario anexo y allí se conservan todos los identificadores. Se comprobó el caso de 60 tanques. |
| Fichas con detalles largos no cabían en el espacio de tres registros. | Los registros largos reciben una página propia; el contador, la vista previa y el PDF usan la misma distribución. Las palabras largas se continúan sin perder caracteres. |
| Al mover un campo se perdían reglas de combustible, fecha de respaldo o prefijo. | Las ubicaciones nuevas conservan esas reglas. Los combustibles ausentes no reciben iniciales ni fechas, incluso con ubicaciones personalizadas. |
| Al mover un párrafo podían quedar sus primeras o últimas líneas anteriores. | Se borra todo el texto de su área original, conservando los trazos del formato. |
| Cero dispensarios o mangueras seguía produciendo una afirmación de despacho. | Se distingue entre «Despacho registrado», «Sin despacho» y «Equipo por confirmar». |
| Un proyecto con fechas o inventario, pero sin personas asignadas, podía conservar compañías anteriores. | Los campos faltantes del equipo indican «Pendiente». |
| El nombre ficticio «Ulises Hernández Cruz» no cabía en una carta de V. | Se aprovecha el espacio libre de la casilla de continuación y se permite un ajuste moderado de letra en las cartas, sin desplazar el texto fijo. |
| Las fechas globales del estudio podían bloquear la exportación de otro procedimiento por separado. | Esos campos se aplican a II y no impiden exportar I, V o VIII. Los campos desconocidos siguen avisando si no tienen ubicación. |
| Repetir la calibración agregaba otra vez las fechas del estudio. | La calibración del equipo y fechas se puede repetir sin añadir campos ni cambiar su resultado. |
| Un número de estación particular del documento podía saltarse la validación. | La validación también comprueba ese valor antes de generar. |

## Comprobaciones sobre PDF reales

Se generaron los 18 documentos con datos ficticios, seis personas asignadas, fechas de estudio nuevas y un registro de tanque con todos sus detalles extensos. El PDF unido tiene **529 páginas y 18 marcadores**: las 523 páginas base y seis fichas anexas.

Se comparó el contenido de píxeles entre la vista previa y el PDF exportado en diez muestras: II páginas 30, 33, 34, 54, 58 y 60; XIII páginas 35, 36, 71 y 73. Coinciden exactamente. En los dos documentos vinculados no quedaron las capacidades, la marca ni las condiciones de operación anteriores del ejemplo. En II también se comprobó la sustitución de las fechas del estudio.

Las pruebas cubren las siete combinaciones no vacías de Magna, Premium y Diésel, iniciales automáticas, combustibles ausentes, nombres y empresas por integrante, fechas, perfiles antiguos y actuales, palabras de 100 caracteres, hasta 60 tanques, vista previa de anexos, bordes, firmas y listas de asistencia vacías.

No se publican los documentos privados ni sus capturas completas. La ejecución de Windows utiliza documentos sintéticos y no recibe la base privada.

## Alcance

El sistema actualiza los datos capturados y conserva las regiones del formato comprobadas. **No recalcula ni certifica las valoraciones de riesgo HAZOP.** Esas valoraciones necesitan revisión técnica cuando cambian la instalación o sus condiciones.

El ZIP y el instalador v0.2.2 publicados anteriormente todavía corresponden a la versión anterior; esta revisión se refiere al proyecto corregido.

## Resultado final

- Suite local con la base privada y escritorio real: **110 pruebas, sin fallos**, con cinco grupos de plantillas antiguas omitidos.
- [Verificación de código e interfaz en Windows](https://github.com/misaelsainz9-glitch/COG/actions/runs/39295273784): completada correctamente.
- [Construcción y prueba del instalador en Windows](https://github.com/misaelsainz9-glitch/COG/actions/runs/39295273632): código probado, ejecutable independiente construido y diagnosticado, instalación, actualización y desinstalación correctas, con conservación de datos del usuario.
- Lote real de 18 documentos y comparación exacta de diez vistas previas: completados correctamente.
- Identificadores de campos de los 18 mapas: sin duplicados.

Las verificaciones de Windows corresponden al código de la corrección `8b02876`. El instalador construido allí quedó como artefacto de pruebas; no reemplaza automáticamente el ZIP público anterior.
