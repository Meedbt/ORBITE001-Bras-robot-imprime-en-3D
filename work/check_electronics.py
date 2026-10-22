import json
import build_arm as a
case=a.electronics_case();tray=a.electronics_tray();panel=a.electronics_panel().tf(a.PANEL)
refs=a.electronics_references()
mobile=a.union(tray,*[r[3] for r in refs if r[0]!='E04_fiche_USB'])
extraction=[]
for dz in [0,-1,-3,-5,-10,-20,-30,-40,-55]:
    volume=(case.m^mobile.move((0,0,dz)).m).volume()
    extraction.append({'descente_fond_mm':abs(dz),'intersection_boitier_mm3':round(volume,5)})
panel_path=[]
for distance in [0,1,3,5,10,20]:
    s=a.electronics_panel().move((0,-distance,0)).tf(a.PANEL)
    volume=(case.m^s.m).volume()
    panel_path.append({'retrait_platine_mm':distance,'intersection_boitier_mm3':round(volume,5)})
wire_probe=a.box((12,7,10),(-40,-18,1))
wire_obstruction=(a.union(case,a.base_fixed()).m^wire_probe.m).volume()
usb_path=[]
usb=[r[3] for r in refs if r[0]=='E04_fiche_USB'][0]
for distance in [0,2,5,10,20]:
    volume=(case.m^usb.move((0,-distance,0)).m).volume()
    usb_path.append({'retrait_fiche_mm':distance,'intersection_boitier_mm3':round(volume,5)})
report={'revision':'0.2','limites':'Vérification géométrique sur enveloppes nominales simplifiées, sans fils, vis ni tolérances d’impression. Fond retiré après débranchement USB et libération des câbles. Échantillonnage discret des déplacements, pas une validation physique.','extraction_fond':extraction,'retrait_platine':panel_path,'retrait_USB':usb_path,'obstruction_passage_vertical_mm3':round(wire_obstruction,5)}
bad=[r for r in extraction+panel_path+usb_path if r['intersection_boitier_mm3']>.5]
report['anomalies']=bad
(a.OUT/'verification_socle_electronique.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert not bad and wire_obstruction<.5,report
print(json.dumps({'extraction_fond_points':len(extraction),'retrait_platine_points':len(panel_path),'retrait_USB_points':len(usb_path),'anomalies':bad,'passage_cables_libre':wire_obstruction<.5}))
