# BASE ACTIVA: SASISOPA1 — TRES PDF, 87 PÁGINAS

Se reemplazó el catálogo anterior por Política (14 páginas), Identificación de peligros (53) y Requisitos legales (20). La interfaz selecciona uno o varios documentos y permite crear también un PDF unificado en orden del catálogo. El Excel se actualizó como catálogo; la captura activa se hace en el formulario.

Los mapas se calibraron sobre los tres originales recibidos y contienen geometría/códigos estructurales, no el contenido privado del PDF. Se verifica SHA-256 antes de editar. Los originales y los resultados reales permanecen fuera de GitHub. Las copias locales de los originales están excluidas de Git.

Se verificaron las 87 páginas: orientación y dimensiones, trazos vectoriales de las tablas, cambio de estación/empresa y conservación de cada carácter sin editar en su posición. Se corrigieron referencias corporativas y códigos divididos en distintos fragmentos de fuente, la selección del nombre de AUTORIZO y límites de dirección/firma que podían alcanzar títulos o etiquetas cercanas. Se revisaron renderizados de portadas, asistencia, matriz y requisitos.

La suite completa terminó con 40 pruebas aprobadas y cuatro grupos de integración omitidos explícitamente (tres de Word y el PDF de Política retirado). Las pruebas actuales incluyen copias idénticas byte por byte con todos los campos vacíos, conservación selectiva de fechas/puestos/revisión/filas, selección, unión de 87 páginas, originales intactos, logo proporcional, firmas en los espacios existentes, diagramas conservados, entradas inválidas, fuentes faltantes/alteradas y limpieza del lote ante error de escritura.

Las firmas/sellos antiguos se retiran de la copia al capturar estación, empresa o nombres; se mantienen sin esos cambios. Las firmas nuevas se colocan en las listas de Política y en los espacios del representante/autoriza existentes. Los otros bloques históricos de elaboración/revisión/aprobación y los nombres del equipo técnico del análisis de riesgo se conservan: no existe aún una asignación de personas a esos roles técnicos.

La instalación y la interacción de la ventana en Windows siguen pendientes de prueba real. Las pruebas se ejecutaron aquí en Linux. Los informes que siguen son históricos y sus catálogos/resultados no describen esta base activa.

---

# ACTUALIZACIÓN: CONSERVAR CAMPOS SIN CAPTURA

Los campos vacíos ahora conservan el original: fecha de reunión opcional sin precarga, puestos independientes de nombres y filas sin compactar. La última suite pasó 38 pruebas y omitió tres grupos retirados de Word. Se añadieron pruebas de igualdad del texto y píxeles renderizados de las 14 páginas cuando todos los campos quedan vacíos, y de conservación selectiva de fechas, puestos y revisión.

Las firmas anteriores se conservan si no cambia estación ni nombres; se retiran si cambia esa identidad. Las imágenes nuevas sustituyen las del representante en sus espacios. Las afirmaciones históricas de obligatoriedad de fechas/puestos y retiro incondicional de firmas quedan sustituidas por esta actualización.

---

# ESTADO ACTUAL: GENERACIÓN NATIVA DE POLÍTICA EN PDF

El usuario confirmó que solo tiene el PDF. Se adaptó el programa para generar directamente una copia de PROCEDIMIENTO I.pdf de 14 páginas. Las siete plantillas anteriores siguen retiradas. El formulario permite cinco asistentes, encabezados, datos y firmas en listas y espacios del representante legal. No requiere Word para generar el PDF.

Se verificó que las imágenes antiguas de firmas/sellos se retiran de la copia y que se conservan las páginas y los trazos vectoriales de las tablas. Se usa texto nuevo en espacios fijos y se rechaza el exceso de longitud. Los bloques genéricos de elaboración/revisión/aprobación quedan sin imágenes de firma; sus asignaciones no están implementadas. Los datos fijos del procedimiento y el historial siguen requerir revisión del usuario.

