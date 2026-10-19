"""Project dates and initials from the current team, independently of revisions."""
ROLES=('representante_legal','representante_tecnico','encargado_estacion','jefe_operaciones','secretario_hazop','lider_hazop')
DATES=(('documento.fecha_inicio_estudio','Inicio del proyecto / estudio HAZOP'),('documento.fecha_fin_estudio','Fin del proyecto / estudio HAZOP'),('documento.fecha_sesion_hazop','Sesión HAZOP (opcional; usa inicio si está vacía)'))

def initials(name):
 return ''.join(next((letter for letter in word if letter.isalpha()),'').upper() for word in name.split())

def group_initials(data,role):
 """List each assigned person once, retaining distinct people with equal initials."""
 person_id=data['roles'].get(role)
 if not person_id:return ''
 for previous in ROLES:
  if previous==role:break
  if data['roles'].get(previous)==person_id:return ''
 person=next((p for p in data['people'] if p['id']==person_id),{})
 return initials(person.get('nombre',''))

def active(data):
 from instalaciones import enabled
 values=data['values'];overrides=data['documents'].get('II',{})
 return any(data['roles'].get(role) for role in ROLES) or enabled(data) or any(overrides.get(key,values.get(key,'')).strip() for key,label in DATES)
