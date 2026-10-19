"""Project dates and initials from the current team, independently of revisions."""
ROLES=('representante_legal','representante_tecnico','encargado_estacion','jefe_operaciones','secretario_hazop','lider_hazop')
DATES=(('documento.fecha_inicio_estudio','Inicio del proyecto / estudio HAZOP'),('documento.fecha_fin_estudio','Fin del proyecto / estudio HAZOP'),('documento.fecha_sesion_hazop','Sesión HAZOP (opcional; usa inicio si está vacía)'))

def initials(name):
 return ''.join(next((letter for letter in word if letter.isalpha()),'').upper() for word in name.split())

def active(data):return any(data['roles'].get(role) for role in ROLES)
