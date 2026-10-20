"""Project-local defaults; empty text inherits, explicit inventory removals do not."""
import copy

SECTIONS=('values','documents','people','roles','installation')

def snapshot(data):
 return {key:copy.deepcopy(data.get(key)) for key in SECTIONS}

def effective(data):
 result=copy.deepcopy(data);defaults=result.pop('defaults',None)
 if not defaults:return result
 def texts(current,base):
  return {key:(current.get(key,'').strip() or base.get(key,'')) for key in dict.fromkeys([*base,*current])}
 result['values']=texts(result['values'],defaults.get('values') or {})
 for doc in dict.fromkeys([*(defaults.get('documents') or {}),*result['documents']]):
  result['documents'][doc]=texts(result['documents'].get(doc,{}),(defaults.get('documents') or {}).get(doc,{}))
 people={p['id']:p for p in defaults.get('people') or []}
 for person in result['people']:
  base=people.get(person['id'],{});person.update(texts(person,base))
 for role,person_id in (defaults.get('roles') or {}).items():
  if not result['roles'].get(role) and person_id in people:
   result['roles'][role]=person_id
   if not any(p['id']==person_id for p in result['people']):result['people'].append(copy.deepcopy(people[person_id]))
 inv=result.get('installation');base=defaults.get('installation') or {}
 if inv:
  tanks={t.get('numero'):t for t in base.get('tanks',[])}
  for tank in inv.get('tanks',[]):
   # A different fuel or a removed tank is intentional, never resurrect it.
   previous=tanks.get(tank.get('numero'),{})
   if previous.get('producto')==tank.get('producto'):tank.update(texts(tank,previous))
  for product,fields in inv.get('equipment',{}).items():
   if product in {t.get('producto') for t in inv.get('tanks',[])}:fields.update(texts(fields,base.get('equipment',{}).get(product,{})))
 return result