La última suite ejecutó 35 pruebas aprobadas y omitió tres grupos de integración de Word retirados. Las siete pruebas del nuevo PDF comprobaron el archivo real con datos/imágenes ficticios, incluidos layout vectorial, texto, imágenes, firmas, original intacto y errores de entrada. Se corrigieron durante la implementación una región de fecha que podía tocar la etiqueta Hora y el ajuste proporcional de imágenes. Se validó la conservación geométrica y de color de las líneas, sin comparar identificadores internos de orden de dibujo que cambian al editar texto.

Se comprobó la disponibilidad de PyMuPDF 1.26.6 para Windows x64/Python 3.12. La interfaz gráfica y la instalación en Windows siguen pendientes de prueba real; se inspeccionaron renderizados de portada y difusión aquí en Linux. Los informes siguientes son históricos y algunos describen fases anteriores.

---

# ESTADO ACTUAL: NUEVA BASE PDF

El catálogo anterior fue retirado por solicitud del usuario. Ahora solo se registra POL-I, PROCEDIMIENTO I.pdf, del ZIP 1. POLITICA. El original tiene 14 páginas, no contiene campos rellenables ni archivos Word.

El llenado de la nueva base no está habilitado ni validado. Se deshabilitó el botón de generación en ambos formularios mientras se confirma el formato de trabajo y se preparan los campos. Se conservaron los perfiles y la interfaz. No se publicó el PDF privado.

Las comprobaciones actuales cubren la identidad/páginas/ausencia de campos del PDF, el retiro del catálogo anterior y el bloqueo de generación. Las pruebas de utilidades/perfiles permanecen; tres grupos que dependían de las plantillas antiguas ahora se omiten explícitamente. Los resultados siguientes son históricos y no prueban la automatización del nuevo PDF.

---

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

- Se ejecutaron 20 pruebas automáticas y todas pasaron, sin omisiones, usando las siete plantillas reales y datos ficticios.
- Cubren generación, filas, imágenes, encabezados, fechas históricas, objetivos fijos, capacidad, duplicados, sobrescritura, párrafos del plan, año bisiesto, nombres de salida, plantillas modificadas, fallo de escritura, reemplazos entre segmentos, dibujos dentro de campos, cantidades enteras y limpieza de COM simulada.
- También se volvió a generar el conjunto de siete documentos del modo avanzado con una base ficticia.
- Se descargaron correctamente las dependencias binarias y sus dependencias transitivas para Windows x64 con Python 3.12. Esto confirma su disponibilidad, no una instalación o ejecución real en Windows.
- No se ejecutó Word ni se exportó un PDF real aquí. Las pruebas de COM son simulaciones.
- Falta ejecutar Instalar.bat/Iniciar.bat en Windows y revisar fuentes, textos largos, encabezados, alturas de filas, saltos de página y PDF.

## Cómo probar en Windows

Descarga una copia nueva del repositorio y extrae todo. Coloca los siete Word originales sin modificar en `plantillas`. Instala Python (3.12 es la versión usada para comprobar las dependencias) y ejecuta `Instalar.bat`, luego `Iniciar.bat`. Primero usa datos ficticios con nombres cortos; después prueba nombres largos y revisa los siete Word y PDF en Word. Conserva los documentos originales aparte.

## Revisión adicional

Se corrigió también la escritura del modo avanzado: si falla un documento se retiran solo los archivos nuevos de ese lote, conservando los archivos previos de la carpeta. Se usa creación exclusiva para evitar sobrescrituras incluso si un archivo aparece después de validar los nombres.

Se añadieron mensajes claros cuando falta el Excel, falta la hoja Plantillas, un nombre de plantilla está vacío o falta el archivo de compatibilidad. Se cerró explícitamente el libro después de leer los datos del modo avanzado. Cinco nuevas pruebas comprueban estos casos y la conservación de archivos anteriores. El total actual es de 20 pruebas aprobadas sin omisiones con las siete plantillas locales.

No se han descubierto otros bloqueos en los caminos ejecutados. La ejecución real en Windows, el PDF con Word y la inspección visual continúan pendientes; las pruebas aquí no permiten certificar esas capacidades.

## Encabezados y firmas — actualización más reciente

El formulario básico ahora permite dirección y logo; el logo se sustituye en el encabezado manteniendo su proporción dentro del espacio original. También permite número de revisión y fecha de revisión opcionales; el formato original presenta mes/año, y la nota informativa no tiene ese bloque. Las fechas históricas de los bloques de elaboración/revisión del cuerpo se conservan.

