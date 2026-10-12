# Revisión técnica del generador

## Resultado

La versión básica es utilizable para una prueba controlada con las siete plantillas originales. No se ha validado en Windows ni se garantiza una paginación idéntica. Las comprobaciones automáticas verifican contenido y estructura del archivo; no equivalen a abrirlo en Microsoft Word.

## Problemas corregidos

- El plan de sesión acumulaba saltos de línea nuevos junto con párrafos vacíos antiguos. Ahora rellena los diez espacios numerados existentes, conservando su distribución de párrafos y el texto de material entregado.
- El reemplazo podía crear encabezados/pies vacíos al consultar variantes inexistentes. Ahora solo modifica las partes presentes.
- Un texto nuevo que contuviera el texto antiguo podía detener los reemplazos antes de cambiar todas las coincidencias. Ahora procesa únicamente las coincidencias originales.
- Al vaciar un campo se podían eliminar dibujos dentro de sus segmentos de texto. Se conservan los dibujos y las propiedades de formato.
- Un fallo al guardar podía dejar un lote Word incompleto. El modo básico elimina únicamente el lote recién creado si falla su escritura; no borra carpetas preexistentes.
- La interfaz llamaba a Tkinter desde un hilo de trabajo y podía cerrarse durante la generación. Ahora entrega las notificaciones mediante una cola que procesa el hilo principal y espera a que termine antes de cerrar.
- Los nombres de salida conservaban enero y el número antiguo de estación. Ahora contienen identificador de plantilla, estación y fecha, por ejemplo `P01_E-99999_20280229.docx`.
- El modo básico ahora verifica la huella de las siete plantillas originales. Si una se ha editado o es un documento previamente generado, rechaza el lote antes de guardarlo. La validación protege el mapeo específico de esta versión; no permite agregar plantillas nuevas sin adaptar el programa.
- El modo avanzado podía convertir cantidades decimales en enteros truncados. Ahora exige enteros positivos para copias, hojas, sesiones y duración.

También siguen vigentes las correcciones previas: inicialización/liberación de COM en PDF, detección de PDF ausente, desplazamiento vertical, rechazo de personal duplicado y controles de capacidad/sobrescritura.

## Lo que se cambia en modo básico

| Campo | Comportamiento |
|---|---|
| Fecha | La misma fecha para los siete documentos y las recepciones. Las fechas históricas de revisión se conservan. |
| Estación | Número en encabezados, cuerpo y códigos; nombre/razón social en el texto editable. |
| Personal | Lista de nombres y puestos en asistentes y receptores; lista del plan y su recuento. |
| Representante | Nombre en entrega y nota; convocante, facilitador y responsables de agenda usan la persona elegida. |
| Secretario | Nombre en el bloque de roles de las reuniones. |

El lote completo admite como máximo seis personas por la capacidad de la plantilla de difusión. La ventana muestra seis filas. La pertenencia al personal no prueba asistencia o recepción: quien genera debe confirmar esas participaciones.

## Datos que todavía se conservan y deben revisarse

Domicilio, correos, teléfonos, cargos SASISOPA, logotipos, horarios, temas, acuerdos, número de copias por receptor y el texto de la nota informativa permanecen como en los originales. En particular, la nota conserva la afirmación de que no hubo cambios de personal o estructura: el programa no comprueba ese hecho. Las cantidades originales se conservan en las filas ocupadas; el total de copias se recalcula. Una fila antes vacía no adquiere automáticamente una cantidad de copias.

Si la estación o las personas son diferentes, los contactos y el logotipo originales pueden no corresponder. El modo básico no pide esos datos. No usar el resultado como documento definitivo sin comprobarlos. Los originales deben copiarse desde el ZIP sin editar; si se requieren cambios de contenido fijo, hay que adaptar el programa o realizar una revisión posterior en las copias generadas.

El formulario básico no guarda su captura para la siguiente sesión. Guardar/cargar una captura es una mejora opcional pendiente. El Excel se conserva para el modo avanzado y como catálogo; no eliminarlo aunque se use solo el formulario.

## Evidencia y límites

- Se ejecutaron 15 pruebas automáticas y todas pasaron, sin omisiones, usando las siete plantillas reales y datos ficticios.
- Cubren generación, filas, imágenes, encabezados, fechas históricas, objetivos fijos, capacidad, duplicados, sobrescritura, párrafos del plan, año bisiesto, nombres de salida, plantillas modificadas, fallo de escritura, reemplazos entre segmentos, dibujos dentro de campos, cantidades enteras y limpieza de COM simulada.
- También se volvió a generar el conjunto de siete documentos del modo avanzado con una base ficticia.
- Se descargaron correctamente las dependencias binarias y sus dependencias transitivas para Windows x64 con Python 3.12. Esto confirma su disponibilidad, no una instalación o ejecución real en Windows.
- No se ejecutó Word ni se exportó un PDF real aquí. Las pruebas de COM son simulaciones.
- Falta ejecutar Instalar.bat/Iniciar.bat en Windows y revisar fuentes, textos largos, encabezados, alturas de filas, saltos de página y PDF.

## Cómo probar en Windows

Descarga una copia nueva del repositorio y extrae todo. Coloca los siete Word originales sin modificar en `plantillas`. Instala Python (3.12 es la versión usada para comprobar las dependencias) y ejecuta `Instalar.bat`, luego `Iniciar.bat`. Primero usa datos ficticios con nombres cortos; después prueba nombres largos y revisa los siete Word y PDF en Word. Conserva los documentos originales aparte.
