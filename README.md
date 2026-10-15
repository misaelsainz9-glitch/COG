# SASISOPA — 18 documentos y vista previa

La aplicación de Windows trabaja con los **18 procedimientos del nuevo SASISOPA.zip: 523 páginas**. Permite capturar estación, personas y funciones; ver el PDF real; reutilizar ubicaciones de campos y generar documentos separados o un PDF unido.

## Descargar y empezar

**[Descargar instalador para Windows](https://github.com/misaelsainz9-glitch/COG/releases/latest/download/SASISOPA-Instalador-Windows.exe)** — Windows 10/11 de 64 bits. Incluye Python y los componentes necesarios.

1. Ejecuta **SASISOPA-Instalador-Windows.exe** y abre **SASISOPA** desde el menú Inicio.
2. En **Documentos → Importar SASISOPA.zip**, selecciona el ZIP original que compartiste; también se admite la copia limpia actualizada.
3. Captura tus datos, revisa la vista previa y pulsa **Guardar datos** para conservar tu perfil.
4. Genera los PDF seleccionados y, si lo deseas, el PDF unido de 523 páginas.

El instalador no incluye tus PDF. Los datos se guardan por defecto en `%LOCALAPPDATA%\SASISOPA\Datos`, separados del programa para conservarlos al actualizar o desinstalar. Consulta [las instrucciones de instalación](docs/instalacion-windows.md).

Para trabajar desde el código fuente: [descarga el repositorio](https://github.com/misaelsainz9-glitch/COG/archive/refs/heads/main.zip), extrae todo, instala Python 3.12 o posterior, ejecuta **Instalar.bat** y abre **Iniciar.bat**. Esta alternativa conserva sus carpetas locales y no requiere el instalador.

Este modo no requiere Word. Los PDF originales, resultados, firmas, logos y datos reales permanecen en tu computadora y no se publican en GitHub. La importación verifica los archivos y reproduce la limpieza validada; no procesa automáticamente versiones diferentes del SASISOPA.

## Capturar los datos

- **Estación:** número `E-00000`, razón social, dirección, localidad, estado, código postal, teléfono, correo y logo. Localidad/estado/código postal se integran en la dirección si se capturan por separado. Revisión y fecha de revisión son opcionales.
- **Personas:** agrega las necesarias, con nombre, puesto, iniciales, empresa, contacto, domicilio para notificaciones y firma. Puedes subir PNG/JPG o dibujar la firma con el mouse.
- **Funciones:** selecciona a la persona de cada función. Una persona puede ocupar varias funciones; los cargos se asignan por separado. Selecciona **Autoriza** para las portadas y los bloques de aprobación, aunque sea la misma persona que el representante legal. Alta dirección y representante legal no se deducen uno del otro.
- **Documentos:** marca cuáles generar, elige si quieres también el PDF unido y captura los datos particulares del documento que estás viendo. Las fechas de revisión, reunión, designación y aceptación son independientes. Una revisión particular se aplica a su documento y a las referencias identificadas a esa versión; no cambia automáticamente la versión de otros procedimientos.
- **Listas:** selecciona una lista detectada y asigna personas por fila. Sus datos y firmas se toman de la ficha de la persona, de modo que corregir un nombre actualiza sus filas vinculadas. También puedes dejar la selección vacía y escribir la fila manualmente.

Los campos vacíos conservan el contenido de la **base limpia**: no recuperan nombres ni firmas retirados. Se conservan puestos, fechas históricas, horarios y textos fijos salvo cuando capturas un cambio en un campo asignado. Las firmas se colocan únicamente en espacios existentes. Las tablas mantienen su capacidad: no se agregan filas ni bloques de firma.

## Qué se coloca automáticamente

Los mapas incluyen el número de estación en encabezados, portadas, cuerpo, códigos e índices; razón social y dirección en sus bloques; logo; revisión y fecha de revisión; nombres previamente identificados por su función, incluido el organigrama y el equipo HAZOP; iniciales de ese equipo; contacto/domicilio del representante técnico; fechas de sus cartas y las listas de personas detectadas. También se prepararon los datos de los encabezados incrustados en imágenes de tres cronogramas.

Los nombres del equipo HAZOP se asignan a representante legal, representante técnico, encargado, jefe de operaciones, secretario técnico HAZOP y líder HAZOP. Sus empresas son datos propios; las cuatro funciones de la estación pueden usar la razón social como valor común si no indicas otra. Las empresas externas del ejemplo permanecen si no capturas un cambio.

El domicilio y contacto del representante técnico no se copian automáticamente del domicilio y contacto de la estación. Las iniciales se capturan o confirman en la ficha: no se heredan del ejemplo.

## Campos particulares: ubicar una vez y reutilizar

No todos los formatos tienen las mismas casillas. Los campos sin ubicación predefinida —por ejemplo CURP/RFC/NSS, otros folios o datos de un evento— se configuran desde la vista previa:

1. Elige el documento y su página. En **Documentos**, captura el dato o pulsa **Agregar otro dato al documento**.
2. Elige ese dato en **Campo**, activa **Ubicar campo** y arrastra sobre su espacio existente en la página.
3. Comprueba la vista previa. Puedes ajustar el tamaño de letra con el control disponible.
4. Pulsa **Guardar datos** para conservar valores, funciones y ubicaciones. Al generar otra vez se colocarán automáticamente en esas ubicaciones.

Para mover una ubicación existente, haz clic sobre ella en la página, activa **Ubicar campo** y marca su nueva zona. El espacio anterior se limpia cuando se coloca el nuevo valor. **Quitar ubicación marcada** retira una ubicación personalizada y restaura la original, si la había.

Si capturas un dato común o particular sin destino, la aplicación lo señala y detiene la generación: no lo ignora silenciosamente. Usa **Mostrar espacios editables** y el zoom para revisar. Cuando un texto no cabe, se muestra la base para que puedas corregirlo o ajustar el espacio.

## Tipografía y contenido

En los encabezados habituales se usa Arial 9 en empresa/dirección, con negrita donde corresponde. La dirección de la estación se alinea a la derecha dentro de su bloque; ajusta líneas y puede reducirse hasta 8 puntos; si no cabe, se rechaza. Las portadas y los nombres ya presentes conservan su estilo de referencia. Los nombres añadidos en los espacios libres de los pies usan 8 puntos. Los títulos, bordes y contenido técnico se conservan.

El programa intenta usar las fuentes originales embebidas y las fuentes instaladas en Windows. Si la fuente del PDF es un subconjunto sin algún carácter nuevo, utiliza una alternativa disponible y lo avisa en la vista previa y en `revision_del_lote.json`. Instalar la fuente original completa puede evitar esa sustitución. No se garantiza identidad tipográfica si falta esa fuente.

Las matrices de riesgo, indicadores, resultados, hallazgos, calendarios, obligaciones legales y contactos públicos de emergencia no se recalculan por cambiar la estación. Sus datos particulares requieren captura/revisión expresa. Tampoco se presupone que una reunión, auditoría o firma haya ocurrido.

## Guardar y cargar

**Guardar datos/Cargar datos** utiliza un archivo `.sasisopa18.json`. Conserva valores, personas, asignaciones, filas vinculadas y ubicaciones. Las imágenes se referencian por su ruta: conserva esos archivos o vuelve a seleccionarlos si los mueves. Guarda una copia por estación si quieres reutilizar su diseño y sus datos.

Los perfiles `.sasisopa` de las versiones antiguas tienen otro formato y no se importan en este editor; se conservan intactos. El Excel se actualizó como catálogo de los 18 PDF, pero este modo no importa sus hojas de datos ni genera lotes desde Excel.

## Verificación y límites

Las pruebas usan los 18 PDF privados localmente. Cubren importación del ZIP original a las huellas exactas de la base limpia, copia idéntica con campos vacíos, unión de 523 páginas, geometría y trazos de tablas, funciones independientes, organigrama, iniciales, fechas, listas vinculadas, imágenes, campos personalizados y errores sin lotes parciales ni sobrescritura. También se ejercitaron la ventana Tk real y acciones de captura/guardado/generación en una pantalla virtual de Linux.

**Windows verificado:** [ejecución de GitHub Actions](https://github.com/misaelsainz9-glitch/COG/actions/runs/38791522490) en `windows-latest` con Python 3.12: 45 pruebas, 34 aprobadas y 11 omitidas, sin fallos. Se ejecutó `Instalar.bat` y se comprobó una ventana Tk real, captura, vista previa, guardado y generación con un PDF ficticio. Se corrigió la extracción del guion en números de estación con Arial de Windows. Los 18 PDF privados no se suben a ese equipo; su integración completa se verifica localmente en Linux. Esto no equivale a una prueba en la computadora particular del usuario.

```bat
set "SASISOPA18_BASE=C:\ruta\a\los\18\pdf\limpios"
set "SASISOPA18_ZIP=C:\ruta\SASISOPA.zip"
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Los grupos de integración de las bases retiradas se omiten explícitamente. Las pruebas gráficas requieren una pantalla; se omiten si no existe `DISPLAY`. Consulta [el inventario por documento](docs/campos-sasisopa-18.md) y [REVISION.md](REVISION.md). Las imágenes antiguas de propuesta son ilustraciones, no capturas de la versión final.
