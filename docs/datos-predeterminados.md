# Campos editables y predeterminados por proyecto

En Documentos, **Usar datos actuales como predeterminados** guarda una copia de los datos actuales dentro del proyecto. Una captura no vacía tiene prioridad. Un texto vacío usa el predeterminado guardado; si no existe, el espacio conserva la plantilla original. **Quitar valores predeterminados** permite volver a ese comportamiento original. Se guardan con el archivo `.sasisopa18.json` y no se comparten entre estaciones.

Instalaciones conserva la ficha de cada tanque, sus condiciones de operación y los equipos de despacho. Los campos vacíos de un tanque existente pueden heredar su ficha guardada; eliminar un tanque o cambiar su producto no recupera el tanque o las condiciones de otro combustible. Un cero explícito sigue siendo cero. Personas y Funciones permiten editar nombres, cargos y firmas y asignar los responsables del estudio. Las listas de asistencia permanecen vacías.

Los perfiles con ubicaciones adicionales muestran sus textos y resultados en Documentos. El filtro de página limita la captura a la página visible. Los párrafos tienen un editor de varias líneas; debajo se muestra el texto que se conservará si se dejan vacíos. Los campos marcados como comunes aparecen en **Datos comunes**: una captura se aplica a todas sus ubicaciones, conservando su numeración particular. Las imágenes con rutas relativas se buscan junto al archivo del proyecto.

El perfil entregado al destinatario puede incluir las celdas HAZOP, normativa aplicable, resultados, evaluaciones, brigadas, recursos y referencia de planos. Esas ubicaciones pertenecen al perfil: el programa no descubre por sí solo todos los campos de cualquier PDF. Los textos internos que corrigen códigos y preservan fechas no se ofrecen como campos de captura.

La captura modifica los espacios existentes y rechaza textos que no caben. No recalcula riesgos, acredita evaluaciones ni convierte datos predeterminados de ejemplo en información validada. Una referencia de plano no incorpora automáticamente el archivo del plano, ni crea un formato de registro que falte. Los ejemplos técnicos conservan su identificación como pendientes de revisión.

En los pasajes corregidos, vaciar un campo conserva el texto corregido definido en el perfil, incluso si se quitan los predeterminados generales. Así no reaparecen las instrucciones inseguras o los errores de la base anterior. Los avisos de revisión incluidos en el perfil también pueden editarse manualmente; capturar datos no los convierte automáticamente en una aprobación.
