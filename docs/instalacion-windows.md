# Instalar SASISOPA en Windows

Descarga **SASISOPA-Instalador-Windows.exe** desde [las versiones del programa](https://github.com/misaelsainz9-glitch/COG/releases). Es para Windows 10/11 de 64 bits e incluye Python y las dependencias. No necesita Word ni ejecutar archivos `.bat`.

1. Ejecuta el instalador y sigue sus pasos. Se instala para tu usuario.
2. Abre **SASISOPA** desde el menú Inicio o el acceso directo que hayas elegido crear.
3. En **Documentos → Importar SASISOPA.zip**, selecciona el ZIP original que compartiste. El instalador no contiene tus documentos.
4. Captura los datos de estación; agrega personas y asigna sus funciones. Sube el logo y las firmas, o dibuja las firmas desde la ficha de la persona.
5. Revisa la vista previa. La dirección de la estación está alineada a la derecha. Los datos particulares sin posición requieren **Ubicar campo** una vez.
6. Pulsa **Guardar datos** y conserva tu archivo `.sasisopa18.json`. Genera los documentos y revisa el resultado antes de usarlo.

## Datos y actualizaciones

Las carpetas predeterminadas de plantillas importadas, resultados y preferencias están en `%LOCALAPPDATA%\SASISOPA\Datos`. Puedes elegir otra carpeta para los resultados y guardar perfiles donde prefieras. Las imágenes de logos y firmas se conservan en las rutas elegidas; no se incluyen dentro del perfil JSON.

Para actualizar, cierra el programa y ejecuta el instalador nuevo. La carpeta de datos está separada de la carpeta del programa y se conserva al actualizar o desinstalar. Conserva además copias de tus originales, perfiles e imágenes. Los perfiles antiguos `.sasisopa` no corresponden a este editor; usa `.sasisopa18.json`.

Si utilizabas el programa desde el código fuente, el instalador no mueve tus carpetas antiguas: vuelve a importar el ZIP, carga tu perfil `.sasisopa18.json` y selecciona las imágenes si sus rutas cambiaron.

Si el programa no puede iniciar, revisa `%LOCALAPPDATA%\SASISOPA\Datos\error_inicio.txt`.

## Alcance de la revisión

Las pruebas con datos ficticios no sustituyen confirmar los nombres, firmas, fechas y contenido técnico definitivos. La prueba en Windows alojado tampoco sustituye verificar el uso en la computadora particular del usuario.

El código fuente y los archivos `.bat` siguen disponibles como alternativa para desarrollo. El Excel del repositorio es un catálogo; este editor captura datos desde la ventana.
