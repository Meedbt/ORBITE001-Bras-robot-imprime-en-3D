from pathlib import Path
import sys,json,zipfile,xml.etree.ElementTree as ET,csv,shutil
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work'/'cad-deps'))
import numpy as np,trimesh
OUT=ROOT
parts=json.loads((OUT/'nomenclature_pieces.json').read_text(encoding='utf-8'))

# Portable 3MF with two fit gauges, not a printer preset or a sliced job.
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
model=ET.Element('{'+NS+'}model',{'unit':'millimeter','xml:lang':'fr-FR'})
ET.SubElement(model,'{'+NS+'}metadata',{'name':'Title'}).text='ORBITE V0.2 — gabarits de départ'
ET.SubElement(model,'{'+NS+'}metadata',{'name':'Description'}).text='Deux gabarits à jeu de 0,35 mm par côté. Géométrie uniquement ; sélectionner A1 mini, buse et filament dans Bambu Studio.'
resources=ET.SubElement(model,'{'+NS+'}resources');build=ET.SubElement(model,'{'+NS+'}build')
gauge_ids=['G_MG996R_jeu_0p35','G_MG90S_jeu_0p35']
for oid,(ident,x) in enumerate(zip(gauge_ids,[25,106]),1):
    mm=trimesh.load(OUT/'stl'/'gabarits'/(ident+'.stl'),force='mesh')
    ob=ET.SubElement(resources,'{'+NS+'}object',{'id':str(oid),'type':'model','name':ident})
    mesh=ET.SubElement(ob,'{'+NS+'}mesh');vs=ET.SubElement(mesh,'{'+NS+'}vertices');ts=ET.SubElement(mesh,'{'+NS+'}triangles')
    for v in mm.vertices:ET.SubElement(vs,'{'+NS+'}vertex',dict(zip(['x','y','z'],[f'{n:.6f}' for n in v])))
    for tri in mm.faces:ET.SubElement(ts,'{'+NS+'}triangle',dict(zip(['v1','v2','v3'],[str(n) for n in tri])))
    ET.SubElement(build,'{'+NS+'}item',{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {x} 75 0'})
with zipfile.ZipFile(OUT/'gabarits_depart_A1_mini.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))

# Colored assembled model for general 3D software. Hardware shown as references.
data=json.loads((ROOT/'work'/'scene.json').read_text(encoding='utf-8'))
sys.path.insert(0,str(ROOT/'work'));import build_arm as a
ff=a.frames();scene=trimesh.Scene();colors={'white':[230,232,230,255],'dark':[32,40,38,255],'servo':[76,85,81,255],'metal':[166,182,174,255],'pcb':[27,117,154,255],'zone':[202,160,106,140]}
for r in data:
    mm=trimesh.Trimesh(vertices=np.array(r['positions']).reshape(-1,3),faces=np.array(r['indices']).reshape(-1,3),process=True)
    mm.visual.vertex_colors=np.tile(colors[r['color']],(len(mm.vertices),1))
    scene.add_geometry(mm,node_name=r['id'],geom_name=r['id'],transform=ff[r['owner']]@np.array(r['matrix']).reshape(4,4))
scene.export(OUT/'assemblage_visuel.glb')

# Human-readable CSV for a workshop inventory.
with (OUT/'liste_pieces.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['Identifiant','Désignation','Groupe','Couleur indicative','X impression mm','Y impression mm','Z impression mm','Volume matière pleine cm3'])
    for p in parts:w.writerow([p['id'],p['designation'],p['groupe'],p['couleur'],*p['dimensions_impression_mm'],p['volume_cm3']])

# Re-open every distributed individual STL after binary export.
checks=[]
for p in parts:
    fn=OUT/'stl'/p['groupe']/(p['id']+'.stl');mm=trimesh.load(fn,force='mesh')
    ok=mm.is_watertight and mm.volume>0 and max(mm.extents)<175
    checks.append({'piece':p['id'],'ferme_apres_relecture_STL':bool(mm.is_watertight),'volume_positif':bool(mm.volume>0),'dimensions_mm':np.round(mm.extents,3).tolist(),'compatible_volume_180_mm':bool(max(mm.extents)<175),'ok':bool(ok)})
bad=[r for r in checks if not r['ok']]
report={'statut':'PROTOTYPE NON VALIDE SUR MATERIEL','nombre_STL_individuels':len(checks),'anomalies':bad,'simplification_geometrique_mm':.005,'interferences_volumiques_pose_initiale_superieures_a_0p5_mm3':json.loads((OUT/'interferences_pose_initiale.json').read_text()),'plages_de_mouvement':'NON VALIDEES','validation_charge':'NON REALISEE SUR MATERIEL','pieces':checks}
(OUT/'verification_export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(OUT/'gabarits_depart_A1_mini.3mf') as z:
    ET.fromstring(z.read('3D/3dmodel.model'));assert z.testzip() is None
assert len(trimesh.load(OUT/'assemblage_visuel.glb',force='scene').geometry)==len(data)
assert not bad,bad
print(json.dumps({'STL_valides':len(checks),'max_dimension_mm':round(max(max(r['dimensions_mm']) for r in checks),2),'masse_PLA_pleine_g_hors_gabarits':round(sum(p['masse_pleine_PLA_g'] for p in parts if p['groupe']!='gabarits'),1),'dimensions_assemblage_mm':scene.extents.round(1).tolist(),'objets_GLB':len(scene.geometry),'3MF_objets':2}))

