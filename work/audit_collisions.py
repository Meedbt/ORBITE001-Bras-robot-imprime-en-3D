import json
import build_arm as a
a.build();a.hardware();a.cleanup_shell_clearance()
f=a.frames();lookup={p['id']:p for p in a.PARTS};items=[]
for r in a.SCENE:
    p=lookup[r['part']];items.append((p['id'],p['groupe'],p['s'].tf(f[r['owner']]@r['local']).m))
for r in a.SERVO_SCENE:items.append((r['id'],'servo',r['shape'].tf(f[r['owner']]@r['local']).m))
for name,label,color,s in a.electronics_references():items.append((name,'electronics_reference',s.tf(f['base']).m))
issues=[]
for i,(n,k,s) in enumerate(items):
    for n2,k2,s2 in items[i+1:]:
        if n.startswith('C') and n2.startswith('C') and n[1:3]==n2[1:3]:continue
        v=(s^s2).volume()
        if v>.5:issues.append({'a':n,'b':n2,'volume_mm3':round(v,2),'types':[k,k2]})
issues.sort(key=lambda r:-r['volume_mm3'])
(a.OUT/'interferences_pose_initiale.json').write_text(json.dumps(issues,indent=2),encoding='utf-8')
print(json.dumps(issues))
