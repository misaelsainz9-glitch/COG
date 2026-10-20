"""Doce meses móviles; solo cambian las cabeceras, no las actividades ni sus marcas."""
from datetime import datetime
import fitz
MONTHS=('ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC')
NAVY=(0,32/255,96/255)
REGIONS={('VI', 29): {'format': 'initial',
              'size': 11.04,
              'months': [{'rect': [307.092, 232.219, 325.092, 244.528],
                          'erase': [312.41, 232.219, 319.774, 244.528]},
                         {'rect': [329.412, 232.219, 347.412, 244.528],
                          'erase': [334.73, 232.219, 342.094, 244.528]},
                         {'rect': [352.365, 232.219, 370.365, 244.528],
                          'erase': [357.07, 232.219, 365.659, 244.528]},
                         {'rect': [375.935, 232.219, 393.935, 244.528],
                          'erase': [380.95, 232.219, 388.921, 244.528]},
                         {'rect': [399.695, 232.219, 417.695, 244.528],
                          'erase': [404.71, 232.219, 412.681, 244.528]},
                         {'rect': [422.432, 232.219, 440.432, 244.528],
                          'erase': [427.75, 232.219, 435.114, 244.528]},
                         {'rect': [445.163, 232.219, 463.163, 244.528],
                          'erase': [450.79, 232.219, 457.535, 244.528]},
                         {'rect': [468.708, 232.219, 486.708, 244.528],
                          'erase': [473.11, 232.219, 482.306, 244.528]},
                         {'rect': [492.422, 232.219, 510.422, 244.528],
                          'erase': [497.74, 232.219, 505.104, 244.528]},
                         {'rect': [517.818, 232.219, 535.818, 244.528],
                          'erase': [522.22, 232.219, 531.416, 244.528]},
                         {'rect': [540.58, 232.219, 558.58, 244.528], 'erase': [546.82, 232.219, 552.34, 244.528]},
                         {'rect': [564.94, 232.219, 582.94, 244.528],
                          'erase': [571.18, 232.219, 576.7, 244.528]}]},
 ('VI', 30): {'format': 'initial',
              'size': 11.04,
              'months': [{'rect': [289.332, 271.819, 307.332, 284.128],
                          'erase': [294.65, 271.819, 302.014, 284.128]},
                         {'rect': [312.492, 271.819, 330.492, 284.128],
                          'erase': [317.81, 271.819, 325.174, 284.128]},
                         {'rect': [335.545, 271.819, 353.545, 284.128],
                          'erase': [340.25, 271.819, 348.839, 284.128]},
                         {'rect': [358.535, 271.819, 376.535, 284.128],
                          'erase': [363.55, 271.819, 371.521, 284.128]},
                         {'rect': [381.575, 271.819, 399.575, 284.128],
                          'erase': [386.59, 271.819, 394.561, 284.128]},
                         {'rect': [403.712, 271.819, 421.712, 284.128],
                          'erase': [409.03, 271.819, 416.394, 284.128]},
                         {'rect': [427.283, 271.819, 445.283, 284.128],
                          'erase': [432.91, 271.819, 439.655, 284.128]},
                         {'rect': [450.228, 271.819, 468.228, 284.128],
                          'erase': [454.63, 271.819, 463.826, 284.128]},
                         {'rect': [473.312, 271.819, 491.312, 284.128],
                          'erase': [478.63, 271.819, 485.994, 284.128]},
                         {'rect': [497.778, 271.819, 515.778, 284.128],
                          'erase': [502.18, 271.819, 511.376, 284.128]},
                         {'rect': [519.94, 271.819, 537.94, 284.128], 'erase': [526.18, 271.819, 531.7, 284.128]},
                         {'rect': [543.58, 271.819, 561.58, 284.128],
                          'erase': [549.82, 271.819, 555.34, 284.128]}]},
 ('VI', 44): {'format': 'vertical',
              'size': 9.96,
              'months': [{'rect': [266.916, 272, 278.022, 325], 'erase': [266.916, 287.029, 278.022, 309.17]},
                         {'rect': [293.676, 272, 304.782, 325], 'erase': [293.676, 288.13, 304.782, 308.09]},
                         {'rect': [329.196, 272, 340.302, 325], 'erase': [329.196, 287.505, 340.302, 308.57]},
                         {'rect': [353.576, 272, 364.682, 325], 'erase': [353.576, 287.297, 364.682, 308.93]},
                         {'rect': [377.936, 272, 389.042, 325], 'erase': [377.936, 289.499, 389.042, 306.65]},
                         {'rect': [402.176, 272, 413.282, 325], 'erase': [402.176, 287.892, 413.282, 308.33]},
                         {'rect': [426.536, 272, 437.642, 325], 'erase': [426.536, 288.378, 437.642, 307.73]},
                         {'rect': [450.896, 272, 462.002, 325], 'erase': [450.896, 287.099, 462.002, 309.17]},
                         {'rect': [475.286, 272, 486.392, 325], 'erase': [475.286, 287.939, 486.392, 308.33]},
                         {'rect': [499.646, 272, 510.752, 325], 'erase': [499.646, 287.297, 510.752, 308.93]},
                         {'rect': [524.006, 272, 535.112, 325], 'erase': [524.006, 288.318, 535.112, 307.73]},
                         {'rect': [548.366, 272, 559.472, 325], 'erase': [548.366, 289.131, 559.472, 306.89]}]},
 ('XIV', 9): {'format': 'initial',
              'size': 8.04,
              'months': [{'rect': [424.071, 183.664, 442.071, 192.628],
                          'erase': [430.39, 183.664, 435.753, 192.628]},
                         {'rect': [452.871, 183.664, 470.871, 192.628],
                          'erase': [459.19, 183.664, 464.553, 192.628]},
                         {'rect': [479.958, 183.664, 497.958, 192.628],
                          'erase': [485.83, 183.664, 492.085, 192.628]},
                         {'rect': [507.482, 183.664, 525.482, 192.628],
                          'erase': [513.58, 183.664, 519.385, 192.628]},
                         {'rect': [534.722, 183.664, 552.722, 192.628],
                          'erase': [540.82, 183.664, 546.625, 192.628]},
                         {'rect': [561.501, 183.664, 579.501, 192.628],
                          'erase': [567.82, 183.664, 573.183, 192.628]},
                         {'rect': [587.436, 183.664, 605.436, 192.628],
                          'erase': [593.98, 183.664, 598.892, 192.628]},
                         {'rect': [614.609, 183.664, 632.609, 192.628],
                          'erase': [620.26, 183.664, 626.957, 192.628]},
                         {'rect': [642.281, 183.664, 660.281, 192.628],
                          'erase': [648.6, 183.664, 653.963, 192.628]},
                         {'rect': [669.709, 183.664, 687.709, 192.628],
                          'erase': [675.36, 183.664, 682.057, 192.628]},
                         {'rect': [696.21, 183.664, 714.21, 192.628], 'erase': [703.2, 183.664, 707.22, 192.628]},
                         {'rect': [720.33, 183.664, 738.33, 192.628],
                          'erase': [727.32, 183.664, 731.34, 192.628]}],
              'year_range': [555.0876, 167.4638, 593.2904, 176.4284]},
 ('XI', 14): {'format': 'abbreviated',
              'raster': True,
              'size': 4.2,
              'months': [{'rect': [325.575, 94.15, 363.925, 98.65]},
                         {'rect': [364.825, 94.15, 394.675, 98.65]},
                         {'rect': [395.575, 94.15, 427.925, 98.65]},
                         {'rect': [428.825, 94.15, 460.925, 98.65]},
                         {'rect': [461.825, 94.15, 496.675, 98.65]},
                         {'rect': [497.575, 94.15, 531.425, 98.65]},
                         {'rect': [532.325, 94.15, 565.925, 98.65]},
                         {'rect': [566.825, 94.15, 600.675, 98.65]},
                         {'rect': [601.575, 94.15, 629.925, 98.65]},
                         {'rect': [630.825, 94.15, 659.175, 98.65]},
                         {'rect': [660.075, 94.15, 686.425, 98.65]},
                         {'rect': [687.325, 94.15, 715.675, 98.65]}],
              'year_band': [325.525, 89.1, 715.725, 93.65],
              'bounds': [325.125,
                         364.375,
                         395.125,
                         428.375,
                         461.375,
                         497.125,
                         531.875,
                         566.375,
                         601.125,
                         630.375,
                         659.625,
                         686.875,
                         716.125]},
 ('XIII', 15): {'format': 'abbreviated',
                'raster': True,
                'size': 7,
                'months': [{'rect': [259.075, 142.85, 302.05, 152.15]},
                           {'rect': [302.95, 142.85, 345.925, 152.15]},
                           {'rect': [346.825, 142.85, 389.675, 152.15]},
                           {'rect': [390.575, 142.85, 433.425, 152.15]},
                           {'rect': [434.325, 142.85, 477.175, 152.15]},
                           {'rect': [478.075, 142.85, 520.925, 152.15]},
                           {'rect': [521.825, 142.85, 564.8, 152.15]},
                           {'rect': [565.7, 142.85, 608.675, 152.15]},
                           {'rect': [609.575, 142.85, 652.425, 152.15]},
                           {'rect': [653.325, 142.85, 696.175, 152.15]},
                           {'rect': [697.075, 142.85, 739.925, 152.15]},
                           {'rect': [740.825, 142.85, 785.55, 152.15]}],
                'year_band': [259.025, 133.1, 785.6, 142.2],
                'bounds': [258.625,
                           302.5,
                           346.375,
                           390.125,
                           433.875,
                           477.625,
                           521.375,
                           565.25,
                           609.125,
                           652.875,
                           696.625,
                           740.375,
                           786]},
 ('XIII', 69): {'format': 'abbreviated',
                'raster': True,
                'size': 7,
                'months': [{'rect': [259.075, 142.85, 302.05, 152.15]},
                           {'rect': [302.95, 142.85, 345.925, 152.15]},
                           {'rect': [346.825, 142.85, 389.675, 152.15]},
                           {'rect': [390.575, 142.85, 433.425, 152.15]},
                           {'rect': [434.325, 142.85, 477.175, 152.15]},
                           {'rect': [478.075, 142.85, 520.925, 152.15]},
                           {'rect': [521.825, 142.85, 564.8, 152.15]},
                           {'rect': [565.7, 142.85, 608.675, 152.15]},
                           {'rect': [609.575, 142.85, 652.425, 152.15]},
                           {'rect': [653.325, 142.85, 696.175, 152.15]},
                           {'rect': [697.075, 142.85, 739.925, 152.15]},
                           {'rect': [740.825, 142.85, 785.55, 152.15]}],
                'year_band': [259.025, 133.1, 785.6, 142.2],
                'bounds': [258.625,
                           302.5,
                           346.375,
                           390.125,
                           433.875,
                           477.625,
                           521.375,
                           565.25,
                           609.125,
                           652.875,
                           696.625,
                           740.375,
                           786]}}

