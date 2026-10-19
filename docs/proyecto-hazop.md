# Proyecto, equipo y grupo multidisciplinario HAZOP

En **Documentos → Proyecto / estudio HAZOP** se capturan inicio y fin, en formato `dd/mm/aaaa`. Estas fechas pertenecen al estudio del procedimiento II y son independientes de la revisión del documento y de las reuniones. El programa rechaza un fin anterior al inicio.

La fecha opcional de sesión HAZOP llena las fechas de nodos y hojas de trabajo. Si queda vacía, esos espacios usan el inicio del estudio. La fecha de finalización se utiliza en su renglón correspondiente. No se cambian otras actividades que coincidan casualmente con las fechas de la plantilla, como las capacitaciones del procedimiento VIII.

En **Personas** se capturan nombre completo, puesto y empresa. En **Funciones** se asignan los integrantes a representante legal, representante técnico, encargado de estación, jefe de operaciones, secretario HAZOP y líder HAZOP. El cuadro de miembros usa esos datos en sus seis filas; los nombres aprovechan la casilla completa y cada dato se mantiene dentro de su columna. Cuando se está llenando el equipo, un dato faltante indica «Pendiente» en lugar de conservar una compañía del ejemplo. Para los primeros cuatro cargos, la razón social de la estación sigue siendo el respaldo de empresa si no se captura una empresa particular.

El **grupo multidisciplinario** se llena con las iniciales del nombre completo de esas personas. Ejemplo ficticio: **Ulises Hernández Cruz → UHC**. Se toma la primera letra de cada palabra; **Ana María López Pérez → AMLP**. Conviene capturar nombres sin títulos profesionales. Las iniciales se muestran automáticamente en la ficha personal, no se editan manualmente y se recalculan cuando cambia el nombre, incluso si un perfil anterior contiene iniciales distintas.

Con Instalaciones activadas, los nodos y apartados HAZOP de un combustible ausente indican «No aplica». No se insertan en ellos fechas de sesión ni iniciales del equipo. Se conservan los encabezados, bordes y cuadros de firmas. Las listas de asistencia siguen vacías.

El llenado de datos no recalcula ni certifica las valoraciones técnicas de riesgo de los productos presentes.

Las ubicaciones del equipo se identifican sin duplicados. Se conserva la compatibilidad de las ubicaciones personalizadas anteriores mediante sus identificadores históricos.

Estos cambios están en el proyecto actualizado. El ZIP y el instalador v0.2.2 anteriores todavía no los incluyen.

Verificación: la suite general terminó con 95 pruebas sin fallos y cinco omisiones de plantillas retiradas. Después del ajuste de compatibilidad de ubicaciones se ejecutaron las siete pruebas específicas del equipo y fechas, también sin fallos. Incluyen generación completa de II, ausencia de las fechas anteriores del estudio, iniciales derivadas del nombre, empresas faltantes, combustibles ausentes, conservación de bordes y compatibilidad de perfiles. La prueba real de interfaz comprueba la captura de fechas y las iniciales automáticas de una persona nueva.