Cada persona puede seleccionar una firma PNG/JPG o dibujarla con el mouse. El dibujo se guarda en un PNG transparente en la ubicación que elija el usuario. Se rechaza un dibujo vacío y una imagen inválida. La captura no toma una imagen de la pantalla. Las firmas permanecen como archivos locales y se insertan como imágenes.

Los destinos actualmente implementados son: seis receptores y quien entrega en P01, seis asistentes en P04 y representante de la nota P03. P02, P05, P06 y P07 no tienen campo explícito de firma: está pendiente acordar su ubicación. No se cambia una columna de teléfono o correo para insertar una firma.

Las afirmaciones anteriores sobre domicilio y logo fijos quedan actualizadas: ahora se conservan únicamente cuando esos campos se dejan vacíos. Los nuevos controles pertenecen al modo básico; el avanzado conserva su flujo de Excel. La interfaz de dibujo, el posicionamiento visual en Word y el PDF real siguen pendientes de prueba en Windows.

La última ejecución terminó con **27 pruebas aprobadas, sin omisiones**. Se agregaron pruebas de dibujo vacío, límites de coordenadas, PNG con transparencia, sustitución de logo con proporción, dirección/revisión, firmas en los espacios previstos, conservación de párrafos/filas, imágenes ausentes/incorrectas y modo sin imágenes de firma. Se utilizaron datos e imágenes ficticios, sin publicar los documentos o firmas reales.

## Revisión del encabezado e integridad de imágenes

Se reprodujo y corrigió una imagen PNG con datos dañados que antes pasaba la lectura de metadatos. Ahora se verifica su integridad y se decodifica antes de insertarla como logo o firma. Una imagen dañada se rechaza antes de guardar el lote.

Se corrigió la incoherencia entre el número de revisión visible y el código documental: introducir revisión 3 actualiza tanto el número como el sufijo `.R3`. Se aceptan enteros no negativos; un valor como 3.5 se rechaza. La nota informativa no tiene bloque de revisión y conserva ese diseño.

La última ejecución terminó con **29 pruebas aprobadas, sin omisiones**, con las siete plantillas locales. Incluye las pruebas nuevas que reproducen el PNG dañado y la revisión inválida, además de comprobar el sufijo de revisión en los códigos.

Se confirmó la preferencia del usuario por firmas únicamente en los espacios existentes. No queda pendiente agregar bloques a las otras cuatro plantillas: se mantienen sin ellos. La instalación y el dibujo con mouse en Windows, la exportación real con Word y la inspección visual siguen sin ejecutarse en este entorno.

## Adaptación visual aprobada

Se añadió tema.py y se reorganizó el formulario básico en Datos de la estación, Personal y firmas y Configuración de archivos. Se añadió vista previa local del logo y validación inmediata de las imágenes seleccionadas. Las funciones de generación y sus destinos de firma no cambiaron. Se compiló la interfaz y las 29 pruebas existentes pasaron; la interacción y distribución gráfica en Windows permanecen pendientes de comprobación.

## Perfiles de estación

Se añadieron los botones Guardar estación y Cargar estación. Cada perfil local `.sasisopa` contiene los datos del encabezado, seis filas de personal, las selecciones de representante/secretario y copias de logo/firmas. Se conservan las filas vacías, por lo que admite borradores. No conserva la fecha de reunión ni cambia carpetas de trabajo al cargarlo.

El guardado escribe primero un archivo temporal y reemplaza el destino solo al terminar. La carga verifica el formato y las imágenes antes de recuperar archivos locales; no extrae rutas arbitrarias del ZIP. Se comprobaron ocho casos nuevos, incluyendo recuperación después de eliminar las imágenes originales y conservación de un perfil anterior cuando falla el guardado. **37 pruebas pasaron sin omisiones** con las plantillas locales. Esta actualización sustituye la limitación anterior de que el formulario no guardaba datos.

Pendiente: interacción real con los diálogos Guardar/Cargar en Windows, además de Word/PDF y revisión visual de documentos.