def period(data):
 # Use the same project start as the HAZOP study, including its document override.
 from sasisopa18 import resolve
 value=resolve(data,'documento.fecha_inicio_estudio','II')
 if not value:return []
 try:start=datetime.strptime(value,'%d/%m/%Y')
 except ValueError:raise ValueError('Inicio del proyecto: usa una fecha válida dd/mm/aaaa.') from None
 result=[]
 for offset in range(12):
  year,month=divmod(start.year*12+start.month-1+offset,12)
  if year>9999:raise ValueError('El período de los calendarios excede el año 9999.')
  result.append((year,month+1))
 return result

def enabled(data,doc_id):return bool(period(data)) and any(d==doc_id for d,p in REGIONS)

def apply(page,doc_id,index,data,write,fonts):
 spec=REGIONS.get((doc_id,index));months=period(data) if spec else []
 if not months:return []
 from sasisopa18 import _ink_metrics,_line_width
 # Raster labels are removed as pixels, vector labels as text; table rules remain.
 for cell in spec['months']:
  page.add_redact_annot(cell.get('erase',cell['rect']),fill=NAVY if spec.get('raster') else None,cross_out=False)
 if spec.get('year_range'):page.add_redact_annot(spec['year_range'],fill=None,cross_out=False)
 if spec.get('year_band'):page.add_redact_annot(spec['year_band'],fill=NAVY,cross_out=False)
 page.apply_redactions(images=2 if spec.get('raster') else 0,graphics=0,text=0)
 color=(1,1,1) if spec.get('raster') else (0,0,0)
 for cell,(year,month) in zip(spec['months'],months):
  rect=fitz.Rect(cell['rect']);text=MONTHS[month-1];text=text[0] if spec['format']=='initial' else text
  size=spec['size'];font,buffer,alias=fonts.get('ArialMT',text);page.insert_font(fontname=alias,fontbuffer=buffer)
  if spec['format']=='vertical':
   top,bottom=_ink_metrics(font,text);width,left=_line_width(font,text,size)
   origin=((rect.x0+rect.x1)/2+(top+bottom)*size/2,(rect.y0+rect.y1)/2+left+width/2)
   page.insert_text(origin,text,fontsize=size,fontname=alias,rotate=90,color=color)
  else:
   # Use the existing writer for exact ink centering and source-sized letters.
   if spec.get('raster'):
    # The writer defaults to black; draw these source-blue header labels in white.
    top,bottom=_ink_metrics(font,text);width,left=_line_width(font,text,size)
    x=(rect.x0+rect.x1-width)/2-left;y=(rect.y0+rect.y1+(top+bottom)*size)/2
    page.insert_text((x,y),text,fontsize=size,fontname=alias,color=color)
   else:write(page,{'rect':list(rect),'size':size,'min_size':size,'align':1,'font':'ArialMT'},text,fonts)
 if spec.get('year_range'):
  text=str(months[0][0]) if months[0][0]==months[-1][0] else str(months[0][0])+'-'+str(months[-1][0])
  write(page,{'rect':spec['year_range'],'size':8.04,'min_size':8.04,'align':1,'font':'ArialMT'},text,fonts)
 if spec.get('year_band'):
  r=fitz.Rect(spec['year_band']);bounds=spec['bounds'];start=0
  while start<12:
   end=start+1
   while end<12 and months[end][0]==months[start][0]:end+=1
   text=str(months[start][0]);size=spec['size'];font,buffer,alias=fonts.get('ArialMT',text);page.insert_font(fontname=alias,fontbuffer=buffer)
   top,bottom=_ink_metrics(font,text);width,left=_line_width(font,text,size)
   page.insert_text(((bounds[start]+bounds[end]-width)/2-left,(r.y0+r.y1+(top+bottom)*size)/2),text,fontsize=size,fontname=alias,color=color)
   if end<12:page.draw_line((bounds[end],r.y0),(bounds[end],r.y1),color=(0,0,0),width=.3)
   start=end
 return [{'field':'calendario.meses','months':[f'{year:04d}-{month:02d}' for year,month in months],'start_source':'documento.fecha_inicio_estudio'}]
