# SASISOPA 0.2.2 para Windows

**[Descargar todo junto en ZIP](https://github.com/misaelsainz9-glitch/COG/releases/download/v0.2.2/SASISOPA-COMPLETO-Windows.zip)**. Incluye el instalador, el proyecto, los `.bat`, instrucciones e informes. Extrae todo y ejecuta el instalador que viene dentro.

[Descargar instalador](https://github.com/misaelsainz9-glitch/COG/releases/download/v0.2.2/SASISOPA-Instalador-Windows.exe) · [Descargar código fuente](https://github.com/misaelsainz9-glitch/COG/archive/refs/tags/v0.2.2.zip)

Windows 10/11 de 64 bits. El instalador incluye Python y las dependencias; no necesita Word.

1. Instala y abre **SASISOPA** desde el menú Inicio.
2. En **Documentos → Importar SASISOPA.zip**, selecciona el ZIP original de los 18 procedimientos que compartiste.
3. Captura estación y personas, asigna sus funciones y sube el logo. Las firmas se pueden dibujar o subir como PNG/JPG.
4. Revisa la vista previa, guarda los datos y genera los documentos, separados o unidos.

El instalador no contiene los documentos privados. Conserva los datos al actualizar o desinstalar. Los logos y firmas externos deben mantenerse en sus rutas.

## Cambios incluidos

- Dirección de la estación alineada a la derecha.
- Firmas grandes en azul y con fondo transparente, dentro de los cuadros de elaboración, revisión y aprobación. Pueden tocar las letras sin borrar los textos fijos. No se imprimen nombres en esos cuadros.
- Listas de asistencia vacías, sin nombres, puestos, teléfonos ni firmas, incluso al cargar un perfil anterior.
- Vista previa, perfiles reutilizables, importación verificada y generación de PDF separados o unidos.

## Comprobaciones

- 70 pruebas del código, la ventana y los PDF completadas correctamente en el entorno de desarrollo. Se omitieron cinco grupos de versiones antiguas retiradas.
- Importación del ZIP original: los 18 PDF limpios coinciden con sus huellas registradas.
- Lote con datos ficticios: 18 procedimientos, 523 páginas y un PDF unido con 18 marcadores. Se comprobaron 1,197 firmas dentro de sus cuadros y 33 filas de asistencia vacías, además de las dimensiones de las páginas y los trazos originales de las tablas.
- En Windows pasaron la compilación, la instalación, la apertura del ejecutable instalado, la vista previa, el guardado/carga, el PDF, las firmas azules grandes, la asistencia vacía, la actualización y la desinstalación. Se conservaron los datos del usuario durante el ciclo.
- [Ejecución de Windows de la versión publicada](https://github.com/misaelsainz9-glitch/COG/actions/runs/38953752306). Los [informes del instalador](https://github.com/misaelsainz9-glitch/COG/releases/tag/v0.2.2) y su archivo SHA-256 acompañan a la descarga.
- Se descargó el instalador publicado (36,887,296 bytes) y su SHA-256 coincidió: `be7c34314182eccd1ef48fd5bf2f332e3c5f4fcbb55811249054d1dc6eb77a49`.

[Ver la prueba visual y sus resultados](prueba-estacion-completa.md).

## Límites que debes conocer

Un texto que excede su espacio detiene la generación con un aviso; no se recorta ni se entrega un lote incompleto. Los domicilios largos pueden requerir ajustar su ubicación, especialmente en la carta del procedimiento V y una página del XI.

El entorno de prueba emitió dos avisos de sustitución por Helvetica/Helvetica-Bold cuando la fuente original no contenía ciertos caracteres. Revisa esos textos en tu computadora. Las pruebas realizadas no permiten garantizar ausencia absoluta de errores en todas las computadoras y datos posibles.
